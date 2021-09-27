"""
load a trained model and apply it

Created on 12/16/2019

Modified on 09/21/2021

@author: RH
"""
import argparse
import matplotlib
matplotlib.use('Agg')
import os
import numpy as np
import pandas as pd
import cv2
import tensorflow as tf
import re

# input
parser = argparse.ArgumentParser()
parser.add_argument('--bs', type=int, default=12, help='batch size')
parser.add_argument('--cls', type=int, default=5, help='number of classes to predict')
parser.add_argument('--img_size', type=int, default=299, help='input tile size (default 299)')
parser.add_argument('--pdmd', type=str, default='stage', help='feature to predict')
parser.add_argument('--modeltoload', type=str, default='', help='reload trained model')
parser.add_argument('--metadir', type=str, default='', help='reload trained model')
parser.add_argument('--imgfile', nargs='+', type=str, default=None,
                    help='load the image (eg. CCRCC/C3L-SSSSS-SS,CCRCC/C3L-SSSSS-SS)')


# pair tiles of 10x, 5x, 2.5x of the same area
def paired_tile_ids_in(root_dir):
    fac = 1000
    ids = []
    for level in range(1, 4):
        dirrr = root_dir + '/level{}'.format(str(level))
        for id in os.listdir(dirrr):
            if '.png' in id:
                x = int(float(id.split('x-', 1)[1].split('-', 1)[0]) / fac)
                y = int(float(re.split('.p', id.split('y-', 1)[1])[0]) / fac)
                ids.append([level, dirrr + '/' + id, x, y])
            else:
                print('Skipping ID:', id)
    ids = pd.DataFrame(ids, columns=['level', 'path', 'x', 'y'])
    idsa = ids.loc[ids['level'] == 1]
    idsa = idsa.drop(columns=['level'])
    idsa = idsa.rename(index=str, columns={"path": "L1path"})
    idsb = ids.loc[ids['level'] == 2]
    idsb = idsb.drop(columns=['level'])
    idsb = idsb.rename(index=str, columns={"path": "L2path"})
    idsc = ids.loc[ids['level'] == 3]
    idsc = idsc.drop(columns=['level'])
    idsc = idsc.rename(index=str, columns={"path": "L3path"})
    idsa = pd.merge(idsa, idsb, on=['x', 'y'], how='left', validate="many_to_many")
    idsa['x'] = idsa['x'] - (idsa['x'] % 2)
    idsa['y'] = idsa['y'] - (idsa['y'] % 2)
    idsa = pd.merge(idsa, idsc, on=['x', 'y'], how='left', validate="many_to_many")
    idsa = idsa.drop(columns=['x', 'y'])
    idsa = idsa.dropna()
    idsa = idsa.reset_index(drop=True)

    return idsa


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
def loaderX(totlist_dir):
    slist = paired_tile_ids_in(totlist_dir)
    slist.insert(loc=0, column='Num', value=slist.index)
    slist.to_csv(totlist_dir + '/te_sample.csv', header=True, index=False)
    imlista = slist['L1path'].values.tolist()
    imlistb = slist['L2path'].values.tolist()
    imlistc = slist['L3path'].values.tolist()
    filename = data_dir + '/test.tfrecords'
    writer = tf.python_io.TFRecordWriter(filename)
    for i in range(len(imlista)):
        try:
            # Load the image
            imga = load_image(imlista[i])
            imgb = load_image(imlistb[i])
            imgc = load_image(imlistc[i])
            # Create a feature
            feature = {'test/imageL1': _bytes_feature(tf.compat.as_bytes(imga.tostring())),
                       'test/imageL2': _bytes_feature(tf.compat.as_bytes(imgb.tostring())),
                       'test/imageL3': _bytes_feature(tf.compat.as_bytes(imgc.tostring()))}
            # Create an example protocol buffer
            example = tf.train.Example(features=tf.train.Features(feature=feature))

            # Serialize to string and write on the file
            writer.write(example.SerializeToString())
        except AttributeError:
            print('Error image: ' + imlista[i] + '~' + imlistb[i] + '~' + imlistc[i])
            pass

    writer.close()


import cnn5 as cnn
import data_input_fusion as data_input


# load tfrecords and prepare datasets
def tfreloader(bs, ct):
    filename = data_dir + '/test.tfrecords'
    datasets = data_input.DataSet(bs, ct, mode='test', filename=filename)

    return datasets


