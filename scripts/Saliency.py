"""
Outputing CAM of tiles

Created on 04/21/2020

@author: RH

"""
import argparse
import os
import numpy as np
import cv2
import pandas as pd
import tensorflow as tf
import Panoptes1
import saliency.tf1 as saliency
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file


parser = argparse.ArgumentParser()
parser.add_argument('--dirr', type=str, default='trial', help='output directory')
parser.add_argument('--classes', type=int, default=2, help='number of classes to predict')
parser.add_argument('--pdmd', type=str, default='tumor', help='feature to predict')
opt = parser.parse_args()

dirr = opt.dirr
classes = opt.classes
pdmd = opt.pdmd

# image to double
def im2double(im):
    return cv2.normalize(im.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)


# image to jpg
def py_map2jpg(imgmap):
    heatmap_x = np.round(imgmap*255).astype(np.uint8)
    return cv2.applyColorMap(heatmap_x, cv2.COLORMAP_JET)


def inference(xa_in_re, xb_in_re, xc_in_re, num_classes):
    logits, nett, ww = Panoptes1.Panoptes1(xa_in_re, xb_in_re, xc_in_re,
                                           num_cls=num_classes,
                                           is_train=False,
                                           dropout=0.5,
                                           scope='Panoptes1')
    return logits, nett


if __name__ == "__main__":
    # saver = tf.train.import_meta_graph('../Results/'+dirr+'/dropout_0.5.meta')

    # print(sess.run('logits/logits/weights:0'))
    # print_tensors_in_checkpoint_file(file_name='../Results/'+dirr+'/dropout_0.5', tensor_name='',
    #                                  all_tensors=False, all_tensor_names=False)
    graph = tf.Graph()
    with graph.as_default():
        # image input
        xa_in = tf.placeholder(tf.float32, name="xa")
        xa_in_reshape = tf.reshape(xa_in, [-1, 299, 299, 3])
        xb_in = tf.placeholder(tf.float32, name="xb")
        xb_in_reshape = tf.reshape(xb_in, [-1, 299, 299, 3])
        xc_in = tf.placeholder(tf.float32, name="xc")
        xc_in_reshape = tf.reshape(xc_in, [-1, 299, 299, 3])

        logits, nett = inference(xa_in_reshape, xb_in_reshape, xc_in_reshape, classes)
        pred = tf.nn.softmax(logits, name="prediction")
        neuron_selector = tf.placeholder(tf.int32)
        y = logits[0][neuron_selector]

        with tf.Session(graph=graph,
                        config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)) as sess:
            tf.global_variables_initializer().run()
            saver = tf.train.import_meta_graph('../Results/'+dirr+'/dropout_0.5.meta')
            saver.restore(sess, '../Results/'+dirr+'/dropout_0.5')
            dirpath = str('../Results/'+dirr+'/saliency/')
            try:
                os.mkdir(dirpath)
            except FileExistsError:
                pass
            test_tiles = pd.read_csv('../Results/'+dirr+'/out/Test_tile.csv')
            for idx, row in test_tiles.iterrows():
                for diiir in [str('../Results/' + dirr + '/saliency/' + str(row['Slide_ID'])),
                              str('../Results/' + dirr + '/saliency/' + str(row['Slide_ID']) + '/level1'),
                              str('../Results/' + dirr + '/saliency/' + str(row['Slide_ID']) + '/level2'),
                              str('../Results/' + dirr + '/saliency/' + str(row['Slide_ID']) + '/level3')]:
                    try:
                        os.mkdir(dirpath)
                    except FileExistsError:
                        pass
                # prediction_class = sess.run(
                #     [prediction], {x_in: img})[0]
                # weight = sess.run('logits/logits/weights:0')

                # Baseline is a white image.
                for paths in ['L1path', 'L2path', 'L3path']:
                    grad = saliency.IntegratedGradients(graph, sess, y, xa_in_reshape)
                    img = cv2.imread(row[paths])
                    img = img.astype(np.float32)
                    baseline = np.zeros(img.shape)
                    baseline.fill(255)
                    # vanilla_mask_3d = grad.GetMask(img, feed_dict={neuron_selector: 1},
                    #                                x_stepIntegratedGradientss=25, x_baseline=baseline)
                    smoothgrad_mask_3d = grad.GetSmoothedMask(img, feed_dict={
                        neuron_selector: int(row["label"])}, x_steps=5, x_baseline=baseline, batch_size=1)

                    # Call the visualization methods to convert the 3D tensors to 2D grayscale.
                    # vanilla_mask_grayscale = saliency.VisualizeImageGrayscale(vanilla_mask_3d)
                    smoothgrad_mask_grayscale = saliency.VisualizeImageGrayscale(smoothgrad_mask_3d)

                    print(row['Slide_ID'])
                    # vanilla_mask_grayscale = im2double(vanilla_mask_grayscale)
                    # vanilla_mask_grayscale = py_map2jpg(vanilla_mask_grayscale)
                    # a = im2double(img) * 255
                    # b = im2double(vanilla_mask_grayscale) * 255
                    # curHeatMap = a * 0.5 + b * 0.5
                    # ab = np.hstack((a, b))
                    # full = np.hstack((curHeatMap, ab))
                    # cv2.imwrite(str(dirpath + '/' + aa), full)

                    smoothgrad_mask_grayscale = im2double(smoothgrad_mask_grayscale)
                    smoothgrad_mask_grayscale = py_map2jpg(smoothgrad_mask_grayscale)
                    sa = im2double(img) * 255
                    sb = im2double(smoothgrad_mask_grayscale) * 255
                    scurHeatMap = sa * 0.5 + sb * 0.5
                    sab = np.hstack((sa, sb))
                    sfull = np.hstack((scurHeatMap, sab))

                    cv2.imwrite(str(dirpath+str(row["Slide_ID"])+"/"+row[paths].split("/", 5)), sfull)

    # print(np.shape(x_))
    # print(np.shape(nett_))
    # print(np.shape(pred_))
    # print(np.shape(weight))



