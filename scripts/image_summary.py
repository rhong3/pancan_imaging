# Image summary
import pandas as pd
import os

type_patient = []
patient_slide = []
slide_tiles = []

for type in os.listdir('../tiles/'):
    patient_num = len(os.listdir('../tiles/' + type)) - 1
    type_patient.append([type, patient_num])
    for patient in os.listdir('../tiles/'+type):
        if patient == 'sum.csv':
            pass
        else:
            slide_num = len(os.listdir('../tiles/' + type + '/' + patient))
            patient_slide.append([type, patient, slide_num])
            for slide in os.listdir('../tiles/'+type+'/'+patient):
                try:
                   level1_num = len(os.listdir('../tiles/'+type+'/'+patient+'/'+slide+'/level1'))-1
                except Exception as err:
                   print(err)
                   print('../tiles/'+type+'/'+patient+'/'+slide+'/level1')
                   level1_num = 0
                try:
                   level2_num = len(os.listdir('../tiles/' + type + '/' + patient + '/' + slide + '/level2')) - 1
                except Exception as err:
                   print(err)
                   print('../tiles/' + type + '/' + patient + '/' + slide + '/level2')
                   level2_num = 0
                try:
                   level3_num = len(os.listdir('../tiles/' + type + '/' + patient + '/' + slide + '/level3')) - 1
                except Exception as err:
                   print(err)
                   print('../tiles/' + type + '/' + patient + '/' + slide + '/level3')
                   level3_num = 0
                slide_tiles.append([type, patient, str(patient+'-'+slide), level1_num, level2_num, level3_num])

dff = pd.read_csv('../tumor_label_df.csv', header=0, usecols=['Patient_ID', 'Slide_ID', 'Tumor_normal'])
dff.columns = ['patient', 'slide', 'Tumor_normal']
df_patient = dff['patient'].tolist()

ps_pd = pd.DataFrame(patient_slide, columns=['type', 'patient', 'slide_count'])
ps_pd.to_csv('../slide_summary.csv', index=False)
ps_pd_df = ps_pd[ps_pd['patient'].isin(df_patient)]
ps_pd_df.to_csv('../slide_summary_df.csv', index=False)

st_pd = pd.DataFrame(slide_tiles, columns=['type', 'patient', 'slide', 'level1_count', 'level2_count', 'level3_count'])
st_pd.to_csv('../tiles_summary.csv', index=False)
st_pd_df = st_pd[st_pd['patient'].isin(df_patient)]
st_pd_df.to_csv('../tiles_summary_df.csv', index=False)

tp_pd = pd.DataFrame(type_patient, columns=['type', 'patient_count'])
dfct = []
for tp in tp_pd['type'].unique().tolist():
    dfct.append(len(ps_pd_df[ps_pd_df['type'] == tp].patient.unique().tolist()))
tp_pd['df_patient_count'] = dfct
tp_pd.to_csv('../patient_summary.csv', index=False)

