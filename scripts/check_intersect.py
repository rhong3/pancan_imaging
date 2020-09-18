# Check for slides that are not in Data freeze; in Data freeze but not in folder
import pandas as pd

df = pd.read_csv('../data_freeze.tsv', header=0, sep='\t')
tile = pd.read_csv('../tiles_summary.csv', header=0)

df_list = df['Slide_ID'].tolist()
tile_not_in = tile[~tile['slide'].isin(df_list)]
tile_not_in.to_csv('../not_DF_tiles_summary.csv', index=False)
tile_in = tile[tile['slide'].isin(df_list)]
tile_in.to_csv('../DF_tiles_summary.csv', index=False)

tile_list = tile['slide'].tolist()
df_not_in = df[~df['Slide_ID'].isin(tile_list)]
df_not_in.to_csv('../Datafreeze_not_found_slides.csv', index=False)


