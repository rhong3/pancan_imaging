import pandas as pd

cancer = ['CCRCC', 'UCEC', 'LUAD', 'LSCC', 'HNSCC', 'PDA']
for i in cancer:
    tsne = pd.read_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/For_tSNE.csv".format(i), header=0)
    tsne.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/For_tSNE_all_cancer.csv".format(i), index=False)
    tsne = tsne[tsne['Tumor'] == 'UCEC']
    tsne.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/For_tSNE_full.csv".format(i), index=False)
    tsne_lt = tsne.sample(30000, replace=False)
    tsne_lt.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/For_tSNE.csv".format(i),
                index=False)
    sl_out = pd.read_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/Test_slide.csv".format(i), header=0)
    sl_out.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/Test_slide_all_cancer.csv".format(i), index=False)
    sl_out = sl_out[sl_out['Tumor'] == 'UCEC']
    sl_out.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/Test_slide.csv".format(i), index=False)

    tl_out = pd.read_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/Test_tile.csv".format(i), header=0)
    tl_out.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/Test_tile_all_cancer.csv".format(i),
                  index=False)
    tl_out = tl_out[tl_out['Tumor'] == 'UCEC']
    tl_out.to_csv("/gpfs/scratch/rh2740/pancan_imaging/Results/Tumor_{}_on_UCEC_CCA/out/Test_tile.csv".format(i),
                  index=False)

