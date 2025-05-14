import random

import pandas as pd
import sys


def gen_pairs(dataset_name, K):
    classes = pd.unique(df['cluster_id'])
    chem_triple = []
    for ci in classes:
        index_i = list(df[df['cluster_id'] == ci].index)
        # print(index_i)
        random_is = random.sample(range(0, len(index_i)), min([K, len(index_i)]))
        div = (len(random_is) - len(random_is) % 2) // 2
        j_pos = random_is[:div]
        random_is = random_is[div:]
        j_neg = list(df[df['cluster_id'] != ci].index)
        random_j_neg = random.sample(range(0, len(j_neg)), min([K, div]))
        chem_triple += [[index_i[i], index_i[j], j_neg[k]] for i, j, k in zip(random_is, j_pos, random_j_neg)]
    pd.DataFrame(chem_triple).to_csv(f'{dataset_name}/mfp/cluster_pairs.csv', header=False, index=False)


dataset = sys.argv[1]
df = pd.read_csv(f'{dataset}/mfp/cluster_res-ward_n=20.csv', index_col=0, header=None, names=['cluster_id'])
# IDEA: 大分子目前无法生成聚类，因而无法被加入到三元组中
print(df)
for univ in pd.unique(df['cluster_id']):
    print(df[df['cluster_id'] == univ].shape[0])

print('\n')

gen_pairs(dataset, 100)