def main(imgfile, bs, cls, modeltoload, pdmd, data_dir, out_dir, LOG_DIR, METAGRAPH_DIR):
    if pdmd == 'stage':
        pos_ls = ['stage0', 'stage1', 'stage2', 'stage3', 'stage4']
        pos_score = ['stage0_score', 'stage1_score', 'stage2_score', 'stage3_score', 'stage4_score']
    elif pdmd == "grade":
        pos_ls = ['grade0', 'grade1', 'grade2', 'grade3', 'grade4']
        pos_score = ['grade0_score', 'grade1_score', 'grade2_score', 'grade3_score', 'grade4_score']
    elif pdmd == "cellularity":
        pos_ls = ['0_79', '80_89', '90_100']
        pos_score = ['0_79_score', '80_89_score', '90_100_score']
    elif pdmd == "nuclei":
        pos_ls = ['0_49', '50_79', '80_100']
        pos_score = ['0_49_score', '50_79_score', '80_100_score']
    elif pdmd == "necrosis":
        pos_ls = ['0', '1_9', '10_100']
        pos_score = ['0_score', '1_9_score', '10_100_score']
    elif pdmd == 'origin':
        pos_ls = ['HNSCC', 'CCRCC', 'CO', 'BRCA', 'LUAD',
                  'LSCC', 'PDA', 'UCEC', 'GBM', 'OV']
        pos_score = ['HNSCC_score', 'CCRCC_score', 'CO_score', 'BRCA_score', 'LUAD_score', 'LSCC_score',
                     'PDA_score', 'UCEC_score', 'GBM_score', 'OV_score']
    else:
        pos_score = ["NEG_score", "POS_score"]
        pos_ls = [pdmd, 'negative']

    slideref = pd.read_csv('../imglowres.csv')
    slideref = slideref[(slideref['SlideID'] == imgfile.split('/')[1].split('.sv')[0])]

    n_x = int(slideref["n_x"].tolist()[0])
    n_y = int(slideref["n_y"].tolist()[0])

    lowres = cv2.imread('../lowres/'+imgfile.split('/')[1].split('.sv')[0]+'.png')
    raw_img = np.array(lowres)[:, :, :3]

    if not os.path.isfile(data_dir + '/level3/dict.csv'):
        tumor = imgfile.split('/')[0]
        slideID = imgfile.split("-")[-1]
        patientID = imgfile.rsplit("-", 1)[0].split('/')[-1]
        os.symlink("../../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level1', data_dir + '/level1',
                   target_is_directory=True)
        os.symlink("../../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level2', data_dir + '/level2',
                   target_is_directory=True)
        os.symlink("../../../tiles/" + tumor + "/" + patientID + "/" + slideID + '/level3', data_dir + '/level3',
                   target_is_directory=True)
    if not os.path.isfile(data_dir + '/test.tfrecords'):
        loaderX(data_dir)
    if not os.path.isfile(out_dir + '/Test.csv'):
        # input image dimension
        INPUT_DIM = [bs, 299, 299, 3]
        # hyper parameters
        HYPERPARAMS = {
            "batch_size": bs,
            "dropout": 0.5,
            "learning_rate": 1E-4,
            "classes": cls,
            "sup": False
        }
        m = cnn.INCEPTION(INPUT_DIM, HYPERPARAMS, meta_graph=modeltoload, log_dir=LOG_DIR, meta_dir=METAGRAPH_DIR)

        print("Loaded! Ready for test!")
        HE = tfreloader(bs, None)
        m.inference(HE, out_dir, bs=bs, realtest=True, pmd=pdmd)

    ### Heatmap ###
    slist = pd.read_csv(data_dir + '/te_sample.csv', header=0)
    # load dictionary of predictions on tiles
    teresult = pd.read_csv(out_dir+'/Test.csv', header=0)
    # join 2 dictionaries
    joined = pd.merge(slist, teresult, how='inner', on=['Num'])
    joined = joined.drop(columns=['Num'])
    joined['L1img'] = joined['L1path'].str.rsplit('/', 1, expand=True)[1]
    tile_dict = pd.read_csv(data_dir+'/level1/dict.csv', header=0)
    tile_dict['L1img'] = tile_dict['Loc'].str.rsplit('/', 1, expand=True)[1]
    joined_dict = pd.merge(joined, tile_dict, how='inner', on=['L1img'])
    logits = joined_dict[pos_score]
    prd_ls = np.asmatrix(logits).argmax(axis=1).astype('uint8')
    prd = int(np.mean(prd_ls))
    print(str(pos_ls[prd])+'!')
    print("Prediction score = " + str(round(logits.iloc[:, prd].mean(), 5)))

    joined_dict['predict_index'] = prd_ls
    # save joined dictionary
    joined_dict.to_csv(out_dir + '/finaldict.csv', index=False)

    # output heat map of pos and neg.
    # initialize a graph and for each RGB channel
    opt = np.full((n_x, n_y), 0)
    hm_R = np.full((n_x, n_y), 0)
    hm_G = np.full((n_x, n_y), 0)
    hm_B = np.full((n_x, n_y), 0)

    # Positive is labeled red in output heat map
    for index, row in joined_dict.iterrows():
        opt[int(row["X_pos"]), int(row["Y_pos"])] = 255
        if row['predict_index'] == 0:
            hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 55
            hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 126
            hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 184
        elif row['predict_index'] == 1:
            hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 228
            hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 26
            hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 28
        elif row['predict_index'] == 2:
            hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 77
            hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 175
            hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 74
        elif row['predict_index'] == 3:
            hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 255
            hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 255
            hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 51
        elif row['predict_index'] == 4:
            hm_R[int(row["X_pos"]), int(row["Y_pos"])] = 191
            hm_G[int(row["X_pos"]), int(row["Y_pos"])] = 64
            hm_B[int(row["X_pos"]), int(row["Y_pos"])] = 191
        else:
            pass
    # expand 5 times
    opt = opt.repeat(50, axis=0).repeat(50, axis=1)

    # small-scaled original image
    ori_img = cv2.resize(raw_img, (np.shape(opt)[0], np.shape(opt)[1]))
    ori_img = ori_img[:np.shape(opt)[1], :np.shape(opt)[0], :3]
    cv2.imwrite(out_dir + '/Original_scaled.png', ori_img)

    # binary output image
    topt = np.transpose(opt)
    opt = np.full((np.shape(topt)[0], np.shape(topt)[1], 3), 0)
    opt[:, :, 0] = topt
    opt[:, :, 1] = topt
    opt[:, :, 2] = topt
    cv2.imwrite(out_dir + '/Mask.png', opt * 255)

    # output heatmap
    hm_R = np.transpose(hm_R)
    hm_G = np.transpose(hm_G)
    hm_B = np.transpose(hm_B)
    hm_R = hm_R.repeat(50, axis=0).repeat(50, axis=1)
    hm_G = hm_G.repeat(50, axis=0).repeat(50, axis=1)
    hm_B = hm_B.repeat(50, axis=0).repeat(50, axis=1)
    hm = np.dstack([hm_B, hm_G, hm_R])
    cv2.imwrite(out_dir + '/HM.png', hm)

    # superimpose heatmap on scaled original image
    overlay = ori_img * 0.5 + hm * 0.5
    cv2.imwrite(out_dir + '/Overlay.png', overlay)

    ### CAM ###
    for pre in ['ol', 'hm']:
        fac = 50
        campath = pre+'l1path'
        canvas = np.full((np.shape(opt)[0], np.shape(opt)[1], 3), 0)
        for idx, row in joined_dict.iterrows():
            imm = cv2.imread(row[campath])[0:250, 0:250, :]
            imm = cv2.resize(imm, (fac, fac))
            canvas[int(row["Y_pos"])*fac:int(row["Y_pos"])*fac+fac,
            int(row["X_pos"])*fac:int(row["X_pos"])*fac+fac, :] = imm
        cv2.imwrite(out_dir + '/' + pre + '_CAM.png', canvas)
        if pre == 'hm':
            # superimpose heatmap on scaled original image
            overlayhm = ori_img * 0.5 + canvas * 0.5
            cv2.imwrite(out_dir + '/cam_Overlay.png', overlayhm)


if __name__ == "__main__":
    option = parser.parse_args()
    print('Input config:')
    print(option, flush=True)

    for imgfile in option.imgfile:
        sld = imgfile.split('/')[1]
        # paths to directories
        LOG_DIR = "../Results/{}_{}".format(option.pdmd, sld)
        METAGRAPH_DIR = "../Results/{}".format(option.metadir)
        data_dir = "../Results/{}_{}/data".format(option.pdmd, sld)
        out_dir = "../Results/{}_{}/out".format(option.pdmd, sld)

        for DIR in (LOG_DIR, data_dir, out_dir):
            try:
                os.mkdir(DIR)
            except FileExistsError:
                pass

        main(imgfile, option.bs, option.cls, option.modeltoload, option.pdmd,
             data_dir, out_dir, LOG_DIR, METAGRAPH_DIR)



