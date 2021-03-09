"""
Convolutional neural nets driving code for TF2.0

Created on 04/26/2019

@author: RH
"""
from datetime import datetime
import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
import Accessory2 as ac
import Panoptes1


# Define an Inception
class INCEPTION:
    def __init__(self, input_dim, d_hyperparams=None,
                 save_graph_def=True, meta_graph=None, transfer=False,
                 log_dir="./log", meta_dir="./meta", weights=tf.constant([1., 1., 1., 1.])):
        if d_hyperparams is None:
            d_hyperparams = {}
        self.input_dim = input_dim
        self.batch_size = d_hyperparams['batch_size']
        self.dropout = d_hyperparams['dropout']
        self.learning_rate = d_hyperparams['learning_rate']
        self.sesh = tf.Session()
        self.weights = weights
        self.transfer = transfer

        if meta_graph:  # load saved graph
            model_name = os.path.basename(meta_graph)
            tf.train.import_meta_graph(meta_dir + '/' + model_name +'.meta').restore(
                self.sesh, meta_dir + '/' + model_name)
            handles = self.sesh.graph.get_collection("cnn_to_restore")

        else:  # build graph from scratch
            self.datetime = datetime.now().strftime(r"%y%m%d_%H%M")
            handles = self._buildGraph()
            for handle in handles:
                tf.add_to_collection("cnn_to_restore", handle)
            self.sesh.run(tf.global_variables_initializer())

        # unpack handles for tensor ops to feed or fetch for lower layers
        (self.xa_in, self.xb_in, self.xc_in, self.is_train, self.y_in, self.logits,
         self.net, self.w, self.pred, self.pred_loss,
         self.global_step, self.train_op, self.merged_summary, self.tumor) = handles

        # vars = []
        # for mm in ['Panoptes1/loss3/classifier/kernel:0', 'Panoptes1/loss3/classifier/bias:0',
        #           'Panoptes1/loss2/classifier_1/kernel:0', 'Panoptes1/loss2/classifier_1/bias:0',
        #           'Panoptes1/loss2/classifier_2/kernel:0', 'Panoptes1/loss2/classifier_2/bias:0',
        #           'Panoptes1/loss2/classifier/kernel:0', 'Panoptes1/loss2/classifier/bias:0']:
        #     vars.extend(tf.trainable_variables(scope=mm))

        if transfer:
            sample_weights = tf.gather_nd(self.weights,
                                          tf.stack([tf.argmax(self.tumor, axis=1),
                                                    tf.argmax(self.y_in, axis=1)], axis=1))

            self.pred_loss = tf.losses.softmax_cross_entropy(
                onehot_labels=self.y_in, logits=self.logits, weights=sample_weights)
            self.train_op = tf.train.AdamOptimizer(
                learning_rate=self.learning_rate, name='trans_Adam').minimize(
                loss=self.pred_loss, global_step=self.global_step)

            uninitialized_vars = []
            for var in tf.global_variables():
                try:
                    self.sesh.run(var)
                except tf.errors.FailedPreconditionError:
                    uninitialized_vars.append(var)
            self.sesh.run(tf.variables_initializer(uninitialized_vars))

        if save_graph_def:  # tensorboard
            try:
                os.mkdir(log_dir + '/training')
                os.mkdir(log_dir + '/validation')

            except FileExistsError:
                pass

            self.train_logger = tf.summary.FileWriter(log_dir + '/training', self.sesh.graph)
            self.valid_logger = tf.summary.FileWriter(log_dir + '/validation', self.sesh.graph)

    @property
    def step(self):
        return self.global_step.eval(session=self.sesh)

    # build graph; choose a structure defined in model
    def _buildGraph(self):
        # image input
        xa_in = tf.placeholder(tf.float32, name="xa")
        xa_in_reshape = tf.reshape(xa_in, [-1, self.input_dim[1], self.input_dim[2], 3])
        xb_in = tf.placeholder(tf.float32, name="xb")
        xb_in_reshape = tf.reshape(xb_in, [-1, self.input_dim[1], self.input_dim[2], 3])
        xc_in = tf.placeholder(tf.float32, name="xc")
        xc_in_reshape = tf.reshape(xc_in, [-1, self.input_dim[1], self.input_dim[2], 3])
        # dropout
        dropout = self.dropout
        # label input
        y_in = tf.placeholder(dtype=tf.float32, name="y")
        # tumor type input
        tumor = tf.placeholder(dtype=tf.float32, name="t")
        # train or test
        is_train = tf.placeholder_with_default(True, shape=[], name="is_train")
        classes = 20

        # other features input
        logits, nett, ww = Panoptes1.Panoptes1(xa_in_reshape, xb_in_reshape, xc_in_reshape,
                                                   num_cls=classes,
                                                   is_train=is_train,
                                                   dropout=dropout,
                                                   scope='Panoptes1')

        pred = tf.nn.softmax(logits, name="prediction")

        global_step = tf.Variable(0, trainable=False)

        sample_weights = tf.gather_nd(self.weights,
                                      tf.stack([tf.argmax(tumor, axis=1), tf.argmax(y_in, axis=1)], axis=1))

        pred_loss = tf.losses.softmax_cross_entropy(
            onehot_labels=y_in, logits=logits, weights=sample_weights)

        tf.summary.scalar("loss", pred_loss)

        tf.summary.tensor_summary("pred", pred)

        # optimizer based on TensorFlow version
        train_op = tf.train.AdamOptimizer(
        learning_rate=self.learning_rate).minimize(
        loss=pred_loss, global_step=global_step)

        merged_summary = tf.summary.merge_all()

        return (xa_in, xb_in, xc_in, is_train,
                y_in, logits, nett, ww, pred, pred_loss,
                global_step, train_op, merged_summary, tumor)

    # inference using trained models
    def inference(self, X, dirr, testset=None, pmd=None, train_status=False, realtest=False):
        now = datetime.now().isoformat()[11:]
        print("------- Testing begin: {} -------\n".format(now))
        rd = 0
        pdx = []
        yl = []
        if realtest:
            itr, file, ph = X.data(realtest=True, train=False)
            next_element = itr.get_next()
            with tf.Session() as sessa:
                sessa.run(itr.initializer, feed_dict={ph: file})
                while True:
                    try:
                        xa, xb, xc = sessa.run(next_element)
                        feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc,
                                     self.is_train: train_status}
                        fetches = [self.pred, self.net, self.w]
                        pred, net, w = self.sesh.run(fetches, feed_dict)
                        # for i in range(3):
                        #     neta = net[:, :, :, :int(np.shape(net)[3] / 3)]
                        #     netb = net[:, :, :, int(np.shape(net)[3] / 3):2 * int(np.shape(net)[3] / 3)]
                        #     netc = net[:, :, :, 2 * int(np.shape(net)[3] / 3):]
                        #     wa = w[:int(np.shape(net)[3] / 3), :]
                        #     wb = w[int(np.shape(net)[3] / 3):2 * int(np.shape(net)[3] / 3), :]
                        #     wc = w[2 * int(np.shape(net)[3] / 3):, :]
                        #     ac.CAM_R(neta, wa, pred, xa, dirr, 'Test_level1', bs, rd)
                        #     ac.CAM_R(netb, wb, pred, xb, dirr, 'Test_level2', bs, rd)
                        #     ac.CAM_R(netc, wc, pred, xc, dirr, 'Test_level3', bs, rd)
                        if rd == 0:
                            pdx = pred
                        else:
                            pdx = np.concatenate((pdx, pred), axis=0)
                        rd += 1
                    except tf.errors.OutOfRangeError:
                        ac.realout(pdx, dirr, 'Test', pmd)
                        break
        else:
            itr, file, ph = X.data(train=False)
            next_element = itr.get_next()
            with tf.Session() as sessa:
                sessa.run(itr.initializer, feed_dict={ph: file})
                while True:
                    try:
                        xa, xb, xc, y, _ = sessa.run(next_element)
                        feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc,
                                     self.is_train: train_status}
                        fetches = [self.pred, self.net, self.w]
                        pred, net, w = self.sesh.run(fetches, feed_dict)
                        # for i in range(3):
                        # neta = net[:, :, :, :int(np.shape(net)[3] / 3)]
                        # netb = net[:, :, :, int(np.shape(net)[3] / 3):2 * int(np.shape(net)[3] / 3)]
                        # netc = net[:, :, :, 2 * int(np.shape(net)[3] / 3):]
                        # wa = w[:int(np.shape(net)[3] / 3), :]
                        # wb = w[int(np.shape(net)[3] / 3):2 * int(np.shape(net)[3] / 3), :]
                        # wc = w[2 * int(np.shape(net)[3] / 3):, :]
                        #     ac.CAM(neta, wa, pred, xa, y, dirr, 'Test_level1', bs, pmd, rd)
                        #     ac.CAM(netb, wb, pred, xb, y, dirr, 'Test_level2', bs, pmd, rd)
                        #     ac.CAM(netc, wc, pred, xc, y, dirr, 'Test_level3', bs, pmd, rd)
                        net = np.mean(net, axis=(1, 2))
                        if rd == 0:
                            pdx = pred
                            yl = y
                            netl = net
                        else:
                            pdx = np.concatenate((pdx, pred), axis=0)
                            yl = np.concatenate((yl, y), axis=0)
                            netl = np.concatenate((netl, net), axis=0)
                        rd += 1
                    except tf.errors.OutOfRangeError:
                        ac.metrics(pdx, yl, dirr, 'Test', pmd, testset)
                        ac.tSNE_prep(flatnet=netl, ori_test=testset, y=yl, pred=pdx, path=dirr, pmd=pmd)
                        break
        now = datetime.now().isoformat()[11:]
        print("------- Testing end: {} -------\n".format(now), flush=True)

    # training
    def train(self, X, VAX, ct, bs, dirr, pmd, max_iter=np.inf, save=True, outdir="./out"):
        start_time = time.time()
        svs = 0
        if save:
            saver = tf.train.Saver(tf.global_variables(), max_to_keep=None)

        err_train = 0
        now = datetime.now().isoformat()[11:]
        print("------- Training begin: {} -------\n".format(now))
        itr, file, ph = X.data()
        next_element = itr.get_next()

        vaitr, vafile, vaph = VAX.data(train=False)
        vanext_element = vaitr.get_next()

        init_i = self.step

        with tf.Session() as sessa:
            sessa.run(itr.initializer, feed_dict={ph: file})
            sessa.run(vaitr.initializer, feed_dict={vaph: vafile})
            train_loss = []
            validation_loss = []
            valid_loss = 0
            trloss_plt = []
            valoss_plt = []

            try:
                while True:
                    xa, xb, xc, y, tum = sessa.run(next_element)
                    feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc, self.y_in: y, self.tumor: tum}

                    fetches = [self.merged_summary, self.logits, self.pred,
                               self.pred_loss, self.global_step, self.train_op]

                    summary, logits, pred, loss, i, _ = self.sesh.run(fetches, feed_dict)
                    if self.transfer:
                        i = i - init_i
                    self.train_logger.add_summary(summary, i)
                    err_train += loss

                    train_loss.append(loss)

                    try:
                        mintrain = min(train_loss)
                    except ValueError:
                        mintrain = 0

                    if loss <= mintrain and i > 29999:
                        print("round {} --> loss: ".format(i), loss)
                        temp_valid = []
                        for iii in range(20):
                            xa, xb, xc, y, tum = sessa.run(vanext_element)
                            feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc, self.y_in: y, self.tumor: tum,
                                         self.is_train: False}
                            fetches = [self.pred_loss, self.merged_summary]
                            valid_loss, valid_summary = self.sesh.run(fetches, feed_dict)
                            self.valid_logger.add_summary(valid_summary, i)
                            temp_valid.append(valid_loss)

                        tempminvalid = np.mean(temp_valid)
                        try:
                            minvalid = min(validation_loss)
                        except ValueError:
                            minvalid = 0

                        if save and tempminvalid <= minvalid:
                            validation_loss.append(tempminvalid)
                            print("round {} --> validation loss: ".format(i), tempminvalid)
                            print("New Min loss model found!", flush=True)
                            outfile = os.path.join(os.path.abspath(outdir),
                                                   "{}".format("_".join(['dropout', str(self.dropout)])))
                            saver.save(self.sesh, outfile, global_step=None)
                            svs = i

                    elif i % 1000 == 0:
                        print("round {} --> loss: ".format(i), loss)
                        temp_valid = []
                        for iii in range(100):
                            xa, xb, xc, y, tum = sessa.run(vanext_element)
                            feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc, self.y_in: y, self.tumor: tum,
                                         self.is_train: False}
                            fetches = [self.pred_loss, self.merged_summary]
                            valid_loss, valid_summary = self.sesh.run(fetches, feed_dict)
                            self.valid_logger.add_summary(valid_summary, i)
                            temp_valid.append(valid_loss)
                        tempminvalid = np.mean(temp_valid)
                        try:
                            minvalid = min(validation_loss)
                        except ValueError:
                            minvalid = 0
                        validation_loss.append(tempminvalid)
                        print("round {} --> Step Average validation loss: ".format(i), tempminvalid, flush=True)

                        # Loss figures
                        if len(train_loss) >= 1000:
                            trloss_plt.append(np.mean(train_loss[-1000:]))
                        else:
                            trloss_plt.append(np.mean(train_loss[-len(train_loss):]))
                        valoss_plt.append(tempminvalid)
                        plt.plot(trloss_plt, color='blue')
                        plt.plot(valoss_plt, color='orange')
                        plt.xlabel('thousand iterations')
                        plt.ylabel('loss')
                        plt.title('Average Train & Validation Loss (every 1000 itrs)')
                        plt.legend(['Train', 'Validation'], loc='upper right')
                        plt.savefig(outdir + '/loss.png')

                        if save and tempminvalid <= minvalid:
                            print("New Min loss model found!")
                            print("round {} --> loss: ".format(i), loss)
                            outfile = os.path.join(os.path.abspath(outdir),
                                                   "{}".format("_".join(['dropout', str(self.dropout)])))
                            saver.save(self.sesh, outfile, global_step=None)
                            svs = i

                        if i > 99999:
                            valid_mean_loss = np.mean(validation_loss[-10:-1])
                            print('Mean validation loss: {}'.format(valid_mean_loss))
                            if valid_loss > valid_mean_loss:
                                print("Early stopped! No improvement for at least 10000 iterations", flush=True)
                                break
                            else:
                                print("Passed early stopping evaluation. Continue training!")

                    elif i >= max_iter-2:
                        print("final avg loss (@ step {} = epoch {}): {}".format(
                            i + 1, np.around(i / ct * bs), err_train / i))

                        now = datetime.now().isoformat()[11:]
                        print("------- Training end: {} -------\n".format(now))

                        now = datetime.now().isoformat()[11:]
                        print("------- Final Validation begin: {} -------\n".format(now))
                        xa, xb, xc, y, tum = sessa.run(vanext_element)
                        feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc, self.y_in: y, self.tumor: tum,
                                     self.is_train: False}
                        fetches = [self.pred_loss, self.merged_summary]
                        valid_loss, valid_summary = self.sesh.run(fetches, feed_dict)

                        self.valid_logger.add_summary(valid_summary, i)
                        print("round {} --> Final Last validation loss: ".format(i), valid_loss)
                        now = datetime.now().isoformat()[11:]
                        print("------- Final Validation end: {} -------\n".format(now), flush=True)
                        try:
                            self.train_logger.flush()
                            self.train_logger.close()
                            self.valid_logger.flush()
                            self.valid_logger.close()

                        except AttributeError:  # not logging
                            print('Not logging')
                        break
            except tf.errors.OutOfRangeError:
                pass

            try:
                print("final avg loss (@ step {} = epoch {}): {}".format(
                    i + 1, np.around(i / ct * bs), err_train / i))

                now = datetime.now().isoformat()[11:]
                print("------- Training end: {} -------\n".format(now))

                if svs < 3000 and save:
                        print("Save the last model as the best model.")
                        outfile = os.path.join(os.path.abspath(outdir),
                                               "{}".format("_".join(['dropout', str(self.dropout)])))
                        saver.save(self.sesh, outfile, global_step=None)

                now = datetime.now().isoformat()[11:]
                print("------- Validation begin: {} -------\n".format(now))

                xa, xb, xc, y, tum = sessa.run(vanext_element)
                feed_dict = {self.xa_in: xa, self.xb_in: xb, self.xc_in: xc, self.y_in: y, self.tumor: tum,
                             self.is_train: False}
                fetches = [self.pred_loss, self.merged_summary, self.pred, self.net, self.w]
                valid_loss, valid_summary, pred, net, w = self.sesh.run(fetches, feed_dict)

                self.valid_logger.add_summary(valid_summary, i)
                print("round {} --> Last validation loss: ".format(i), valid_loss)
                for i in range(3):
                    neta = net[:, :, :, :int(np.shape(net)[3] / 3)]
                    netb = net[:, :, :, int(np.shape(net)[3] / 3):2 * int(np.shape(net)[3] / 3)]
                    netc = net[:, :, :, 2 * int(np.shape(net)[3] / 3):]
                    wa = w[:int(np.shape(net)[3] / 3), :]
                    wb = w[int(np.shape(net)[3] / 3):2 * int(np.shape(net)[3] / 3), :]

                    wc = w[2 * int(np.shape(net)[3] / 3):, :]

                    ac.CAM(neta, wa, pred, xa, y, dirr, 'Validation_level1', bs, pmd)
                    ac.CAM(netb, wb, pred, xb, y, dirr, 'Validation_level2', bs, pmd)
                    ac.CAM(netc, wc, pred, xc, y, dirr, 'Validation_level3', bs, pmd)
                ac.metrics(pred, y, dirr, 'Validation', pmd)
                now = datetime.now().isoformat()[11:]
                print("------- Validation end: {} -------\n".format(now), flush=True)

                try:
                    self.train_logger.flush()
                    self.train_logger.close()
                    self.valid_logger.flush()
                    self.valid_logger.close()

                except AttributeError:  # not logging
                    print('Not logging')

            except tf.errors.OutOfRangeError:
                print("final avg loss (@ step {} = epoch {}): {}".format(
                    i + 1, np.around(i / ct * bs), err_train / i))

                now = datetime.now().isoformat()[11:]
                print("------- Training end: {} -------\n".format(now))
                print('No more validation needed!')

        print("--- %s seconds ---" % (time.time() - start_time))

