"""
Main method for Panoptes

Created on 04/26/2019; modified 11/06/2019

@author: RH
"""
import os
import argparse
import numpy as np
import tensorflow as tf
import cnn5
import Sample_prep2
import pandas as pd
import cv2
import data_input_fusion as data_input3
import matplotlib
matplotlib.use('Agg')

# input
parser = argparse.ArgumentParser()
parser.add_argument('--dirr', type=str, default='trial', help='output directory')
parser.add_argument('--bs', type=int, default=24, help='batch size')
parser.add_argument('--ep', type=int, default=100, help='max epochs')
parser.add_argument('--frac', type=float, default=0.5, help='fraction of data to use')
parser.add_argument('--classes', type=int, default=2, help='number of classes to predict')
parser.add_argument('--img_size', type=int, default=299, help='input tile size (default 299)')
parser.add_argument('--dropout', type=float, default=0.5, help='drop out rate (default 0.5)')
parser.add_argument('--lr', type=float, default=0.0001, help='initial learning rate (default 0.0001)')
parser.add_argument('--cut', type=float, default=0.3, help='train and test+validation split (default 0.3)')
parser.add_argument('--pdmd', type=str, default='tumor', help='feature to predict')
parser.add_argument('--mode', type=str, default='train', help='train or test')
parser.add_argument('--modeltoload', type=str, default='', help='reload trained model')
parser.add_argument('--reference', type=str, default='../tumor_label_df.csv', help='reference label file')
parser.add_argument('--label_column', type=str, default='Tumor_normal', help='label column name in reference file')
parser.add_argument('--tile_path', type=str, default='../tiles', help='directory to tiles')
parser.add_argument('--transfer', type=bool, default=False, help='reload for transfer learning (True or False)')
parser.add_argument('--exclude', nargs='+', type=str, default=None, help='list cancer types to exclude from this study')


opt = parser.parse_args()
print('Input config:')
print(opt, flush=True)

# tumor reference dictionary
tumor_dict = {'HNSCC': int(0), 'CCRCC': int(1), 'CO': int(2), 'BRCA': int(3),
                    'LUAD': int(4), 'LSCC': int(5), 'PDA': int(6), 'UCEC': int(7), 'GBM': int(8), 'OV': int(9)}

# input image dimension
INPUT_DIM = [opt.bs, opt.img_size, opt.img_size, 3]
# hyper parameters
HYPERPARAMS = {
    "batch_size": opt.bs,
    "dropout": opt.dropout,
    "learning_rate": opt.lr,
}

# paths to directories
img_dir = '../tiles/'
LOG_DIR = "../Results/{}".format(opt.dirr)
METAGRAPH_DIR = "../Results/{}".format(opt.dirr)
data_dir = "../Results/{}/data".format(opt.dirr)
out_dir = "../Results/{}/out".format(opt.dirr)


# count numbers of training and testing images
def counters(trlist, telist, valist, cls, tumor_d):
    trcc = len(trlist['label'])
    tecc = len(telist['label'])
    vacc = len(valist['label'])
    weigh = []
    for tum in tumor_d.keys():
        trlist_x = trlist[trlist['Tumor'] == tum]
        valist_x = valist[valist['Tumor'] == tum]
        telist_x = telist[telist['Tumor'] == tum]
        wee = []
        for i in range(cls):
            ccct = len(trlist_x.loc[trlist_x['label'] == i])+len(valist_x.loc[valist_x['label'] == i])\
                   + len(telist_x.loc[telist_x['label'] == i])
            wt = np.cbrt(((trcc+tecc+vacc)/cls)/(ccct+1))
            wee.append(wt)
        weigh.append(wee)
    weigh = tf.constant(np.array(weigh))
    return trcc, tecc, vacc, weigh


# read images
def load_image(addr):
    img = cv2.imread(addr)
    img = img.astype(np.float32)
    return img


# used for tfrecord float generation
def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


# used for tfrecord labels generation
def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


# used for tfrecord images generation
def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


