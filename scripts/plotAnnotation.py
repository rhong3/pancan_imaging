import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import feather
import openslide
import libtiff
# from openslide import OpenSlideError
import os
import PIL
from PIL import Image
from PIL import ImageDraw
import re
import sys

import argparse
parser = argparse.ArgumentParser()
#Universal arguments
parser.add_argument('--scaleFactor',type=int,default=4)
parser.add_argument('--imageID',type=str,default='C3L-02650-25') 
parser.add_argument('--originalSlideFile',type=str,default='/gpfs/data/proteomics/projects/Josh_imaging/images/LSCC/C3L-02650-25.svs')
parser.add_argument('--outcomeIndex',type=int,default=1)
parser.add_argument('--tileProbFile',type=str,default='/gpfs/data/proteomics/home/jw4359/cellOfOrigin/modelOutputs-multi-10/Xception-dkr0.3-l20-fromScratch-all/all-test_preds_tile.feather')
parser.add_argument('--outDir',type=str,default='/gpfs/data/proteomics/home/jw4359/cellOfOrigin/annotated_images-2')

args = parser.parse_args()
print(args)

def open_slide(filename):
    """
    Open a whole-slide image (*.svs, etc).
    Args:
    filename: Name of the slide file.
    Returns:
    An OpenSlide object representing a whole-slide image.
    """
    try:
        slide = openslide.open_slide(filename)
    except OpenSlideError:
        slide = None
    except FileNotFoundError:
        slide = None
    return slide

def slide_to_scaled_pil_image(slide,SCALE_FACTOR=args.scaleFactor):
    """
    Convert a WSI training slide to a scaled-down PIL image.
    Returns:
    Tuple consisting of scaled-down PIL image, original width, original height, new width, and new height.
    """
    large_w, large_h = slide.dimensions
    new_w = math.floor(large_w / SCALE_FACTOR)
    new_h = math.floor(large_h / SCALE_FACTOR)
    level = slide.get_best_level_for_downsample(SCALE_FACTOR)
    whole_slide_image = slide.read_region((0, 0), level, slide.level_dimensions[level])
    img = whole_slide_image.convert("RGB")
    if SCALE_FACTOR!=1:
        img = img.resize((new_w, new_h), PIL.Image.BILINEAR)
    return img, large_w, large_h, new_w, new_h

def show_slide(slide,SCALE_FACTOR=args.scaleFactor):
    """
    Display a WSI slide on the screen, where the slide has been scaled down and converted to a PIL image.
    """
    pil_img = slide_to_scaled_pil_image(slide,SCALE_FACTOR)[0]
    pil_img.show()


slide_PIL = slide_to_scaled_pil_image(open_slide(args.originalSlideFile),args.scaleFactor)

test_images = pd.read_csv('/gpfs/data/proteomics/home/jw4359/cellOfOrigin/outcomeTables/multiResolutionInput/test.omicsAnnotated.multiResolution.csv')
test_images = test_images.sample(frac=1,random_state=123)
searchfor = ['CCRCC','HNSCC','LSCC','LUAD','PDA','UCEC']
test_images = test_images[test_images['cancerType'].str.contains('|'.join(searchfor))]
tile_prob = feather.read_dataframe(args.tileProbFile)

tile_prob['imageIDs'] = test_images['imageIDs'].to_numpy()
tile_prob['L0path'] = test_images['L0path'].to_numpy()
tile_prob['L1path'] = test_images['L1path'].to_numpy()
tile_prob['L2path'] = test_images['L2path'].to_numpy()

tile_prob_subset = tile_prob.loc[tile_prob['imageIDs'] == args.imageID]



im = slide_PIL[0].copy()
PIL.Image.MAX_IMAGE_PIXELS = 4294967295 


colors = ['#FFFFCC',"#fff1b3","#ffea94","#FED976","#FEB24C","#FD8D3C","#FC4E2A","#E31A1C","#BD0026","#800026",'#800026']
draw = ImageDraw.Draw(im)
# temp = tile_prob_subset.sort_values(by=[str(outcome)],ascending=False)[1:int(tile_prob_subset.shape[0]*0.1)]
temp = tile_prob_subset
for rowI in range(temp.shape[0]):
    prob = temp.iloc[rowI,args.outcomeIndex]
    color = colors[math.floor(prob/0.1)]
    if temp.iloc[rowI,args.outcomeIndex]>=0: #previously 0.99
        coordinate = temp.iloc[rowI]['L0path']
        x = int(coordinate.split("/")[-1].split('-')[1])
        y = int(coordinate.split("/")[-1].split('-')[3][:-4])
#         draw.rectangle(xy=[x,y,(x+500),(y+500)],outline='red',fill=None)
        draw.rectangle(width=5,xy=[x/args.scaleFactor,y/args.scaleFactor,(x+500)/args.scaleFactor,(y+500)/args.scaleFactor],outline=color,fill=None)

