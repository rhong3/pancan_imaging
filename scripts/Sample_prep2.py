"""
Prepare training and testing datasets as CSV dictionaries 2.0

Created on 04/26/2019; modified on 11/06/2019

@author: RH
"""
import os
import pandas as pd
import sklearn.utils as sku
import numpy as np
import re


# get all full paths of images
def image_ids_in(root_dir, ignore=['.DS_Store', 'dict.csv', 'all.csv']):
    ids = []
    for id in os.listdir(root_dir):
        if id in ignore:
            print('Skipping ID:', id)
        else:
            ids.append(id)
    return ids


# Get intersection of 2 lists
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def tile_ids_in(inp):
    ids = []
    try:
        for id in os.listdir(inp['path']):
            if '_{}.png'.format(str(inp['sldnum'])) in id:
                ids.append([inp['slide'], inp['level'], inp['path']+'/'+id, inp['BMI'], inp['age'], inp['label']])
    except FileNotFoundError:
        print('Ignore:', inp['path'])

    return ids


# pair tiles of 10x, 5x, 2.5x of the same area
def paired_tile_ids_in(patient, slide, tumor, label, root_dir):
    dira = os.path.isdir(root_dir + 'level1')
    dirb = os.path.isdir(root_dir + 'level2')
    dirc = os.path.isdir(root_dir + 'level3')
    if dira and dirb and dirc:
        fac = 1000
        ids = []
        for level in range(1, 4):
            dirr = root_dir + 'level{}'.format(str(level))
            for id in os.listdir(dirr):
                if '.png' in id:
                    x = int(float(id.split('x-', 1)[1].split('-', 1)[0]) / fac)
                    y = int(float(re.split('.p', id.split('y-', 1)[1])[0]) / fac)
                    ids.append([patient, slide, tumor, label, level, dirr + '/' + id, x, y])
        ids = pd.DataFrame(ids, columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'level', 'path', 'x', 'y'])
        idsa = ids.loc[ids['level'] == 1]
        idsa = idsa.drop(columns=['level'])
        idsa = idsa.rename(index=str, columns={"path": "L1path"})
        idsb = ids.loc[ids['level'] == 2]
        idsb = idsb.drop(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'level'])
        idsb = idsb.rename(index=str, columns={"path": "L2path"})
        idsc = ids.loc[ids['level'] == 3]
        idsc = idsc.drop(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'level'])
        idsc = idsc.rename(index=str, columns={"path": "L3path"})
        idsa = pd.merge(idsa, idsb, on=['x', 'y'], how='left', validate="many_to_many")
        idsa['x'] = idsa['x'] - (idsa['x'] % 2)
        idsa['y'] = idsa['y'] - (idsa['y'] % 2)
        idsa = pd.merge(idsa, idsc, on=['x', 'y'], how='left', validate="many_to_many")
        idsa = idsa.drop(columns=['x', 'y'])
        idsa = idsa.dropna()
        idsa = sku.shuffle(idsa)
    else:
        print('Pass: ', root_dir)
        idsa = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])

    return idsa


# Prepare label at per patient level
def big_image_sum(label_col, path, ref_file, pdmd='tumor', exclude=None):
    ref = pd.read_csv(ref_file, header=0)
    big_images = []
    ref = ref.loc[ref[label_col].notna()]
    for idx, row in ref.iterrows():
        big_images.append([row['Patient_ID'], row['Slide_ID'], row['Tumor'],
                           path + "/{}/{}/{}/".format(str(row['Tumor']), str(row['Patient_ID']),
                                                      row['Slide_ID'].split('-')[-1]), row[label_col]])
    datapd = pd.DataFrame(big_images, columns=['Patient_ID', 'Slide_ID', 'Tumor', 'path', 'label'])
    datapd = datapd.dropna()
    if exclude:
        datapd = datapd[~datapd['Tumor'].isin(exclude)]
    if pdmd != 'origin':
        rm = []
        for tu in list(datapd.Tumor.unique()):
            for lb in list(datapd.label.unique()):
                if datapd.loc[(datapd['Tumor'] == tu) & (datapd['label'] == lb)].shape[0] < 3:
                    rm.append(tu)
        datapd = datapd[~datapd['Tumor'].isin(rm)]
        print('Remove rare case cancer types if any: ', rm, flush=True)

    return datapd


