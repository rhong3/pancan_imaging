"""
Make tSNE mosaic for X models

Created on Sep 13 2019

@author: lwk, RH
"""

import pandas as pd
from PIL import Image
import sys
import os

filename = sys.argv[1]   # DEFAULT='tSNE_P_N'
bin = int(sys.argv[2])   # DEFAULT=50
size = int(sys.argv[3])  # DEFAULT=299
pdmd = sys.argv[4]
dirr = sys.argv[5]
outim = sys.argv[6]


# random select representative images and output the file paths
def sample(dat, md, bins):
    if md == 'stage':
        classes = 5
        redict = {1: 'stage1_score', 2: 'stage2_score', 3: 'stage3_score', 4: 'stage4_score', 0: 'stage0_score'}
        cutoff = 0.25
    elif md == "grade":
        redict = {1: 'grade1_score', 2: 'grade2_score', 3: 'grade3_score', 4: 'grade4_score', 0: 'grade0_score'}
        classes = 5
        cutoff = 0.25
    elif md == "cellularity":
        redict = {0: 'X0_79_score', 1: 'X80_89_score', 2: 'X90_100_score'}
        classes = 3
        cutoff = 0.5
    elif md == "nuclei":
        redict = {0: 'X0_49_score', 1: 'X50_79_score', 2: 'X80_100_score'}
        classes = 3
        cutoff = 0.5
    elif md == "necrosis":
        redict = {0: 'X0_score', 1: 'X1_9_score', 2: 'X10_100_score'}
        classes = 3
        cutoff = 0.5
    else:
        redict = {0: 'NEG_score', 1: 'POS_score'}
        classes = 2
        cutoff = 0.6
    sampledls = []
    for m in range(classes):
        for i in range(bins):
            for j in range(bins):
                try:
                    sub = dat.loc[(dat['x_int'] == i) & (dat['y_int'] == j)
                                    & (dat[redict[m]] > cutoff) & (dat['True_label'] == m)]
                    picked = sub.sample(1, replace=False)
                    for idx, row in picked.iterrows():
                        sampledls.append([row['L1path'], row['L2path'], row['L3path'], row['x_int'], row['y_int']])
                except ValueError:
                    pass
    samples = pd.DataFrame(sampledls, columns=['L0impath', 'L1impath', 'L2impath', 'x_int', 'y_int'])
    return samples


if __name__ == "__main__":
    dirls = dirr.split(',')

    for i in dirls:
        try:
            ipdat = pd.read_csv('../Results/{}/out/{}.csv'.format(i, filename))
            imdat = sample(ipdat, pdmd, bin)
            imdat.to_csv('../Results/{}/out/tsne_selected.csv'.format(i), index=False)
            for j in range(3):
                new_im = Image.new(mode='RGB', size=(size*(bin+1), size*(bin+1)), color='white')

                for idx, rows in imdat.iterrows():
                    impath = rows['L{}impath'.format(j)]
                    x = rows.x_int
                    y = rows.y_int
                    try:
                        im = Image.open(impath)
                        im.thumbnail((size, size))
                        new_im.paste(im, ((x-1)*size, (bin-y)*size))
                    except FileNotFoundError:
                        print(impath)
                        pass
                new_im.save(os.path.abspath('../Results/{}/out/{}_{}.jpeg'.format(i, outim, j)), "JPEG")
                print('{} done'.format(i))
        except FileNotFoundError:
            print('{} passed'.format(i))
            pass


