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
import saliency
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file


parser = argparse.ArgumentParser()
parser.add_argument('--dirr', type=str, default='trial', help='output directory')
parser.add_argument('--classes', type=int, default=2, help='number of classes to predict')
parser.add_argument('--pdmd', type=str, default='tumor', help='feature to predict')
parser.add_argument('--imgfile',type=str, default=None,
                    help='load the image (eg. CCRCC/C3L-SSSSS-SS,CCRCC/C3L-SSSSS-SS)')
parser.add_argument('--modeltoload', type=str, default='', help='reload trained model')
parser.add_argument('--metadir', type=str, default='', help='reload trained model')
opt = parser.parse_args()

dirr = opt.dirr
classes = opt.classes
pdmd = opt.pdmd
imgfile = opt.imgfile
modeltoload = opt.modeltoload
metadir = opt.metadir


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
    try:
        os.mkdir('../Results/'+dirr)
    except FileExistsError:
        pass
    try:
        os.mkdir('../Results/'+dirr+'/saliency')
    except FileExistsError:
        pass
    if not os.path.isfile('../Results/' + dirr + '/level1/dict.csv'):
        tumor = imgfile.split('/')[0]
        slideID = imgfile.split("-")[-1]
        patientID = imgfile.rsplit("-", 1)[0].split('/')[-1]
        os.symlink("../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level1', '../Results/'+dirr + '/level1',
                   target_is_directory=True)
    tiles = pd.read_csv('../Results/' + dirr + '/level1/dict.csv')

    # saver = tf.train.import_meta_graph('../Results/'+dirr+'/dropout_0.5.meta')
    # print(sess.run('logits/logits/weights:0'))
    # print_tensors_in_checkpoint_file(file_name='../Results/'+dirr+'/dropout_0.5', tensor_name='',
    #                                  all_tensors=False, all_tensor_names=False)
    graph = tf.Graph()
    with graph.as_default():
        # image input
        xa_in = tf.placeholder(tf.float32, name="xa")
        xa_in_reshape = tf.reshape(xa_in, [-1, 299, 299, 3])
        # xb_in = tf.placeholder(tf.float32, name="xb")
        # xb_in_reshape = tf.reshape(xb_in, [-1, 299, 299, 3])
        # xc_in = tf.placeholder(tf.float32, name="xc")
        # xc_in_reshape = tf.reshape(xc_in, [-1, 299, 299, 3])

        logits, nett = inference(xa_in_reshape, xa_in_reshape, xa_in_reshape, classes)
        pred = tf.nn.softmax(logits, name="prediction")
        neuron_selector = tf.placeholder(tf.int32)
        y = logits[0][neuron_selector]

        with tf.Session(graph=graph,
                        config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)) as sess:
            tf.global_variables_initializer().run()
            saver = tf.train.import_meta_graph('../Results/'+metadir+'/'+modeltoload+'.meta')
            saver.restore(sess, '../Results/'+metadir+'/'+modeltoload)
            finalls = []
            for idx, row in tiles.iterrows():
                if os.path.isfile('../Results/'+dirr+'/saliency/SGIG_'+row['Loc'].split("/")[-1]):
                    finalls.append([row['Num'], row['X_pos'], row['Y_pos'], row['X'],
                                    row['Y'], '../Results/' + dirr + '/saliency/SGIG_' + row['Loc'].split("/")[-1]])
                else:
                    img = cv2.imread(row['Loc'])
                    img = img.astype(np.float32)
                    baseline = np.zeros(img.shape)
                    baseline.fill(255)

                    grad = saliency.IntegratedGradients(graph, sess, y, xa_in_reshape)
                    smoothgrad_mask_3d = grad.GetSmoothedMask(img, feed_dict={
                        neuron_selector: 1}, x_steps=5, x_baseline=baseline)
                    smoothgrad_mask_grayscale = saliency.VisualizeImageGrayscale(smoothgrad_mask_3d)
                    smoothgrad_mask_grayscale = im2double(smoothgrad_mask_grayscale)
                    smoothgrad_mask_grayscale = py_map2jpg(smoothgrad_mask_grayscale)
                    sa = im2double(img) * 255
                    sb = im2double(smoothgrad_mask_grayscale) * 255
                    scurHeatMap = sa * 0.5 + sb * 0.5
                    sab = np.hstack((sa, sb))
                    sfull = np.hstack((scurHeatMap, sab))
                    cv2.imwrite('../Results/'+dirr+'/saliency/SGIG_'+row['Loc'].split("/")[-1], sfull)
                    finalls.append([row['Num'], row['X_pos'], row['Y_pos'], row['X'],
                                    row['Y'], '../Results/'+dirr+'/saliency/SGIG_'+row['Loc'].split("/")[-1]])

    joined_dict = pd.DataFrame(finalls, columns=['Num', 'X_pos', 'Y_pos', 'X', 'Y', 'path'])
    joined_dict.to_csv('../Results/'+dirr+'/saliency.csv', index=False)

    ### slide level ###
    slideref = pd.read_csv('../imglowres.csv')
    slideref = slideref[(slideref['SlideID'] == imgfile.split('/')[1].split('.sv')[0])]

    n_x = int(slideref["n_x"].tolist()[0])
    n_y = int(slideref["n_y"].tolist()[0])

    lowres = cv2.imread('../lowres/'+imgfile.split('/')[1].split('.sv')[0]+'.png')
    raw_img = np.array(lowres)[:, :, :3]

    optimg = np.full((n_x, n_y), 0)
    for index, row in joined_dict.iterrows():
        optimg[int(row["X_pos"]), int(row["Y_pos"])] = 255

    # expand 5 times
    optimg = optimg.repeat(50, axis=0).repeat(50, axis=1)

    # small-scaled original image
    ori_img = cv2.resize(raw_img, (np.shape(optimg)[0], np.shape(optimg)[1]))
    ori_img = ori_img[:np.shape(optimg)[1], :np.shape(optimg)[0], :3]
    cv2.imwrite('../Results/' + dirr + '/Original_scaled.png', ori_img)

    # binary output image
    topt = np.transpose(optimg)
    optimg = np.full((np.shape(topt)[0], np.shape(topt)[1], 3), 0)
    optimg[:, :, 0] = topt
    optimg[:, :, 1] = topt
    optimg[:, :, 2] = topt
    cv2.imwrite('../Results/' + dirr + '/Mask.png', optimg * 255)

    fac = 50
    canvas = np.full((np.shape(optimg)[0], np.shape(optimg)[1], 3), 0)
    for idx, row in joined_dict.iterrows():
        imm = cv2.imread(row['path'])[0:250, 0:250, :]
        imm = cv2.resize(imm, (fac, fac))
        canvas[int(row["Y_pos"])*fac:int(row["Y_pos"])*fac+fac,
        int(row["X_pos"])*fac:int(row["X_pos"])*fac+fac, :] = imm
    cv2.imwrite('../Results/' + dirr + '/Saliency.png', canvas)
    # superimpose on scaled original image
    overlayhm = ori_img * 0.5 + canvas * 0.5
    cv2.imwrite('../Results/' + dirr + '/Saliency_Overlay.png', overlayhm)

