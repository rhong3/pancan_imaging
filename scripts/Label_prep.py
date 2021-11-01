import pandas as pd
import numpy as np
import os

# # Chrm8q
# brca = pd.read_csv('../Chrm8q/brca_has_event.tsv', header=0, sep='\t')
# brca['Tumor'] = 'BRCA'
# hn = pd.read_csv('../Chrm8q/hnscc_has_event.tsv', header=0, sep='\t')
# hn['Tumor'] = 'HNSCC'
# ov = pd.read_csv('../Chrm8q/ovarian_has_event.tsv', header=0, sep='\t')
# ov['Tumor'] = 'OV'
# luad = pd.read_csv('../Chrm8q/luad_has_event.tsv', header=0, sep='\t')
# luad['Tumor'] = 'LUAD'
# lscc = pd.read_csv('../Chrm8q/lscc_has_event.tsv', header=0, sep='\t')
# lscc['Tumor'] = 'LSCC'
# co = pd.read_csv('../Chrm8q/colon_has_event.tsv', header=0, sep='\t')
# co['Tumor'] = 'CO'
#
# summ = pd.concat([brca, hn, ov, luad, lscc, co], axis=0)
#
# summ['8q_gain_event'] = summ['8q_gain_event'].astype(np.uint8)
# summ['8p_loss_event'] = summ['8p_loss_event'].astype(np.uint8)
#
# df_case = []
# for i in os.listdir('../Case_ID/'):
#     try:
#         for j in os.listdir('../Case_ID/'+i):
#             pdd = pd.read_csv('../Case_ID/'+i+'/'+j, sep='\t')
#             df_case.extend(pdd['CASE_ID'].tolist())
#     except NotADirectoryError:
#         print(i)
#         pass
#
# summ.columns = ['Patient_ID', '8q_gain_event', '8p_loss_event', 'Tumor']
# summ['Patient_ID'] = summ['Patient_ID'].str.replace('X', '')
# summ['8_change_event'] = ((summ['8q_gain_event']+summ['8p_loss_event']) > 0).astype(np.uint8)
#
# tumor = pd.read_csv('../tumor_label.csv', header=0, usecols=['Patient_ID', 'Slide_ID', 'Tumor_normal'])
# tumor = tumor[tumor['Tumor_normal'] == 1]
# tumor = tumor.drop(columns=['Tumor_normal'])
# summ = summ.join(tumor.set_index('Patient_ID'), on='Patient_ID', how='left')
# summ = summ.dropna()
# summ = summ[['Slide_ID', 'Patient_ID', 'Tumor', '8q_gain_event', '8p_loss_event', '8_change_event']]
#
# summ.to_csv('../Chrm8q_label.csv', index=False)
# summ_df = summ[summ['Patient_ID'].isin(df_case)]
# summ_df.to_csv('../Chrm8q_label_df.csv', index=False)
#

# ICA labels
# ic = pd.read_csv('../IC_1QT_raw.csv', header=0)
# tumor = pd.read_csv('../tumor_label_df.csv', header=0, usecols=['Patient_ID', 'Slide_ID', 'Tumor_normal'])
# tumor = tumor[tumor['Tumor_normal'] == 1]
# tumor = tumor.drop(columns=['Tumor_normal'])
#
# ic = ic.join(tumor.set_index('Patient_ID'), on='Patient_ID', how='left')
# ic = ic.dropna()
# ic = ic[['Slide_ID', 'Patient_ID', 'Tumor', 'ic_001_q75', 'ic_005_q75', 'ic_013_q75',
#        'ic_031_q75', 'ic_039_q75']]
# ic.to_csv('../IC_1QT_label.csv', index=False)

# Vas cluster scores label
protein = pd.read_csv('../Theme5/Final_Protein_method_gsva4.csv', header=0,
                      usecols=['Protein_Cluster_10', 'Protein_Cluster_11',
       'Protein_Cluster_12', 'Protein_Cluster_13', 'Protein_Cluster_14',
       'Protein_Cluster_15', 'Protein_Cluster_16', 'Protein_Cluster_17',
       'Protein_Cluster_18', 'Protein_Cluster_19', 'Protein_Cluster_2',
       'Protein_Cluster_20', 'Protein_Cluster_21', 'Protein_Cluster_3',
       'Protein_Cluster_4', 'Protein_Cluster_5', 'Protein_Cluster_6',
       'Protein_Cluster_7', 'Protein_Cluster_8', 'Protein_Cluster_9', 'Pat_ID'])
