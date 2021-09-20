"""
Aggregate all CAM output to 1 single giant image

Created on 09/17/2021

@author: RH
"""

import pandas as pd
import cv2
import argparse
import os
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--dirr', type=str, default='trial', help='output directory')
parser.add_argument('--mode', type=str, default='ol', help='heatmap only or overlay')
parser.add_argument('--slides', nargs='+', type=str, default=None, help='slides to plot')
parser.add_argument('--filter', type=str, default=None, help='plot only Correct/Wrong tiles')

opt = parser.parse_args()
dirr = opt.dirr
mode = opt.mode

# Map output CAMs to dict
hm = []
ol = []
for it in os.listdir('../Results/'+dirr+'/out/Test_level1_img'):
    if '_hm.png' in it:
        hm.append([it.split('_')[0], it.split('_')[1], '../Results/'+dirr+'/out/Test_level1_img/'+it,
                   '../Results/'+dirr+'/out/Test_level2_img/'+it, '../Results/'+dirr+'/out/Test_level3_img/'+it])
    elif '_ol.png' in it:
        ol.append([it.split('_')[0], it.split('_')[1], '../Results/'+dirr+'/out/Test_level1_img/'+it,
                   '../Results/'+dirr+'/out/Test_level2_img/'+it, '../Results/'+dirr+'/out/Test_level3_img/'+it])

hm = pd.DataFrame(hm, columns=['idx', 'bool', 'caml1path', 'caml2path', 'caml3path'])
ol = pd.DataFrame(ol, columns=['idx', 'bool', 'caml1path', 'caml2path', 'caml3path'])
hm['idx'] = hm['idx'].astype(int)
ol['idx'] = ol['idx'].astype(int)

tiles = pd.read_csv('../Results/'+dirr+'/out/Test_tile.csv', header=0)
tiles['idx'] = tiles.index

hmtiles = tiles.join(hm.set_index('idx'), on='idx', how='inner')
oltiles = tiles.join(ol.set_index('idx'), on='idx', how='inner')
hmtiles.to_csv('../Results/'+dirr+'/out/hmtiles.csv', index=False)
oltiles.to_csv('../Results/'+dirr+'/out/oltiles.csv', index=False)

# Create giant image from dict
for slide in opt.slides:
    if mode == "hm":
        tdict = hmtiles
    else:
        tdict = oltiles
    print(slide)
    if opt.filter:
        tdict = tdict[(tdict['bool'] == opt.filter) & (tdict['Slide_ID'] == slide)]
        filt = opt.filter
    else:
        tdict = tdict[tdict['Slide_ID'] == slide]
        filt = ""
    tm = tdict.iloc[0, 2]
    pt = tdict.iloc[0, 0]

    for j in range(1, 4):
        idict = pd.read_csv('../tiles/'+tm+'/'+pt+'/'+slide.split('-')[-1]+'/level'+str(j)+'/dict.csv', header=0)
        canvas = np.full(((idict['X_pos'].max()*500+1000)*(2**(j-1)), (idict['Y_pos'].max()*500+1000)*(2**(j-1)), 3), 0)
        for idx, row in tdict.iterrows():
            x = int(int(row['L1path'].split('x-')[1].split('-y')[0]))
            y = int(int(row['L1path'].split('y-')[1].split('.pn')[0]))
            imm = cv2.imread(row['caml1path'])[25:275, 25:275, :]
            imm = cv2.resize(imm, (500, 500))
            canvas[x:x+500, y:y+500, :] = imm
        cv2.imwrite('../Results/'+dirr+'/out/'+slide+'_'+mode+'_level'+str(j)+'_'+filt+'.jpeg', canvas)

