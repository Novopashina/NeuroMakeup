from flask import Flask, request, send_file
from io import BytesIO
import tensorflow as tf
import numpy as np
import cv2
from imageio import imread, imsave
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = Flask(__name__)

class NeuralNetwork:
    def __init__(self):
        self.pb = 'dmt.pb'
        self.load_model()

    def preprocess(self, img):
        return (img / 255. - 0.5) * 2

    def deprocess(self, img):
        return (img + 1) / 2

    def load_image(self, img):
        img_ = cv2.resize(img, (256, 256))
        img_ = np.expand_dims(self.preprocess(img_), 0)
        return img_

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

    def process_images(self, img1, img2):
        A_img_ = self.load_image(img1)
        B_img_ = self.load_image(img2)
        Xs_ = self.sess.run(self.Xs, feed_dict={self.X: A_img_, self.Y: B_img_})
        return self.deprocess(Xs_)[0]

neural_network = NeuralNetwork()

@app.route('/process_images', methods=['POST'])
def process_images():
    # Получаем два изображения из POST-запроса
    image1 = request.files['image1']
    image2 = request.files['image2']

    # Преобразуем изображения в байтовые массивы
    image1_bytes = image1.read()
    image2_bytes = image2.read()

    # Обрабатываем изображения с помощью нейросети
    result_image_bytes = neural_network.process_images(image1_bytes, image2_bytes)

    # Создаем файловый объект для отправки результата обратно клиенту
    result_file = BytesIO(result_image_bytes)

    # Отправляем файл обратно клиенту
    return send_file(result_file, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
