import cv2

# for i in ["Tumor", "TP53", "PTEN", "STK11", "KRAS", "NOTCH1"]:
#     image = cv2.imread("/Users/rh2740/Documents/pancan_imaging/DLCCA/Figures/Figure3-S3/{}/mosaic_0.jpeg".format(i))
#     cv2.imwrite("/Users/rh2740/Documents/pancan_imaging/DLCCA/Figures/TIF/{}.tif".format(i, i), image)


image = cv2.imread("/Users/rh2740/Documents/pancan_imaging/Results/immune/out/mosaic_2.jpeg")
cv2.imwrite("/Users/rh2740/Documents/pancan_imaging/Results/immune/out/mosaic_2.tif", image)

