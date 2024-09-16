from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
from io import BytesIO
import tensorflow as tf
import numpy as np
import cv2
from imageio import imread
import os
import tempfile

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class DMT(object):
    def __init__(self):
        self.pb = 'dmt.pb'
        self.style_dim = 8

    def preprocess(self, img):
        return (img / 255. - 0.5) * 2

    def deprocess(self, img):
        return (img + 1) / 2

    def load_image(self, path):
        img = cv2.resize(imread(path), (256, 256))  
        img_ = np.expand_dims(self.preprocess(img), 0)
        return img / 255., img_

    def load_model(self):
        with tf.Graph().as_default():
            output_graph_def = tf.compat.v1.GraphDef()

            with open(self.pb, 'rb') as fr:
                output_graph_def.ParseFromString(fr.read())
                tf.import_graph_def(output_graph_def, name='')

            self.sess = tf.compat.v1.Session()
            self.sess.run(tf.compat.v1.global_variables_initializer())
            graph = tf.compat.v1.get_default_graph()
            self.X = graph.get_tensor_by_name('X:0')
            self.Y = graph.get_tensor_by_name('Y:0')
            self.S = graph.get_tensor_by_name('S:0')
            self.X_content = graph.get_tensor_by_name('content_encoder/content_code:0')
            self.X_style = graph.get_tensor_by_name('style_encoder/style_code:0')
            self.Xs = graph.get_tensor_by_name('decoder_1/g:0')
            self.Xf = graph.get_tensor_by_name('decoder_2/g:0')

    def pairwise(self, A, B):
        A_img, A_img_ = self.load_image(A)
        B_img, B_img_ = self.load_image(B)
        Xs_ = self.sess.run(self.Xs, feed_dict={self.X: A_img_, self.Y: B_img_})

        processed_img = self.deprocess(Xs_)[0]
        processed_img = (processed_img * 255).astype(np.uint8)
        processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB) 
        return processed_img

neural_network = DMT()

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_type, _ = cgi.parse_header(self.headers['Content-Type'])
        if content_type == 'multipart/form-data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            form = cgi.FieldStorage(
                BytesIO(post_data),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            with tempfile.NamedTemporaryFile(delete=False) as f1:
                f1.write(form['image1'].file.read())
                image1_path = f1.name
            with tempfile.NamedTemporaryFile(delete=False) as f2:
                f2.write(form['image2'].file.read())
                image2_path = f2.name

            print("Received images successfully.")

            result_image = neural_network.pairwise(image1_path, image2_path)

            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            _, buffer = cv2.imencode('.jpg', result_image)
            self.wfile.write(buffer.tobytes())  
            print("Sent processed image successfully.")
            os.unlink(image1_path)
            os.unlink(image2_path)

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    neural_network.load_model()  
    run()
