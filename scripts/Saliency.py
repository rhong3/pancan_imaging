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
    saver = tf.train.import_meta_graph('../Results/'+dirr+'/dropout_0.5.meta')

    # print(sess.run('logits/logits/weights:0'))
    print_tensors_in_checkpoint_file(file_name='../Results/'+dirr+'/dropout_0.5', tensor_name='',
                                     all_tensors=False, all_tensor_names=False)
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
            saver = tf.train.import_meta_graph('../Results/'+dirr+'/dropout_0.5.meta')
            saver.restore(sess, '../Results/'+dirr+'/dropout_0.5')
            dirpath = str('../Results/'+dirr+'/saliency/')
            try:
                os.mkdir(dirpath)
            except FileExistsError:
                pass
            test_tiles = pd.read_csv('../Results/'+dirr+'/out/Test_tile.csv')
            for idx, row in test_tiles.iterrows():
                print(row['Slide_ID'])
                try:
                    os.mkdir(dirpath + str(row['Slide_ID']))
                except FileExistsError:
                    pass
                img = cv2.imread(row['L1path'])
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
                cv2.imwrite(str(dirpath+str(row["Slide_ID"])+"/SGIG"+row['L1path'].split("/")[-1]), sfull)

                # conv_tensor = graph.get_tensor_by_name('Panoptes1/conv2d_130/kernel:0')
                # grad_cam = saliency.GradCam(graph, sess, y, xa_in_reshape, conv_tensor)
                # smoothgrad_grad_cam_mask_3d = grad_cam.GetSmoothedMask(img, feed_dict={neuron_selector: 1})
                # smoothgrad_grad_cam_mask_grayscale = saliency.VisualizeImageGrayscale(smoothgrad_grad_cam_mask_3d)
                # smoothgrad_grad_cam_mask_grayscale = im2double(smoothgrad_grad_cam_mask_grayscale)
                # smoothgrad_grad_cam_mask_grayscale = py_map2jpg(smoothgrad_grad_cam_mask_grayscale)
                # sa = im2double(img) * 255
                # sb = im2double(smoothgrad_grad_cam_mask_grayscale) * 255
                # scurHeatMap = sa * 0.5 + sb * 0.5
                # sab = np.hstack((sa, sb))
                # sfull = np.hstack((scurHeatMap, sab))
                # cv2.imwrite(str(dirpath + str(row["Slide_ID"]) + "/gradCAM" + row['L1path'].split("/")[-1]), sfull)


