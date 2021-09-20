"""
Aggregate all CAM output to 1 single giant image

Created on 09/17/2021

@author: RH
"""

import pandas as pd
import cv2
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--dirr', type=str, default='trial', help='output directory')
opt = parser.parse_args()
dirr = opt.dirr


hmpd = pd.DataFrame(columns=['idx', 'bool', 'hmpath', 'level'])
olpd = pd.DataFrame(columns=['idx', 'bool', 'olpath', 'level'])
# Map output CAMs to dict
for lv in range(1, 4):
    hm = []
    ol = []
    for it in os.listdir('../Results/'+dirr+'/out/Test_level'+str(lv)+'_img'):
        if '_hm.png' in it:
            hm.append([it.split('_')[0], it.split('_')[1], it])
        elif '_ol.png' in it:
            ol.append([it.split('_')[0], it.split('_')[1], it])
    hm = pd.DataFrame(hm, columns=['idx', 'bool', 'hmpath'])
    hm['level'] = lv
    ol = pd.DataFrame(ol, columns=['idx', 'bool', 'olpath'])
    ol['level'] = lv
    hmpd.append(hm)
    olpd.append(ol)

pdpd = hmpd.join(olpd.set_index('idx'))
tiles = pd.read_csv('../Results/'+dirr+'/out/Test_tile.csv')
tiles['idx'] = tiles.index

tiles = tiles.join()


# Create giant image from dict


