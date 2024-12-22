# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
from imageio import imread, imsave
import os, glob, cv2

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

no_makeup = os.path.join('faces', 'no_makeup', 'xfsy_0055.png')
makeup_a = os.path.join('faces', 'makeup', 'vFG756.png')
img_size = 256

class DMT(object):
    def __init__(self):
        self.pb = 'dmt.pb'
        self.style_dim = 8

    def preprocess(self, img):
        return (img / 255. - 0.5) * 2

    def deprocess(self, img):
        return (img + 1) / 2

    def load_image(self, path):
        img = cv2.resize(imread(path), (img_size, img_size))
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
        imsave(os.path.join('output', 'processed_img .jpg'), processed_img)
	    

if __name__ == '__main__':
    model = DMT()
    model.load_model()
    model.pairwise(no_makeup, makeup_a)