im.save(args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-annotated.tiff',format='TIFF')

os.system('/gpfs/data/proteomics/home/jw4359/software/vips-8.10.6/bin/vips im_vips2tiff '+args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-annotated.tiff ' +args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-annotated-deepzoom.tiff:jpeg:100,tile:256x256,pyramid')

os.system('rm '+args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-annotated.tiff')


###For generating actual heatmaps for outcomeIndex
colors = ['#FFFFCC',"#fff1b3","#ffea94","#FED976","#FEB24C","#FD8D3C","#FC4E2A","#E31A1C","#BD0026","#800026",'#800026']
im = slide_PIL[0].copy()
draw = ImageDraw.Draw(im)
# temp = tile_prob_subset.sort_values(by=[str(outcome)],ascending=False)[1:int(tile_prob_subset.shape[0]*0.1)]
temp = tile_prob_subset
for rowI in range(temp.shape[0]):
    prob = temp.iloc[rowI,args.outcomeIndex]
    color = colors[math.floor(prob/0.1)]
    if temp.iloc[rowI,args.outcomeIndex]>=0: #previously 0.99
        coordinate = temp.iloc[rowI]['L0path']
        x = int(coordinate.split("/")[-1].split('-')[1])
        y = int(coordinate.split("/")[-1].split('-')[3][:-4])
#         draw.rectangle(xy=[x,y,(x+500),(y+500)],outline='red',fill=None)
        draw.rectangle(width=5,xy=[x/args.scaleFactor,y/args.scaleFactor,(x+500)/args.scaleFactor,(y+500)/args.scaleFactor],outline=color,fill=color)

im.save(args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-summary.jpg',format='JPEG',quality=30)



###For generating outline based on class. i.e. for each tile, which class won?
# colors = ['#e377c2','#ff7f0e','#00008b','#818081','#902020','#41e0d1','#f4f5dd','#018081','#9566bd','#ff0101']
# im = slide_PIL[0].copy()
# draw = ImageDraw.Draw(im)
# # temp = tile_prob_subset.sort_values(by=[str(outcome)],ascending=False)[1:int(tile_prob_subset.shape[0]*0.1)]
# temp = tile_prob_subset
# for rowI in range(temp.shape[0]):
#     # prob = temp.iloc[rowI,0:10].astype('float64')
#     prob = temp.iloc[rowI,0:2].astype('float64')
#     color = colors[int(prob.argmax())]
#     if temp.iloc[rowI,args.outcomeIndex]>=0: #previously 0.99
#         coordinate = temp.iloc[rowI]['L0path']
#         x = int(coordinate.split("/")[-1].split('-')[1])
#         y = int(coordinate.split("/")[-1].split('-')[3][:-4])
# #         draw.rectangle(xy=[x,y,(x+500),(y+500)],outline='red',fill=None)
#         draw.rectangle(width=5,xy=[x/args.scaleFactor,y/args.scaleFactor,(x+500)/args.scaleFactor,(y+500)/args.scaleFactor],outline=color,fill=None)
# im.save(args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-cancerType-annotated.tiff',format='TIFF')

# os.system('/gpfs/data/proteomics/home/jw4359/software/vips-8.10.6/bin/vips im_vips2tiff '+args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-cancerType-annotated.tiff ' +args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-cancerType-annotated-deepzoom.tiff:jpeg:100,tile:256x256,pyramid')

# os.system('rm '+args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-cancerType-annotated.tiff')


###For generating heatmaps based on class. i.e. for each box, which class won?
colors = ['#e377c2','#ff7f0e','#00008b','#818081','#902020','#41e0d1','#f4f5dd','#018081','#9566bd','#ff0101']
im = slide_PIL[0].copy()
draw = ImageDraw.Draw(im)
# temp = tile_prob_subset.sort_values(by=[str(outcome)],ascending=False)[1:int(tile_prob_subset.shape[0]*0.1)]
temp = tile_prob_subset
for rowI in range(temp.shape[0]):
    # prob = temp.iloc[rowI,0:10].astype('float64')
    prob = temp.iloc[rowI,0:2].astype('float64')
    color = colors[int(prob.argmax())]
    if temp.iloc[rowI,args.outcomeIndex]>=0: #previously 0.99
        coordinate = temp.iloc[rowI]['L0path']
        x = int(coordinate.split("/")[-1].split('-')[1])
        y = int(coordinate.split("/")[-1].split('-')[3][:-4])
#         draw.rectangle(xy=[x,y,(x+500),(y+500)],outline='red',fill=None)
        draw.rectangle(width=5,xy=[x/args.scaleFactor,y/args.scaleFactor,(x+500)/args.scaleFactor,(y+500)/args.scaleFactor],outline=color,fill=color)

im.save(args.outDir+'/'+args.originalSlideFile.split('/')[-1][:-4]+'-cancerType-summary.jpg',format='JPEG',quality=10)