# if not os.path.isfile(data_dir + '/level3/dict.csv'):
#     tumor = imgfile.split('/')[0]
#     slideID = imgfile.split("-")[-1]
#     patientID = imgfile.rsplit("-", 1)[0].split('/')[-1]
#     os.symlink("../../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level1', data_dir + '/level1',
#                target_is_directory=True)
#     os.symlink("../../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level2', data_dir + '/level2',
#                target_is_directory=True)
#     os.symlink("../../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level3', data_dir + '/level3',
#                target_is_directory=True)
# ### Heatmap ###
# slist = pd.read_csv(data_dir + '/te_sample.csv', header=0)
# # load dictionary of predictions on tiles
# teresult = pd.read_csv(out_dir+'/Test.csv', header=0)
# # join 2 dictionaries
# joined = pd.merge(slist, teresult, how='inner', on=['Num'])
# joined = joined.drop(columns=['Num'])
# joined['L1img'] = joined['L1path'].str.rsplit('/', 1, expand=True)[1]
# tile_dict = pd.read_csv(data_dir+'/level1/dict.csv', header=0)
# tile_dict['L1img'] = tile_dict['Loc'].str.rsplit('/', 1, expand=True)[1]
# joined_dict = pd.merge(joined, tile_dict, how='inner', on=['L1img'])
# logits = joined_dict[pos_score]
# prd_ls = np.asmatrix(logits).argmax(axis=1).astype('uint8')
# prd = int(np.round(np.mean(prd_ls)))
# print(str(pos_ls[prd])+'!')
# print("Prediction score = " + str(round(logits.iloc[:, prd].mean(), 5)))
#
# joined_dict['predict_index'] = prd_ls
# # save joined dictionary
# joined_dict.to_csv(out_dir + '/finaldict.csv', index=False)
#
# # output heat map of pos and neg.
# # initialize a graph and for each RGB channel
# opt = np.full((n_x, n_y), 0)
# hm_R = np.full((n_x, n_y), 0)
# hm_G = np.full((n_x, n_y), 0)
# hm_B = np.full((n_x, n_y), 0)
#
# if cls == 2:
#     for index, row in joined_dict.iterrows():
#         opt[int(row["X_pos"]), int(row["Y_pos"])] = 255
#         if row['POS_score'] >= 0.5:
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 255
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = int((1 - (row['POS_score'] - 0.5) * 2) * 255)
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = int((1 - (row['POS_score'] - 0.5) * 2) * 255)
#         else:
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 255
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = int((1 - (row["NEG_score"] - 0.5) * 2) * 255)
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = int((1 - (row["NEG_score"] - 0.5) * 2) * 255)
# else:
#     # Positive is labeled red in output heat map
#     for index, row in joined_dict.iterrows():
#         opt[int(row["X_pos"]), int(row["Y_pos"])] = 255
#         if row['predict_index'] == 0:
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 55
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 126
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 184
#         elif row['predict_index'] == 1:
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 228
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 26
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 28
#         elif row['predict_index'] == 2:
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 77
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 175
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 74
#         elif row['predict_index'] == 3:
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 255
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 255
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 51
#         elif row['predict_index'] == 4:
#             hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 191
#             hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 64
#             hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 191
#         else:
#             pass
# # expand 5 times
# opt = opt.repeat(50, axis=0).repeat(50, axis=1)
#
# # small-scaled original image
# ori_img = cv2.resize(raw_img, (np.shape(opt)[0], np.shape(opt)[1]))
# ori_img = ori_img[:np.shape(opt)[1], :np.shape(opt)[0], :3]
# cv2.imwrite(out_dir + '/Original_scaled.png', ori_img)
#
# # binary output image
# topt = np.transpose(opt)
# opt = np.full((np.shape(topt)[0], np.shape(topt)[1], 3), 0)
# opt[:, :, 0] = topt
# opt[:, :, 1] = topt
# opt[:, :, 2] = topt
# cv2.imwrite(out_dir + '/Mask.png', opt * 255)
#
# # output heatmap
# hm_R = np.transpose(hm_R)
# hm_G = np.transpose(hm_G)
# hm_B = np.transpose(hm_B)
# hm_R = hm_R.repeat(50, axis=0).repeat(50, axis=1)
# hm_G = hm_G.repeat(50, axis=0).repeat(50, axis=1)
# hm_B = hm_B.repeat(50, axis=0).repeat(50, axis=1)
# hm = np.dstack([hm_B, hm_G, hm_R])
# cv2.imwrite(out_dir + '/HM.png', hm)
#
# # superimpose heatmap on scaled original image
# overlay = ori_img * 0.5 + hm * 0.5
# cv2.imwrite(out_dir + '/Overlay.png', overlay)
#
# ### CAM ###
# for pre in ['ol', 'hm']:
#     fac = 50
#     campath = pre+'l1path'
#     canvas = np.full((np.shape(opt)[0], np.shape(opt)[1], 3), 0)
#     for idx, row in joined_dict.iterrows():
#         imm = cv2.imread(row[campath])[0:250, 0:250, :]
#         imm = cv2.resize(imm, (fac, fac))
#         canvas[int(row["Y_pos"])*fac:int(row["Y_pos"])*fac+fac,
#         int(row["X_pos"])*fac:int(row["X_pos"])*fac+fac, :] = imm
#     cv2.imwrite(out_dir + '/' + pre + '_CAM.png', canvas)
#     if pre == 'hm':
#         # superimpose heatmap on scaled original image
#         overlayhm = ori_img * 0.5 + canvas * 0.5
#         cv2.imwrite(out_dir + '/cam_Overlay.png', overlayhm)
#
