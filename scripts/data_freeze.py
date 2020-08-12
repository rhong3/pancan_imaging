# For CPTAC pan cancer data freeze
import pandas as pd
import os

images = pd.read_csv('../cohort_DF.csv')
images = images.drop(['_id', 'Pathology', 'Tumor_normal', 'in_proteomics'], axis=1)

m = 0
for tumor in ['ccRCC', 'UCEC', 'GBM', 'HNSCC', 'LSCC', 'LUAD', 'PDA']:
    if tumor == 'UCEC':
        cases = pd.read_csv('../Case_ID/EC/Case_ID_EC.tsv', sep='\t')
    else:
        cases = pd.read_csv('../Case_ID/{}/Case_ID_{}.tsv'.format(tumor, tumor), sep='\t')
    sh = pd.read_csv('../sh/{}.sh'.format(tumor.lower()), sep=' -LOC - ', names=['c', 'TCIA_url'])
    sh['Slide_ID'] = sh['TCIA_url'].str.split('/',  expand=True)[5].str.split('.', expand=True)[0]
    sh = sh.drop('c', axis=1)

    cohort = images[images['Case_ID'].isin(cases['CASE_ID'].tolist())]
    cohort = cohort.join(sh.set_index('Slide_ID'), on='Slide_ID', how='left')
    try:
        os.mkdir('../data_freeze/{}'.format(tumor))
    except FileExistsError:
        pass
    cohort.to_csv('../data_freeze/{}/{}.tsv'.format(tumor, tumor), sep='\t', index=False)
    if m == 0:
        full = cohort.copy()
    else:
        full = pd.concat([full, cohort], axis=0)
    m = 1

full.to_csv('../data_freeze.tsv'.format(tumor), sep='\t', index=False)
