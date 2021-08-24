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

