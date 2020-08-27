# Processing CPTAC2 Data
import pandas as pd

imgdf = pd.read_excel('../CPTAC II Images to TCIA.xlsx')
brbl = pd.read_excel('../clinical/Breast Baseline Clinical Data_20160927_MT.xls')
broy = pd.read_excel('../clinical/Breast One Year Clinical Data_20160927_MT.xls')
ovbl = pd.read_excel('../clinical/Ovary Baseline Clinical Data_20160927_MT.xls')
ovoy = pd.read_excel('../clinical/Ovary One Year Clinical Data_20160927_MT.xls')
cobl = pd.read_excel('../clinical/Colon Baseline Clinical Data_20160927_MT.xls')
cooy = pd.read_excel('../clinical/Colon One Year Clinical Data_20160927_MT.xls')

brbl = brbl.drop(['CPTAC Case ID', 'CRF Name'], axis=1)
PID = brbl['Participant ID'].unique().tolist()

for i in PID:
    brbl[brbl['Participant ID'] == i] = brbl[brbl['Participant ID'] == i].fillna(method='bfill')
    brbl[brbl['Participant ID'] == i] = brbl[brbl['Participant ID'] == i].fillna(method='ffill')

brbl = brbl.drop_duplicates()

brbl.to_csv('../test.csv', index=False)