# loading images for dictionaries and generate tfrecords
def loader(totlist_dir, ds, dict_t):
    if ds == 'train':
        slist = pd.read_csv(totlist_dir + '/tr_sample.csv', header=0)
    elif ds == 'validation':
        slist = pd.read_csv(totlist_dir + '/va_sample.csv', header=0)
    elif ds == 'test':
        slist = pd.read_csv(totlist_dir + '/te_sample.csv', header=0)
    else:
        slist = pd.read_csv(totlist_dir + '/te_sample.csv', header=0)
    imlista = slist['L1path'].values.tolist()
    imlistb = slist['L2path'].values.tolist()
    imlistc = slist['L3path'].values.tolist()
    lblist = slist['label'].values.tolist()
    slist['Tumor'] = slist['Tumor'].replace(dict_t)
    tplist = slist['Tumor'].values.tolist()
    filename = data_dir + '/' + ds + '.tfrecords'
    writer = tf.python_io.TFRecordWriter(filename)
    for i in range(len(lblist)):
        try:
            # Load the image
            imga = load_image(imlista[i])
            imgb = load_image(imlistb[i])
            imgc = load_image(imlistc[i])
            label = lblist[i]
            tumor = tplist[i]
            # Create a feature
            feature = {ds + '/label': _int64_feature(int(label)),
                       ds + '/tumor': _int64_feature(int(tumor)),
                       ds + '/imageL1': _bytes_feature(tf.compat.as_bytes(imga.tostring())),
                       ds + '/imageL2': _bytes_feature(tf.compat.as_bytes(imgb.tostring())),
                       ds + '/imageL3': _bytes_feature(tf.compat.as_bytes(imgc.tostring()))}
            # Create an example protocol buffer
            example = tf.train.Example(features=tf.train.Features(feature=feature))

            # Serialize to string and write on the file
            writer.write(example.SerializeToString())
        except AttributeError:
            print('Error image: ' + imlista[i] + '~' + imlistb[i] + '~' + imlistc[i])
            pass

    writer.close()


# load tfrecords and prepare datasets
def tfreloader(mode, ep, bs, ctr, cte, cva):
    filename = data_dir + '/' + mode + '.tfrecords'
    if mode == 'train':
        ct = ctr
    elif mode == 'test':
        ct = cte
    else:
        ct = cva

    datasets = data_input3.DataSet(bs, ct, ep=ep, mode=mode, filename=filename)

    return datasets


# main; trc is training image count; tec is testing image count; to_reload is the model to load; test or not
def main(trc, tec, vac, weight, testset=None, to_reload=None, test=None):

    if test:  # restore for testing only
        m = cnn5.INCEPTION(INPUT_DIM, HYPERPARAMS, meta_graph=to_reload, log_dir=LOG_DIR,
                           meta_dir=METAGRAPH_DIR, weights=weight)
        print("Loaded! Ready for test!")
        if tec >= opt.bs:
            THE = tfreloader('test', 1, opt.bs, trc, tec, vac)
            m.inference(THE, opt.dirr, testset=testset, pmd=opt.pdmd)
        else:
            print("Not enough testing images!")

    elif to_reload:  # restore for further training and testing
        m = cnn5.INCEPTION(INPUT_DIM, HYPERPARAMS, meta_graph=to_reload, log_dir=LOG_DIR,
                           meta_dir=METAGRAPH_DIR, weights=weight, transfer=opt.transfer)
        print("Loaded! Restart training.")
        HE = tfreloader('train', opt.ep, opt.bs, trc, tec, vac)
        VHE = tfreloader('validation', opt.ep*100, opt.bs, trc, tec, vac)
        itt = int(trc * opt.ep / opt.bs)
        if trc <= 2 * opt.bs or vac <= opt.bs:
            print("Not enough training/validation images!")
        else:
            m.train(HE, VHE, trc, opt.bs, pmd=opt.pdmd, dirr=opt.dirr, max_iter=itt, save=True, outdir=METAGRAPH_DIR)
        if tec >= opt.bs:
            THE = tfreloader('test', 1, opt.bs, trc, tec, vac)
            m.inference(THE, opt.dirr, testset=testset, pmd=opt.pdmd)
        else:
            print("Not enough testing images!")

    else:  # train and test
        m = cnn5.INCEPTION(INPUT_DIM, HYPERPARAMS, log_dir=LOG_DIR, weights=weight)
        print("Start a new training!")
        HE = tfreloader('train', opt.ep, opt.bs, trc, tec, vac)
        VHE = tfreloader('validation', opt.ep*100, opt.bs, trc, tec, vac)
        itt = int(trc*opt.ep/opt.bs)+1
        if trc <= 2 * opt.bs or vac <= opt.bs:
            print("Not enough training/validation images!")
        else:
            m.train(HE, VHE, trc, opt.bs, pmd=opt.pdmd, dirr=opt.dirr, max_iter=itt, save=True, outdir=METAGRAPH_DIR)
        if tec >= opt.bs:
            THE = tfreloader('test', 1, opt.bs, trc, tec, vac)
            m.inference(THE, opt.dirr, testset=testset, pmd=opt.pdmd)
        else:
            print("Not enough testing images!")


