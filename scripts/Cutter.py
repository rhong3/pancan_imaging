"""
Tile svs/scn files

Created on 11/01/2018

@author: RH
"""

import time
import matplotlib
import os
import shutil
import pandas as pd
matplotlib.use('Agg')
import Slicer
import staintools


# Get all images in the root directory
def image_ids_in(root_dir, ignore=['.DS_Store', 'dict.csv']):
    ids = []
    for id in os.listdir(root_dir):
        if id in ignore:
            print('Skipping ID:', id)
        elif '.svs' in id:
            dirname = id.split('.')[0][:-3]
            sldnum = id.split('-')[-1].split('.')[0]
            ids.append((id, dirname, sldnum))
        else:
            continue
    return ids


# cut; each level is 2 times difference (20x, 10x, 5x)
def cut(impath, outdir):
    try:
        os.mkdir(outdir)
    except FileExistsError:
        pass
    # load standard image for normalization
    std = staintools.read_image("../colorstandard.png")
    std = staintools.LuminosityStandardizer.standardize(std)
    # cut tiles with coordinates in the name (exclude white)
    start_time = time.time()
    CPTAClist = image_ids_in(impath)

    CPTACpp = pd.DataFrame(CPTAClist, columns=['id', 'dir', 'sld'])
    CPTACpp.to_csv(outdir+'/sum.csv', index=False)

    for i in CPTAClist:
        try:
            os.mkdir("{}/{}".format(outdir, i[1]))
        except FileExistsError:
            pass
        try:
            os.mkdir("{}/{}/{}".format(outdir, i[1], i[2]))
        except FileExistsError:
            pass
        outfolder = "{}/{}/{}".format(outdir, i[1], i[2])
        for m in range(1, 4):
            if m == 0:
                tff = 1
                level = 0
            elif m == 1:
                tff = 2
                level = 0
            elif m == 2:
                tff = 1
                level = 1
            elif m == 3:
                tff = 2
                level = 1
            otdir = "{}/level{}".format(outfolder, str(m))
            try:
                os.mkdir(otdir)
            except FileExistsError:
                pass
            try:
                n_x, n_y, raw_img, ct = Slicer.tile(image_file=impath+'/'+i[0], outdir=otdir,
                                                                level=level, std_img=std, ft=tff)
            except Exception as err:
                print(type(err))
                print(err)
                pass
            if len(os.listdir(otdir)) < 2:
                shutil.rmtree(otdir, ignore_errors=True)
        if len(os.listdir(outfolder)) < 3:
            shutil.rmtree(outfolder, ignore_errors=True)
            print(outfolder+' has less than 3 levels. Deleted!')

    print("--- %s seconds ---" % (time.time() - start_time))


# Run as main
#
if __name__ == "__main__":
    if not os.path.isdir('../tiles'):
        os.mkdir('../tiles')
    for cancer in ['UCEC', 'GBM', 'LSCC', 'CCRCC', 'HNSCC', 'LUAD', 'CM', 'PDA', 'SAR']:
        cut('../images/'+cancer, '../tiles/'+cancer)