protein.columns = ['Protein_10', 'Protein_11',
       'Protein_12', 'Protein_13', 'Protein_4',
       'Protein_15', 'Protein_16', 'Protein_17',
       'Protein_18', 'Protein_19', 'Protein_2',
       'Protein_20', 'Protein_21', 'Protein_3',
       'Protein_4', 'Protein_5', 'Protein_6',
       'Protein_7', 'Protein_8', 'Protein_9', 'Patient_ID']
for i in ['Protein_10', 'Protein_11',
       'Protein_12', 'Protein_13', 'Protein_4',
       'Protein_15', 'Protein_16', 'Protein_17',
       'Protein_18', 'Protein_19', 'Protein_2',
       'Protein_20', 'Protein_21', 'Protein_3',
       'Protein_4', 'Protein_5', 'Protein_6',
       'Protein_7', 'Protein_8', 'Protein_9']:
       protein[i] = (protein[i] > 0).astype('uint8')

RNA = pd.read_csv('../Theme5/Final_RNA_method_gsva4.csv', header=0,
                  usecols=['RNA_Cluster_10', 'RNA_Cluster_11', 'RNA_Cluster_12',
       'RNA_Cluster_13', 'RNA_Cluster_14', 'RNA_Cluster_15', 'RNA_Cluster_16',
       'RNA_Cluster_17', 'RNA_Cluster_18', 'RNA_Cluster_19', 'RNA_Cluster_2',
       'RNA_Cluster_20', 'RNA_Cluster_21', 'RNA_Cluster_3', 'RNA_Cluster_4',
       'RNA_Cluster_5', 'RNA_Cluster_6', 'RNA_Cluster_7', 'RNA_Cluster_8',
       'RNA_Cluster_9', 'Pat_ID'])
RNA.columns = ['RNA_10', 'RNA_11', 'RNA_12',
       'RNA_13', 'RNA_14', 'RNA_15', 'RNA_16',
       'RNA_17', 'RNA_18', 'RNA_19', 'RNA_2',
       'RNA_20', 'RNA_21', 'RNA_3', 'RNA_4',
       'RNA_5', 'RNA_6', 'RNA_7', 'RNA_8',
       'RNA_9', 'Patient_ID']
for j in ['RNA_10', 'RNA_11', 'RNA_12',
       'RNA_13', 'RNA_14', 'RNA_15', 'RNA_16',
       'RNA_17', 'RNA_18', 'RNA_19', 'RNA_2',
       'RNA_20', 'RNA_21', 'RNA_3', 'RNA_4',
       'RNA_5', 'RNA_6', 'RNA_7', 'RNA_8',
       'RNA_9']:
       RNA[j] = (RNA[j] > 0).astype('uint8')

tumor = pd.read_csv('../tumor_label_df.csv', header=0, usecols=['Patient_ID', 'Slide_ID', 'Tumor_normal', 'Tumor'])
tumor = tumor[tumor['Tumor_normal'] == 1]
tumor = tumor.drop(columns=['Tumor_normal'])

cb = protein.join(tumor.set_index('Patient_ID'), on='Patient_ID', how='left')
cb = cb.join(RNA.set_index('Patient_ID'), on='Patient_ID', how='left')

cb = cb[['Patient_ID', 'Slide_ID', 'Tumor', 'Protein_10', 'Protein_11', 'Protein_12', 'Protein_13', 'Protein_4',
       'Protein_15', 'Protein_16', 'Protein_17', 'Protein_18', 'Protein_19',
       'Protein_2', 'Protein_20', 'Protein_21', 'Protein_3', 'Protein_4',
       'Protein_5', 'Protein_6', 'Protein_7', 'Protein_8', 'Protein_9',
       'RNA_10', 'RNA_11', 'RNA_12',
       'RNA_13', 'RNA_14', 'RNA_15', 'RNA_16', 'RNA_17', 'RNA_18', 'RNA_19',
       'RNA_2', 'RNA_20', 'RNA_21', 'RNA_3', 'RNA_4', 'RNA_5', 'RNA_6',
       'RNA_7', 'RNA_8', 'RNA_9']]
cb = cb.dropna()
cb.to_csv('../protein_RNA_cluster_label.csv', index=False)

