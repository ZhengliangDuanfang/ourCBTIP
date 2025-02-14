import time
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics 

dataset = 'C-DB'
df = pd.read_csv(f'../data/{dataset}/mfp/morgan_fp.csv', header=None, index_col=0)
fp_dict = {}
for row in df.itertuples():
    fp_dict[row.Index] = list(row[1:])

df = pd.read_csv(f'../data/{dataset}/ddi_pos.csv', header=None, dtype=str)
ddi_pos_array = df.values 
df = pd.read_csv(f'../data/{dataset}/ddi_neg.csv', header=None, dtype=str)
ddi_neg_array = df.values 

# 清除包含指纹未知的分子的互作用对
def mfp_existence(row): # 掩膜
    return row[0] in fp_dict and row[2] in fp_dict
mask_ddi_pos = np.apply_along_axis(mfp_existence, axis=1, arr=ddi_pos_array)
ddi_pos_array = ddi_pos_array[mask_ddi_pos]
mask_ddi_neg = np.apply_along_axis(mfp_existence, axis=1, arr=ddi_neg_array)
ddi_neg_array = ddi_neg_array[mask_ddi_neg]

# 检查是否出现仅有正样本或者负样本的互作用类型
ddi_pos_rel = np.unique(ddi_pos_array[:, 1])
ddi_neg_rel = np.unique(ddi_neg_array[:, 1])
if(not np.array_equal(np.sort(ddi_pos_rel), np.sort(ddi_neg_rel))):
    raise ValueError
else:
    print('DDI relation types match checked.')

# 调整互作用的表示方法，以互作用类型作为索引建立字典
ddi_rel_list = ddi_pos_rel
ddi_dicts = {}
for rel in ddi_rel_list:
    ddi_pos_arrays_by_rel = np.delete(ddi_pos_array[ddi_pos_array[:, 1] == rel], 1, axis=1)
    ddi_neg_arrays_by_rel = np.delete(ddi_neg_array[ddi_neg_array[:, 1] == rel], 1, axis=1)
    ddi_dicts[rel] = {'pos': ddi_pos_arrays_by_rel, 'neg': ddi_neg_arrays_by_rel}

# 将分子指纹组装为分子对特征，并拆分数据集
def construct_feat(chem1, chem2): # 采用首尾相连（concatenate）的方式组装分子对特征
    return np.array(fp_dict[chem1] + fp_dict[chem2])

def separate_train_data(X, y, train_ratio=0.8, test_ratio=0.1, rd=42): # 数据集拆分
    train_size = 1 - train_ratio
    val_size = 1 - test_ratio / train_size
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=train_size, random_state=rd)
    X_test, X_val, y_test, y_val = train_test_split(X_temp, y_temp, test_size=val_size, random_state=rd)
    return X_train, X_test, X_val, y_train, y_test, y_val

final_train_data_dict = {}
for rel, ddi_dict in tqdm(ddi_dicts.items(), total=len(ddi_dicts), desc='Map Feat Lists to Relations'):
    feat_arrays = {}
    separated_data = {}
    for pos_or_neg, ddi_arrays in ddi_dict.items():
        feat_arrays[pos_or_neg] = np.array([construct_feat(ddi_array[0], ddi_array[1]) for ddi_array in ddi_arrays])
    feats = np.concatenate((feat_arrays['pos'], feat_arrays['neg']), axis=0)
    targets = np.concatenate((np.ones(feat_arrays['pos'].shape[0]), np.zeros(feat_arrays['neg'].shape[0])))
    separated_data['x_train'], separated_data['x_test'], separated_data['x_val'], \
    separated_data['y_train'], separated_data['y_test'], separated_data['y_val'], \
        = separate_train_data(feats, targets)
    final_train_data_dict[rel] = separated_data

# 训练并预测
lr_cls_dict = {}
lr_prediction_list = []
lr_target_list = []
for rel in tqdm(ddi_rel_list, total = len(ddi_rel_list), desc='LR Training'):
    lr_cls_dict[rel] = LogisticRegression(max_iter=1000)
    lr_cls_dict[rel].fit(final_train_data_dict[rel]['x_train'], final_train_data_dict[rel]['y_train'])
    lr_prediction_list.append(lr_cls_dict[rel].predict(final_train_data_dict[rel]['x_val']))
    lr_target_list.append(final_train_data_dict[rel]['y_val'])
target_array = np.concatenate(lr_target_list)
prediction_array = np.concatenate(lr_prediction_list)

# 计算性能参数
def calc_aupr(label, prob): # AUPRC
    precision, recall, _thresholds = metrics.precision_recall_curve(label, prob)
    return metrics.auc(recall, precision)
auroc = metrics.roc_auc_score(target_array, prediction_array)
f1 = metrics.f1_score(target_array, prediction_array)
ap = metrics.average_precision_score(target_array, prediction_array)
auprc = calc_aupr(target_array, prediction_array)
# 输出结果
print(f'F1-Score: {f1}, AUROC: {auroc}, AUPRC: {auprc}, Average Precision: {ap}')
if not os.path.isdir('results'):
    os.mkdir('results')
with open(f'results/baseline_summary.txt', 'a+') as f:
    f.write(
        f'LR {dataset}\n'
        f'Train end time: {time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))}\n'
        f'F1-Score: {f1}, AUROC: {auroc}, AUPRC: {auprc}, Average Precision: {ap}\n\n'
    )