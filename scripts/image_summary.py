# Image summary
import pandas as pd
import os

type_patient = []
patient_slide = []
slide_tiles = []

for type in os.listdir('../tiles/'):
    for patient in os.listdir('../tiles/'+type):
        patient_num = len(os.listdir('../tiles/'+type))-1
        type_patient.append([type, patient_num])
        if patient == 'sum.csv':
            pass
        else:
           for slide in os.listdir('../tiles/'+type+'/'+patient):
               slide_num = len(os.listdir('../tiles/'+type+'/'+patient))
               patient_slide.append([type, patient, slide_num])
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
               slide_tiles.append([type, patient, slide, level1_num, level2_num, level3_num])

tp_pd = pd.DataFrame(type_patient, columns=['type', 'patient_count'])
tp_pd.to_csv('../patient_summary.csv', index=False)
ps_pd = pd.DataFrame(patient_slide, columns=['type', 'patient', 'slide_count'])
ps_pd.to_csv('../slide_summary.csv', index=False)
st_pd = pd.DataFrame(slide_tiles, columns=['type', 'patient', 'slide', 'level1_count', 'level2_count', 'level3_count'])
st_pd.to_csv('../tiles_summary.csv', index=False)

