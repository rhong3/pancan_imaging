# Processing CPTAC2 Data
import pandas as pd
import numpy as np
import os


def combine(pdin):
    pdin = pdin.drop(['CPTAC Case ID', 'CRF Name'], axis=1)
    PID = pdin['Participant ID'].unique().tolist()
    for i in PID:
        pdin[pdin['Participant ID'] == i] = pdin[pdin['Participant ID'] == i].fillna(method='bfill')
        pdin[pdin['Participant ID'] == i] = pdin[pdin['Participant ID'] == i].fillna(method='ffill')
    pdout = pdin.drop_duplicates()
    return pdout


# brbl = pd.read_excel('../clinical/Breast Baseline Clinical Data_20160927_MT.xls')
# ovbl = pd.read_excel('../clinical/Ovary Baseline Clinical Data_20160927_MT.xls')
# cobl = pd.read_excel('../clinical/Colon Baseline Clinical Data_20160927_MT.xls')
#
# brbl = combine(brbl)
# brbl['Stage'] = brbl['Stage (The patient must be Stage IIA-IIIC to be included in the CPTAC study. )'].copy()
# brbl['Stage'] = brbl['Stage'].str.replace('Stage ', '')
# brbl['Stage'] = brbl['Stage'].str.replace('Not Performed', '')
# brbl['Stage'] = brbl['Stage'].str.replace('A', '')
# brbl['Stage'] = brbl['Stage'].str.replace('B', '')
# brbl['Stage'] = brbl['Stage'].str.replace('C', '')
# brbl['Stage'] = brbl['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# brbl.columns = brbl.columns.str.replace('Participant ID', 'Patient_ID')
# brbl.to_csv('../clinical/breast_full.csv', index=False)
#
# ovbl = combine(ovbl)
# ovbl['Stage'] = ovbl['Tumor Stage (Pathological) Ovary FIGO Staging System'].copy()
# ovbl['Stage'] = ovbl['Stage'].str.replace('Not Reported/ Unknown', '')
# ovbl['Stage'] = ovbl['Stage'].str.replace('A', '')
# ovbl['Stage'] = ovbl['Stage'].str.replace('B', '')
# ovbl['Stage'] = ovbl['Stage'].str.replace('C', '')
# ovbl['Stage'] = ovbl['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# ovbl.columns = ovbl.columns.str.replace('Participant ID', 'Patient_ID')
# ovbl.to_csv('../clinical/ovarian_full.csv', index=False)
#
# cobl = combine(cobl)
# cobl['Stage'] = cobl['Tumor Stage (Pathological)'].copy()
# cobl['Stage'] = cobl['Stage'].str.replace('Stage', '')
# cobl['Stage'] = cobl['Stage'].str.replace(' ', '')
# cobl['Stage'] = cobl['Stage'].str.replace('A', '')
# cobl['Stage'] = cobl['Stage'].str.replace('B', '')
# cobl['Stage'] = cobl['Stage'].str.replace('C', '')
# cobl['Stage'] = cobl['Stage'].replace({'IV': 4, 'III': 3, 'II': 2, 'I': 1})
# cobl.columns = cobl.columns.str.replace('Participant ID', 'Patient_ID')
# cobl.to_csv('../clinical/colon_full.csv', index=False)

# Concatenate to image DF
# imgdf = pd.read_excel('../CPTAC II Images to TCIA.xlsx')
# imgdf.columns = imgdf.columns.str.replace('Subject ID', 'Patient_ID')
# brbl = pd.read_csv('../clinical/breast_full.csv', usecols=['Patient_ID', 'Stage'])
# brbl['type'] = 'BRCA'
# ovbl = pd.read_csv('../clinical/ovarian_full.csv', usecols=['Patient_ID', 'Stage'])
# ovbl['type'] = 'OV'
# cobl = pd.read_csv('../clinical/colon_full.csv', usecols=['Patient_ID', 'Stage'])
# cobl['type'] = 'CO'
#
# bl = pd.concat([brbl, ovbl, cobl], axis=0)
# imgdf = imgdf.join(bl.set_index('Patient_ID'), on='Patient_ID', how='left')
# imgdf['type'] = imgdf['type'].fillna('no_clinical')
# imgdf.to_csv('../CPTAC2_images.csv', index=False)

