"""
Outputing CAM of tiles

Created on 04/21/2020

@author: RH

"""
import os
import numpy as np
import cv2
import tensorflow as tf
import saliency.tf1 as saliency
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file


# format activation and weight to get heatmap
def py_returnCAMmap(activation, weights_LR):
    n_feat, w, h, n = activation.shape
    act_vec = np.reshape(activation, [n_feat, w*h])
    n_top = weights_LR.shape[0]
    out = np.zeros([w, h, n_top])

    for t in range(n_top):
        weights_vec = np.reshape(weights_LR[t], [1, weights_LR[t].shape[0]])
        heatmap_vec = np.dot(weights_vec,act_vec)
        heatmap = np.reshape(np.squeeze(heatmap_vec), [w, h])
        out[:, :, t] = heatmap
    return out


# image to double
def im2double(im):
    return cv2.normalize(im.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)


# image to jpg
def py_map2jpg(imgmap):
    heatmap_x = np.round(imgmap*255).astype(np.uint8)
    return cv2.applyColorMap(heatmap_x, cv2.COLORMAP_JET)


def inference(images, num_classes, for_training=False, restore_logits=True,
              scope=None):
  # Set weight_decay for weights in Conv and FC layers.
  with slim.arg_scope([slim.ops.conv2d, slim.ops.fc], weight_decay=0.00004):
    with slim.arg_scope([slim.ops.conv2d],
                        stddev=0.1,
                        activation=tf.nn.relu,
                        batch_norm_params={'decay': 0.9997, 'epsilon': 0.001}):
      logits, endpoints, net2048, sel_endpoints, netts = slim.inception.inception_v3(
          images,
          dropout_keep_prob=0.8,
          num_classes=num_classes,
          is_training=for_training,
          restore_logits=restore_logits,
          scope=scope)

  # Grab the logits associated with the side head. Employed during training.
  auxiliary_logits = endpoints['aux_logits']

  #return logits, auxiliary_logits
  return logits, auxiliary_logits, endpoints, net2048, sel_endpoints, netts


if __name__ == "__main__":
    # saver = tf.train.import_meta_graph('../model/model.ckpt-31500.meta')

    # print(sess.run('logits/logits/weights:0'))
    # print_tensors_in_checkpoint_file(file_name='../model/model.ckpt-31500', tensor_name='',
    #                                  all_tensors=False, all_tensor_names=False)
    graph = tf.Graph()
    with graph.as_default():
        # image input
        x_in = tf.placeholder(tf.float32, name="x")
        x_in_reshape = tf.reshape(x_in, [-1, 299, 299, 3])
        logits, _, _, _, _, nett = inference(x_in_reshape, 2)
        pred = tf.nn.softmax(logits, name="prediction")
        # prediction = tf.argmax(logits, 1)
        neuron_selector = tf.placeholder(tf.int32)
        y = logits[0][neuron_selector]

        with tf.Session(graph=graph,
                        config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=True)) as sess:
            tf.global_variables_initializer().run()
            saver = tf.train.import_meta_graph('../tiles_for_saliency/model.ckpt-99000.meta')
            saver.restore(sess, '../tiles_for_saliency/model.ckpt-99000')
            for dirr in ['top_200_NYU', 'top_200_TCGA',
                         'bottom_200_NYU', 'bottom_200_TCGA']:
                dirpath = str("../tiles_for_saliency/Results/"+dirr)
                try:
                    os.mkdir(dirpath)
                except FileExistsError:
                    pass
                for aa in os.listdir(str("../tiles_for_saliency/"+dirr)):
                    if 'jpeg' in aa and aa not in os.listdir(str("../tiles_for_saliency/Results/"+dirr)):
                        img = cv2.imread(str("../tiles_for_saliency/"+dirr + '/' + aa))
                        img = img.astype(np.float32)
                        # prediction_class = sess.run(
                        #     [prediction], {x_in: img})[0]
                        # weight = sess.run('logits/logits/weights:0')
                        grad = saliency.IntegratedGradients(graph, sess, y, x_in_reshape)
                        # Baseline is a white image.
                        baseline = np.zeros(img.shape)
                        baseline.fill(255)

                        # vanilla_mask_3d = grad.GetMask(img, feed_dict={neuron_selector: 1},
                        #                                x_stepIntegratedGradientss=25, x_baseline=baseline)
                        smoothgrad_mask_3d = grad.GetSmoothedMask(img, feed_dict={
                            neuron_selector: 1}, x_steps=5, x_baseline=baseline, batch_size=1)

                        # Call the visualization methods to convert the 3D tensors to 2D grayscale.
                        # vanilla_mask_grayscale = saliency.VisualizeImageGrayscale(vanilla_mask_3d)
                        smoothgrad_mask_grayscale = saliency.VisualizeImageGrayscale(smoothgrad_mask_3d)

                        print(aa)
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
                        cv2.imwrite(str(dirpath + '/' + aa), sfull)

    # print(np.shape(x_))
    # print(np.shape(nett_))
    # print(np.shape(pred_))
    # print(np.shape(weight))



