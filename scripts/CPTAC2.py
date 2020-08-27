# Processing CPTAC2 Data
import pandas as pd


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
imgdf = pd.read_excel('../CPTAC II Images to TCIA.xlsx')
imgdf.columns = imgdf.columns.str.replace('Subject ID', 'Patient_ID')
brbl = pd.read_csv('../clinical/breast_full.csv', usecols=['Patient_ID', 'Stage'])
brbl['type'] = 'BRCA'
ovbl = pd.read_csv('../clinical/ovarian_full.csv', usecols=['Patient_ID', 'Stage'])
ovbl['type'] = 'OV'
cobl = pd.read_csv('../clinical/colon_full.csv', usecols=['Patient_ID', 'Stage'])
cobl['type'] = 'CO'

bl = pd.concat([brbl, ovbl, cobl], axis=0)
imgdf = imgdf.join(bl.set_index('Patient_ID'), on='Patient_ID', how='left')
imgdf['type'] = imgdf['type'].fillna('no_clinical')
imgdf.to_csv('../CPTAC2_images.csv', index=False)

