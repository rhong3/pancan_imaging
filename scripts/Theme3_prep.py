# Preparation for Theme3 Cell of Origin using Panoptes
import pandas as pd

train = pd.read_csv('../Theme3/train.csv', header=0)
validation = pd.read_csv('../Theme3/val.csv', header=0)
test = pd.read_csv('../Theme3/test.csv', header=0)

cancer_dict = {'HNSCC': 0, 'CCRCC': 1, 'CO': 2, 'BRCA': 3, 'LUAD': 4, 'LSCC': 5, 'PDA': 6, 'UCEC': 7, 'GBM': 8, 'OV': 9}

train['set'] = 'train'
validation['set'] = 'validation'
test['set'] = 'test'

origin = pd.concat([train, validation, test])
origin.columns = ['Tumor', 'Patient_ID', 'Slide_ID', 'set']
origin['label'] = origin['Tumor'].replace(cancer_dict)
pathls = []
for idx, row in origin.iterrows():
    pathls.append("../tiles/{}/{}/{}/".format(str(row['Tumor']), str(row['Patient_ID']),
                                                          row['Slide_ID'].split('-')[-1]))
origin['path'] = pathls

origin.to_csv('../Theme3_split.csv', index=False)

