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

# Merge dataframes to create label files
images = pd.read_csv('../cohort.csv')
images['Tumor_normal'] = images['Specimen_Type'].replace({'tumor_tissue': 1, 'normal_tissue': 0})
images = images.drop_duplicates()
images.to_csv('../tumor_label.csv', index=False)
br = pd.read_csv('../clinical/breast_clincial.csv', usecols=['Patient_ID', 'Stage'])
br['type'] = 'BRCA'
cc = pd.read_csv('../clinical/ccrcc_clincial.csv', usecols=['Patient_ID', 'Stage'])
cc['type'] = 'CCRCC'
co = pd.read_csv('../clinical/colon_clincial.csv', usecols=['Patient_ID', 'Stage'])
co['type'] = 'CO'
en = pd.read_csv('../clinical/endometrial_clincial.csv', usecols=['Patient_ID', 'Stage'])
en['type'] = 'UCEC'
gbm = pd.read_csv('../clinical/gbm_clincial.csv', usecols=['Patient_ID', 'Stage'])
gbm['type'] = 'GBM'
hn = pd.read_csv('../clinical/headneck_clincial.csv', usecols=['Patient_ID', 'Stage'])
hn['type'] = 'HNSCC'
ls = pd.read_csv('../clinical/lscc_clincial.csv', usecols=['Patient_ID', 'Stage'])
ls['type'] = 'LSCC'
lu = pd.read_csv('../clinical/luad_clincial.csv', usecols=['Patient_ID', 'Stage'])
lu['type'] = 'LUAD'
ov = pd.read_csv('../clinical/ovarian_clincial.csv', usecols=['Patient_ID', 'Stage'])
ov['type'] = 'OV'
pa = pd.read_csv('../clinical/pancreatic_clinical.csv', usecols=['Patient_ID', 'Stage'])
pa['type'] = 'PDA'

meta = pd.concat([br, cc, co, en, gbm, hn, ls, lu, ov, pa], axis=0)
meta = meta.reset_index()
meta = meta.drop(['index'], axis=1)
meta = meta.drop_duplicates()

joint = images.join(meta.set_index('Patient_ID'), on='Patient_ID', how='inner')
joint = joint.drop_duplicates()
joint['label'] = joint['Tumor_normal']*joint['Stage']
joint = joint.drop_duplicates()
joint = joint[joint['label'].notnull()]
joint.to_csv('../stage_label.csv', index=False)

imlist = images['Patient_ID'].tolist()
metalist = meta['Patient_ID'].tolist()
has_img = []
for idx, row in meta.iterrows():
    if row['Patient_ID'] in imlist:
        has_img.append(1)
    else:
        has_img.append(0)

meta['has_image'] = has_img

meta.to_csv('../meta_cohort.csv', index=False)

in_proteomics = []
for idx, row in images.iterrows():
    if row['Patient_ID'] in metalist:
        in_proteomics.append(1)
    else:
        in_proteomics.append(0)

images['in_proteomics'] = in_proteomics

images.to_csv('../cohort.csv', index=False)