# seperate into training and testing; each type is the same separation ratio on big images
# test and train csv files contain tiles' path.
def set_sep(alll, path, cut=0.3):
    trlist = []
    telist = []
    valist = []

    for tm in list(alll.Tumor.unique()):
        sub = alll[alll['Tumor'] == tm]
        unq = list(sub.Patient_ID.unique())
        np.random.shuffle(unq)
        validation = unq[:np.max([int(len(unq) * cut / 2), 1])]
        valist.append(sub[sub['Patient_ID'].isin(validation)])
        test = unq[np.max([int(len(unq) * cut / 2), 1]):np.max([int(len(unq) * cut), 2])]
        telist.append(sub[sub['Patient_ID'].isin(test)])
        train = unq[np.max([int(len(unq) * cut), 2]):]
        trlist.append(sub[sub['Patient_ID'].isin(train)])

    test = pd.concat(telist)
    train = pd.concat(trlist)
    validation = pd.concat(valist)

    test.to_csv(path + '/te_sample_raw.csv', header=True, index=False)
    train.to_csv(path + '/tr_sample_raw.csv', header=True, index=False)
    validation.to_csv(path + '/va_sample_raw.csv', header=True, index=False)

    test_tiles = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])
    train_tiles = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])
    validation_tiles = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])
    for idx, row in test.iterrows():
        tile_ids = paired_tile_ids_in(row['Patient_ID'], row['Slide_ID'], row['Tumor'], row['label'], row['path'])
        test_tiles = pd.concat([test_tiles, tile_ids])
    for idx, row in train.iterrows():
        tile_ids = paired_tile_ids_in(row['Patient_ID'], row['Slide_ID'], row['Tumor'], row['label'], row['path'])
        train_tiles = pd.concat([train_tiles, tile_ids])
    for idx, row in validation.iterrows():
        tile_ids = paired_tile_ids_in(row['Patient_ID'], row['Slide_ID'], row['Tumor'], row['label'], row['path'])
        validation_tiles = pd.concat([validation_tiles, tile_ids])

    # No shuffle on test set
    train_tiles = sku.shuffle(train_tiles)
    validation_tiles = sku.shuffle(validation_tiles)
    test_tiles = test_tiles.sort_values(by=['Tumor', 'Slide_ID'], ascending=True)

    test_tiles.to_csv(path+'/te_sample_full.csv', header=True, index=False)
    train_tiles.to_csv(path+'/tr_sample_full.csv', header=True, index=False)
    validation_tiles.to_csv(path+'/va_sample_full.csv', header=True, index=False)


# TO KEEP SPLIT SAME AS BASELINES. seperate into training and testing; each type is the same separation
# ratio on big images test and train csv files contain tiles' path.
def set_sep_secondary(alll, path, cut=0.3, theme3path='../Theme3_split.csv'):
    theme3 = pd.read_csv(theme3path, header=0)

    test = theme3[theme3['set'] == 'test']
    test = test.drop(columns=['set'])
    train = theme3[theme3['set'] == 'train']
    train = train.drop(columns=['set'])
    validation = theme3[theme3['set'] == 'validation']
    validation = validation.drop(columns=['set'])

    test.to_csv(path + '/te_sample_raw.csv', header=True, index=False)
    train.to_csv(path + '/tr_sample_raw.csv', header=True, index=False)
    validation.to_csv(path + '/va_sample_raw.csv', header=True, index=False)

    test_tiles = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])
    train_tiles = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])
    validation_tiles = pd.DataFrame(columns=['Patient_ID', 'Slide_ID', 'Tumor', 'label', 'L1path', 'L2path', 'L3path'])
    for idx, row in test.iterrows():
        tile_ids = paired_tile_ids_in(row['Patient_ID'], row['Slide_ID'], row['Tumor'], row['label'], row['path'])
        test_tiles = pd.concat([test_tiles, tile_ids])
    for idx, row in train.iterrows():
        tile_ids = paired_tile_ids_in(row['Patient_ID'], row['Slide_ID'], row['Tumor'], row['label'], row['path'])
        train_tiles = pd.concat([train_tiles, tile_ids])
    for idx, row in validation.iterrows():
        tile_ids = paired_tile_ids_in(row['Patient_ID'], row['Slide_ID'], row['Tumor'], row['label'], row['path'])
        validation_tiles = pd.concat([validation_tiles, tile_ids])

    # No shuffle on test set
    train_tiles = sku.shuffle(train_tiles)
    validation_tiles = sku.shuffle(validation_tiles)
    test_tiles = test_tiles.sort_values(by=['Tumor', 'Slide_ID'], ascending=True)

    test_tiles.to_csv(path + '/te_sample_full.csv', header=True, index=False)
    train_tiles.to_csv(path + '/tr_sample_full.csv', header=True, index=False)
    validation_tiles.to_csv(path + '/va_sample_full.csv', header=True, index=False)