# imsum_OV = pd.read_csv('../CPTAC2_images_OV.csv', header=0)
# imsum_OV = imsum_OV[imsum_OV['type'] == 'OV']
# imsum_OV = imsum_OV.drop(columns=['Unnamed: 0'], axis=1)
# imsum_BRCA = pd.read_csv('../CPTAC2_images_BRCA.csv', header=0)
# imsum_BRCA = imsum_BRCA[imsum_BRCA['type'] == 'BRCA']
# imsum_BRCA = imsum_BRCA.drop(columns=['Unnamed: 0'], axis=1)
# imsum_CO = pd.read_csv('../CPTAC2_images_CO.csv', header=0)
# imsum_CO = imsum_CO[imsum_CO['type'] == 'CO']
# imsum_CO = imsum_CO.drop(columns=['Unnamed: 0'], axis=1)
#
# clinical_OV = pd.read_csv('../clinical/ovarian_clincial.csv', header=0)
# clinical_OV = clinical_OV.drop(columns=['Stage'], axis=1)
# clinical_OV['Tumor_normal'] = clinical_OV['Sample_Tumor_Normal']
# clinical_OV['Tumor_normal'] = clinical_OV['Tumor_normal'].replace({'Tumor': 1, 'Normal': 0})
#
# clinical_BRCA = pd.read_csv('../clinical/breast_clincial.csv', header=0)
# clinical_BRCA = clinical_BRCA.drop(columns=['Stage'], axis=1)
# clinical_BRCA['Patient_ID'] = clinical_BRCA['Patient_ID'].str.replace('X', '')
# clinical_BRCA['Replicate_Measurement_IDs'] = clinical_BRCA['Replicate_Measurement_IDs'].str.replace('X', '')
# clinical_BRCA['Tumor_normal'] = clinical_BRCA['Sample_Tumor_Normal']
# clinical_BRCA['Tumor_normal'] = clinical_BRCA['Tumor_normal'].replace({'Tumor': 1, 'Normal': 0})
#
# clinical_CO = pd.read_csv('../clinical/colon_clincial.csv', header=0)
# clinical_CO = clinical_CO.drop(columns=['Stage'], axis=1)
# clinical_CO['Tumor_normal'] = clinical_CO['Sample_Tumor_Normal']
# clinical_CO['Tumor_normal'] = clinical_CO['Tumor_normal'].replace({'Tumor': 1, 'Normal': 0})
#
#
# OV = imsum_OV.join(clinical_OV.set_index('Patient_ID'), on='Patient_ID', how='left')
# BRCA = imsum_BRCA.join(clinical_BRCA.set_index('Patient_ID'), on='Patient_ID', how='left')
# CO = imsum_CO.join(clinical_CO.set_index('Patient_ID'), on='Patient_ID', how='left')
#
# OV = OV.rename(columns={'Patient_ID': 'Case_ID', 'Specimen ID': 'Specimen_ID', 'type': 'Tumor'})
# CO = CO.rename(columns={'Patient_ID': 'Case_ID', 'Specimen ID': 'Specimen_ID', 'type': 'Tumor'})
# BRCA = BRCA.rename(columns={'Patient_ID': 'Case_ID', 'Specimen ID': 'Specimen_ID', 'type': 'Tumor'})
#
# OVc = pd.read_csv('../Case_ID/OV/Case_ID_OV.tsv', sep='\t')
# OVc = OVc['CASE_ID'].tolist()
# COc = pd.read_csv('../Case_ID/CO/Case_ID_CO.tsv', sep='\t')
# COc = COc['CASE_ID'].tolist()
# BRc = pd.read_csv('../Case_ID/BR/Case_ID_BR.tsv', sep='\t')
# BRc = BRc['CASE_ID'].tolist()
#
# OVx = OV[OV['Case_ID'].isin(OVc)]
# BRCAx = BRCA[BRCA['Case_ID'].isin(BRc)]
# COx = CO[CO['Case_ID'].isin(COc)]

# OVx.to_csv('../data_freeze/OV/OV.tsv', index=False, sep='\t')
# BRCAx.to_csv('../data_freeze/BRCA/BRCA.tsv', index=False, sep='\t')
# COx.to_csv('../data_freeze/CO/CO.tsv', index=False, sep='\t')

# df = pd.read_csv('../data_freeze.tsv', header=0, sep='\t')
# df = pd.concat([df, OVx, COx, BRCAx], axis=0)
# df.to_csv('../data_freeze.tsv', index=False, sep='\t')


# dff = pd.concat([OV, BRCA, CO], axis=0)
#
# dff['Slide_ID'] = dff['Case_ID'].str.cat(dff['Slide_ID'].astype(str), sep='-')
# dff['Slide_ID'] = dff['Slide_ID'].str.replace(".0", "", regex=False)
# dff = dff.rename(columns={'Case_ID': 'Patient_ID'})
#
# tumor = pd.read_csv('../tumor_label.csv', header=0)
# tumor = pd.concat([tumor, dff], axis=0)
# tumor = tumor.dropna(subset=['Tumor_normal'])
# tumor.to_csv('../tumor_label.csv', index=False)
#
# dff['label'] = dff['Stage']*dff['Tumor_normal']
# stage = pd.read_csv('../stage_label.csv', header=0)
# stage = pd.concat([stage, dff], axis=0)
# stage = stage.dropna(subset=['label'])
# stage.to_csv('../stage_label.csv', index=False)

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

# tumor = pd.read_csv('../tumor_label.csv', header=0)
# stage = pd.read_csv('../stage_label.csv', header=0)
#
# tumor.drop_duplicates(subset='Slide_ID', inplace=True)
# stage.drop_duplicates(subset='Slide_ID', inplace=True)
#
# tumor.to_csv('../tumor_label.csv', index=False)
# stage.to_csv('../stage_label.csv', index=False)

# tumor = pd.read_csv('../tumor_label.csv', header=0)
# stage = pd.read_csv('../stage_label.csv', header=0)
#
# tumor_df = tumor[tumor['Patient_ID'].isin(df_case)]
# stage_df = stage[stage['Patient_ID'].isin(df_case)]
#
# tumor_df.to_csv('../tumor_label_df.csv', index=False)
# stage_df.to_csv('../stage_label_df.csv', index=False)
#
# print(len(tumor_df[tumor_df['Tumor']=='CO'].Patient_ID.unique()))

# ims = pd.read_csv('../CPTAC2_images.csv', header=0)
# print(len(ims[ims['type'] == 'CO'].Patient_ID.unique()))

dff = pd.read_csv('../tumor_label_df.csv', header=0)
print(len(dff[(dff['Tumor'] == 'BRCA') & (dff['Tumor_normal'] == 1)].Patient_ID.unique()))
