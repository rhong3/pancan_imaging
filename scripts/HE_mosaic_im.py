"""
Make tSNE mosaic for Immune jobs

Created on Dec 3 2021

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
    sampledls = []
    for i in range(bins):
        for j in range(bins):
            try:
                sub = dat.loc[(dat['x_int'] == i) & (dat['y_int'] == j)]
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
            ipdat['X0'] = (ipdat['X0']+110)
            ipdat['X0'] = ipdat['X0']/ipdat['X0'].max()*bin
            ipdat['X1'] = (ipdat['X1']+110)
            ipdat['X1'] = ipdat['X1'] / ipdat['X0'].max()*bin
            ipdat['x_int'] = ipdat['X0'].round()
            ipdat['y_int'] = ipdat['X1'].round()
            imdat = sample(ipdat, pdmd, bin)
            imdat.to_csv('../Results/{}/out/tsne_selected.csv'.format(i), index=False)
            for j in range(3):
                new_im = Image.new(mode='RGB', size=(size*(bin+1), size*(bin+1)), color='white')

                for idx, rows in imdat.iterrows():
                    impath = rows['L{}impath'.format(j)]
                    x = int(rows.x_int)
                    y = int(rows.y_int)
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


