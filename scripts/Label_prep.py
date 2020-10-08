import pandas as pd
import numpy as np
import os

# Chrm8q
brca = pd.read_csv('../Chrm8q/brca_has_event.tsv', header=0, sep='\t')
brca['Tumor'] = 'BRCA'
hn = pd.read_csv('../Chrm8q/hnscc_has_event.tsv', header=0, sep='\t')
hn['Tumor'] = 'HNSCC'
ov = pd.read_csv('../Chrm8q/ovarian_has_event.tsv', header=0, sep='\t')
ov['Tumor'] = 'OV'
luad = pd.read_csv('../Chrm8q/luad_has_event.tsv', header=0, sep='\t')
luad['Tumor'] = 'LUAD'
lscc = pd.read_csv('../Chrm8q/lscc_has_event.tsv', header=0, sep='\t')
lscc['Tumor'] = 'LSCC'
co = pd.read_csv('../Chrm8q/colon_has_event.tsv', header=0, sep='\t')
co['Tumor'] = 'CO'

summ = pd.concat([brca, hn, ov, luad, lscc, co], axis=0)

summ['8q_gain_event'] = summ['8q_gain_event'].astype(np.uint8)
summ['8p_loss_event'] = summ['8p_loss_event'].astype(np.uint8)

df_case = []
for i in os.listdir('../Case_ID/'):
    try:
        for j in os.listdir('../Case_ID/'+i):
            pdd = pd.read_csv('../Case_ID/'+i+'/'+j, sep='\t')
            df_case.extend(pdd['CASE_ID'].tolist())
    except NotADirectoryError:
        print(i)
        pass

summ.columns = ['Patient_ID', '8q_gain_event', '8p_loss_event', 'Tumor']
summ['8_change_event'] = ((summ['8q_gain_event']+summ['8p_loss_event']) > 0).astype(np.uint8)
summ.to_csv('../Chrm8q_label.csv', index=False)

summ_df = summ[summ['Patient_ID'].isin(df_case)]
summ_df.to_csv('../Chrm8q_label_df.csv', index=False)
