### Sample tSNE files ###

import pandas as pd
import random

for i in ['IC5', 'IC70']:
    n = sum(1 for line in open('../Results/{}/out/For_tSNE.csv'.format(i))) - 1
    s = 20000
    skip = sorted(random.sample(range(n), n - s))
    try:
        skip.remove(0)
    except:
        pass
    xx = pd.read_csv('../Results/{}/out/For_tSNE.csv'.format(i), header=0, skiprows=skip)
    xx.to_csv('../Results/{}/out/tSNE_sampled.csv'.format(i), index=False)

