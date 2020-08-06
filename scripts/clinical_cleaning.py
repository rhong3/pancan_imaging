# Clean clinical dataframes
import pandas as pd
import numpy

# # brca
# br = pd.read_csv('../clinical/breast_clincial.csv')
# br['Stage-original'] = br['Stage']
# br['Stage'] = br['Stage'].str.replace('Stage ', '')
# br['Stage'] = br['Stage'].str.replace('A', '')
# br['Stage'] = br['Stage'].str.replace('B', '')
# br['Stage'] = br['Stage'].str.replace('C', '')
# br['Stage'] = br['Stage'].replace({'III': 3, 'II': 2, 'I': 1})
# br.to_csv('../clinical/breast_clincial.csv', index=False)
#
# # ccrcc
# cc = pd.read_csv('../clinical/ccrcc_clincial.csv')
# cc['Patient_ID'] = cc['Patient_ID'].str.split('.').str[0]
# cc['Stage'] = cc['tumor_stage_pathological']
# cc['Stage'] = cc['Stage'].str.replace('Stage ', '')
# cc['Stage'] = cc['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# cc.to_csv('../clinical/ccrcc_clincial.csv', index=False)
#
# # colon
# co = pd.read_csv('../clinical/colon_clincial.csv')
# co['Patient_ID'] = co['Patient_ID'].str.split('.').str[0]
# co['Stage-original'] = co['Stage']
# co['Stage'] = co['Stage'].str.replace('Stage ', '')
# co['Stage'] = co['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# co.to_csv('../clinical/colon_clincial.csv', index=False)
#
# # endometrial
# en = pd.read_csv('../clinical/endometrial_clincial.csv')
# en['Patient_ID'] = en['Patient_ID'].str.split('.').str[0]
# en['Stage'] = en['tumor_Stage-Pathological']
# en['Stage'] = en['Stage'].str.replace('Stage ', '')
# en['Stage'] = en['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# en.to_csv('../clinical/endometrial_clincial.csv', index=False)

# # gbm
# gbm = pd.read_csv('../clinical/gbm_clincial.csv')
# gbm['Patient_ID'] = gbm['Patient_ID'].str.split('.').str[0]
# gbm['Stage-original'] = gbm['Stage']
# gbm['Stage'] = gbm['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# gbm.to_csv('../clinical/gbm_clincial.csv', index=False)

# # hn
# hn = pd.read_csv('../clinical/headneck_clincial.csv')
# hn['Patient_ID'] = hn['Patient_ID'].str.split('.').str[0]
# hn['Stage'] = hn['patho_staging_curated']
# hn['Stage'] = hn['Stage'].str.replace('Stage ', '')
# hn['Stage'] = hn['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# hn.to_csv('../clinical/headneck_clincial.csv', index=False)

# # lscc
# ls = pd.read_csv('../clinical/lscc_clincial.csv')
# ls['Patient_ID'] = ls['Patient_ID'].str.split('.').str[0]
# ls['Stage-original'] = ls['Stage']
# ls['Stage'] = ls['Stage'].str.replace('A', '')
# ls['Stage'] = ls['Stage'].str.replace('B', '')
# ls['Stage'] = ls['Stage'].str.replace('C', '')
# ls['Stage'] = ls['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# ls.to_csv('../clinical/lscc_clincial.csv', index=False)

# # luad
# lu = pd.read_csv('../clinical/luad_clincial.csv')
# lu['Patient_ID'] = lu['Patient_ID'].str.split('.').str[0]
# lu['Stage-original'] = lu['Stage']
# lu['Stage'] = lu['Stage'].str.replace('A', '')
# lu['Stage'] = lu['Stage'].str.replace('B', '')
# lu['Stage'] = lu['Stage'].str.replace('C', '')
# lu['Stage'] = lu['Stage'].replace({'4': 4, '3': 3, '2': 2, '1': 1})
# lu.to_csv('../clinical/luad_clincial.csv', index=False)

# # ovarian
# ov = pd.read_csv('../clinical/ovarian_clincial.csv')
# ov['Patient_ID'] = ov['Patient_ID'].str.split('.').str[0]
# ov['Stage'] = ov['Tumor_Stage_Ovary_FIGO']
# ov['Stage'] = ov['Stage'].str.replace('Not Reported/ Unknown', '')
# ov['Stage'] = ov['Stage'].str.replace('A', '')
# ov['Stage'] = ov['Stage'].str.replace('B', '')
# ov['Stage'] = ov['Stage'].str.replace('C', '')
# ov['Stage'] = ov['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# ov.to_csv('../clinical/ovarian_clincial.csv', index=False)

# # pancreatic
# pa = pd.read_csv('../clinical/pancreatic_clinical.csv')
# pa['Stage'] = pa['tumor_stage_pathological']
# pa['Stage'] = pa['Stage'].str.replace('Stage ', '')
# pa['Stage'] = pa['Stage'].str.replace('NA', '')
# pa['Stage'] = pa['Stage'].str.replace('A', '')
# pa['Stage'] = pa['Stage'].str.replace('B', '')
# pa['Stage'] = pa['Stage'].str.replace('C', '')
# pa['Stage'] = pa['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# pa.to_csv('../clinical/pancreatic_clinical.csv', index=False)