if __name__ == "__main__":
    tf.reset_default_graph()
    # make directories if not exist
    for DIR in (LOG_DIR, METAGRAPH_DIR, data_dir, out_dir):
        try:
            os.mkdir(DIR)
        except FileExistsError:
            pass
    # if not exist, prepare testing and training datasets from sampling
    try:
        trs = pd.read_csv(data_dir + '/tr_sample.csv', header=0)
        tes = pd.read_csv(data_dir + '/te_sample.csv', header=0)
        vas = pd.read_csv(data_dir + '/va_sample.csv', header=0)
    except FileNotFoundError:
        try:
            tr = pd.read_csv(data_dir + '/tr_sample_full.csv', header=0)
            te = pd.read_csv(data_dir + '/te_sample_full.csv', header=0)
            va = pd.read_csv(data_dir + '/va_sample_full.csv', header=0)
        except FileNotFoundError:
            alll = Sample_prep2.big_image_sum(label_col=opt.label_column, path=opt.tile_path,
                                              ref_file=opt.reference, pdmd=opt.pdmd, exclude=opt.exclude)
            Sample_prep2.set_sep(alll, path=data_dir, cut=opt.cut)
            # Sample_prep2.set_sep_secondary(alll, path=data_dir, cut=opt.cut)
            tr = pd.read_csv(data_dir + '/tr_sample_full.csv', header=0)
            te = pd.read_csv(data_dir + '/te_sample_full.csv', header=0)
            va = pd.read_csv(data_dir + '/va_sample_full.csv', header=0)
        trs = tr.sample(frac=opt.frac, replace=False)
        trs.to_csv(data_dir + '/tr_sample.csv', header=True, index=False)
        tes = te.sample(frac=opt.frac, replace=False)
        tes = tes.sort_values(by=['Tumor', 'Slide_ID'], ascending=True)
        tes.to_csv(data_dir + '/te_sample.csv', header=True, index=False)
        vas = va.sample(frac=opt.frac, replace=False)
        vas.to_csv(data_dir + '/va_sample.csv', header=True, index=False)

    # get counts of testing, validation, and training datasets
    trc, tec, vac, weights = counters(trs, tes, vas, opt.classes, tumor_dict)

    # test or not
    if opt.mode == 'test':
        if not os.path.isfile(data_dir + '/test.tfrecords'):
            loader(data_dir, 'test', tumor_dict)
        main(trc, tec, vac, weights, testset=tes, to_reload=opt.modeltoload, test=True)
    elif opt.mode == 'train':
        if not os.path.isfile(data_dir + '/test.tfrecords'):
            loader(data_dir, 'test', tumor_dict)
        if not os.path.isfile(data_dir + '/validation.tfrecords'):
            loader(data_dir, 'validation', tumor_dict)
        if not os.path.isfile(data_dir + '/train.tfrecords'):
            loader(data_dir, 'train', tumor_dict)
        if opt.modeltoload == '':
            main(trc, tec, vac, weights, testset=tes)
        else:
            main(trc, tec, vac, weights, testset=tes, to_reload=opt.modeltoload)
    else:
        print('Mode must be specified as either train or test!')

