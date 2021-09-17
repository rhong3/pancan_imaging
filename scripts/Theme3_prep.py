# Preparation for Theme3 Cell of Origin using Panoptes
import pandas as pd

# train = pd.read_csv('../Theme3/train.csv', header=0)
# validation = pd.read_csv('../Theme3/val.csv', header=0)
# test = pd.read_csv('../Theme3/test.csv', header=0)
#
# cancer_dict = {'HNSCC': 0, 'CCRCC': 1, 'CO': 2, 'BRCA': 3, 'LUAD': 4, 'LSCC': 5, 'PDA': 6, 'UCEC': 7, 'GBM': 8, 'OV': 9}
#
# train['set'] = 'train'
# validation['set'] = 'validation'
# test['set'] = 'test'
#
# origin = pd.concat([train, validation, test])
# origin.columns = ['Tumor', 'Patient_ID', 'Slide_ID', 'set']
# origin['label'] = origin['Tumor'].replace(cancer_dict)
# pathls = []
# for idx, row in origin.iterrows():
#     pathls.append("../tiles/{}/{}/{}/".format(str(row['Tumor']), str(row['Patient_ID']),
#                                                           row['Slide_ID'].split('-')[-1]))
# origin['path'] = pathls
#
# origin.to_csv('../Theme3_split.csv', index=False)
#


# DLCCA secondary prep
train = pd.read_csv('../DLCCA/train.csv', header=0)
validation = pd.read_csv('../DLCCA/val.csv', header=0)
test = pd.read_csv('../DLCCA/test.csv', header=0)

train['set'] = 'train'
validation['set'] = 'validation'
test['set'] = 'test'

DLCCA = pd.concat([train, validation, test])
DLCCA.columns = ['Patient_ID', 'Slide_ID', 'Tumor', 'RNA_ID', "grade", "set"]
paths = []
for idx, row in DLCCA.iterrows():
    paths.append(str('../tiles/'+row['Tumor']+'/'+row['Patient_ID']+'/'+row['Slide_ID'].split('-')[-1]+'/'))
DLCCA['path'] = paths
DLCCA.to_csv('../DLCCA/grade.csv', index=False)

DLCCA = DLCCA.drop(['grade'], axis=1)

tumor_normal = pd.read_csv('../tumor_label_df.csv', header=0, usecols=['Slide_ID', 'Tumor_normal'])
tumor_normal = DLCCA.join(tumor_normal.set_index('Slide_ID'), on='Slide_ID', how='inner')
tumor_normal.to_csv('../DLCCA/tumor_normal.csv', index=False)

stage = pd.read_csv('../stage_label_df.csv', header=0, usecols=['Slide_ID', 'label'])
stage.columns = ['Slide_ID', 'Stage']
stage = DLCCA.join(stage.set_index('Slide_ID'), on='Slide_ID', how='inner')
stage.to_csv('../DLCCA/stage.csv', index=False)

mutations = pd.read_csv('../mutation_label.csv', header=0)
mutations = mutations.drop(['Patient_ID', 'Tumor'], axis=1)
mutations = DLCCA.join(mutations.set_index('Slide_ID'), on='Slide_ID', how='inner')
mutations.to_csv('../DLCCA/mutations.csv', index=False)

nuclei = pd.read_csv('../stage_label_df.csv', header=0, usecols=['Slide_ID', 'Percent_Tumor_Nuclei'])
nuclei = nuclei[nuclei['Percent_Tumor_Nuclei'] >= 0]
nuclei = DLCCA.join(nuclei.set_index('Slide_ID'), on='Slide_ID', how='inner')
label = []
for idx, row in nuclei.iterrows():
    if row["Percent_Tumor_Nuclei"] < 50:
        label.append(0)
    elif row["Percent_Tumor_Nuclei"] >= 80:
        label.append(2)
    else:
        label.append(1)
nuclei['label'] = label
nuclei.to_csv('../DLCCA/tumor_nuclei.csv', index=False)

cellularity = pd.read_csv('../stage_label_df.csv', header=0, usecols=['Slide_ID', 'Percent_Total_Cellularity'])
cellularity = cellularity[cellularity['Percent_Total_Cellularity'] >= 0]
cellularity = DLCCA.join(cellularity.set_index('Slide_ID'), on='Slide_ID', how='inner')
label = []
for idx, row in cellularity.iterrows():
    if row["Percent_Total_Cellularity"] < 80:
        label.append(0)
    elif row["Percent_Total_Cellularity"] >= 90:
        label.append(2)
    else:
        label.append(1)
cellularity['label'] = label
cellularity.to_csv('../DLCCA/cellularity.csv', index=False)

necrosis = pd.read_csv('../stage_label_df.csv', header=0, usecols=['Slide_ID', 'Percent_Necrosis'])
necrosis = necrosis[necrosis['Percent_Necrosis'] >= 0]
necrosis = DLCCA.join(necrosis.set_index('Slide_ID'), on='Slide_ID', how='inner')
label = []
for idx, row in necrosis.iterrows():
    if row["Percent_Necrosis"] == 0:
        label.append(0)
    elif row["Percent_Necrosis"] >= 10:
        label.append(2)
    else:
        label.append(1)
necrosis['label'] = label
necrosis.to_csv('../DLCCA/necrosis.csv', index=False)


# # Get common CCA test slides for all tasks
# tumor = pd.read_csv('../Results/tumor_CCA/data/te_sample_raw.csv', header=0)
# tumor = tumor.drop(['Tumor_normal'], axis=1)
#
# stage = pd.read_csv('../Results/stage_CCA/data/te_sample_raw.csv', header=0, usecols=['Slide_ID', 'Stage'])
# TP53 = pd.read_csv('../Results/TP53_CCA/data/te_sample_raw.csv', header=0, usecols=['Slide_ID', 'TP53'])
# nuclei = pd.read_csv('../Results/nuclei_CCA/data/te_sample_raw.csv', header=0, usecols=['Slide_ID', 'Percent_Tumor_Nuclei'])
# necrosis = pd.read_csv('../Results/necrosis_CCA/data/te_sample_raw.csv', header=0, usecols=['Slide_ID', 'Percent_Necrosis'])
# cellularity = pd.read_csv('../Results/cellularity_CCA/data/te_sample_raw.csv', header=0, usecols=['Slide_ID', 'Percent_Total_Cellularity'])
# grade = pd.read_csv('../Results/grade_CCA/data/te_sample_raw.csv', header=0, usecols=['Slide_ID', 'grade'])
#
# for i in [stage, grade, nuclei, necrosis, TP53, cellularity]:
#     tumor = tumor.join(i.set_index('Slide_ID'), on='Slide_ID', how='inner')
#
#
# tumor.to_csv('../CCA_test_raw_common.csv', index=False)