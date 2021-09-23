"""
get low resolution of images

Created on 09/22/2021

@author: RH
"""
from openslide import OpenSlide
import pandas as pd
import os
import numpy as np
import cv2

out = []
for tm in os.listdir('../images/'):
    for im in os.listdir('../images/'+tm):
        if '.svs' in im:
            level = 0
            ft = 2
            try:
                slide = OpenSlide('../images/' + tm + '/' + im)
            except:
                continue
            bounds_width = slide.level_dimensions[level][0]
            bounds_height = slide.level_dimensions[level][1]
            x = 0
            y = 0
            half_width_region = 49 * ft
            full_width_region = 299 * ft
            stepsize = (full_width_region - half_width_region)

            n_x = int((bounds_width - 1) / stepsize)
            n_y = int((bounds_height - 1) / stepsize)
            name = im.split(".sv")[0]

            out.append([name, tm, bounds_width, bounds_height, n_x, n_y])
            if not os.path.isfile('../lowres/'+name+'.png'):
                try:
                    lowres = slide.read_region((x, y), level + 1, (int(n_x * stepsize / 4), int(n_y * stepsize / 4)))
                    ori_img = np.array(lowres)[:, :, :3]
                    tq = ori_img[:, :, 0]
                    ori_img[:, :, 0] = ori_img[:, :, 2]
                    ori_img[:, :, 2] = tq
                    cv2.imwrite('../lowres/'+name+'.png', ori_img)
                except:
                    continue
outpd = pd.DataFrame(out, columns=['SlideID', 'tumor', 'bounds_width', 'bounds_height', 'n_x', 'n_y'])
outpd.to_csv('../imglowres.csv', index=False)

