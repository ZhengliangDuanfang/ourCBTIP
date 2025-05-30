import logging
import os
import time
import json
import pandas as pd
import numpy as np
import torch
import numpy as np
import dgl
from sklearn import metrics
from model import build_optimizer
from model.customized_loss import select_loss_function
from model.model_config import initialize_BioMIP
from utils.arg_parser import parser
from utils.data_utils import eval_threshold
from utils.generate_intra_graph_db import generate_small_mol_graph_datasets, generate_macro_mol_graph_datasets
from utils.hete_data_utils import ssp_multigraph_to_dgl, \
    dd_dt_tt_build_inter_graph_from_links, build_valid_test_graph
from utils.intra_graph_dataset import IntraGraphDataset
from utils.utils import calc_aupr


def train(encoder, decoder_intra, decoder_inter, dgi_model,
          opt, loss_fn: dict,
          mol_graphs,
          train_pos_graph, train_neg_graph,
          loss_save_file,
          epo_no,
          intra_pairs,
          epo_num_with_fp=200):
    # print(params.learning_rate)
    encoder.train()
    decoder_intra.train()
    decoder_inter.train()
    dgi_model.train()
    opt.zero_grad()
    emb_intra, emb_inter = encoder(mol_graphs,
                                   train_pos_graph)
    dgi_loss = dgi_model(emb_intra, emb_inter,
                         train_pos_graph, train_neg_graph)
    emb_intra_prot = emb_intra['target']
    if emb_intra['bio'] is not None:
        emb_intra_prot = torch.cat((emb_intra['target'], emb_intra['bio']), dim=0)
        emb_intra = torch.cat((emb_intra['small'], emb_intra['bio']), dim=0)
    else:
        emb_intra = emb_intra['small']
    # emb_intra = emb_intra['small']
    emb_inter = emb_inter['drug']
    pos_scores_intra = torch.hstack(tuple(decoder_intra(train_pos_graph, emb_intra).values())) #  hstack水平方向连接
    neg_scores_intra = torch.hstack(tuple(decoder_intra(train_neg_graph, emb_intra).values()))
    labels = torch.cat(
        [torch.ones(pos_scores_intra.shape[0]), torch.zeros(neg_scores_intra.shape[0])]).cuda()  # .numpy()
    pos_scores_inter = torch.hstack(tuple(decoder_inter(train_pos_graph, emb_inter).values()))
    neg_scores_inter = torch.hstack(tuple(decoder_inter(train_neg_graph, emb_inter).values()))

    score_inter, score_intra = torch.cat([pos_scores_inter, neg_scores_inter]), torch.cat(
        [pos_scores_intra, neg_scores_intra])
    BCEloss = torch.mean(loss_fn['ERROR'](score_inter, labels)) # 见 model/customized_loss.py 
    BCEloss += params.alpha_loss * torch.mean(loss_fn['ERROR'](score_intra, labels))
    KLloss = torch.mean(loss_fn['DIFF'](score_intra, score_inter))
    
    # delta_loss = 1
    # C = 0.5
    if epo_no < epo_num_with_fp:
        emb_intra_in1, emb_intra_in2, emb_intra_bt2 = emb_intra[intra_pairs[0]], emb_intra[intra_pairs[1]], emb_intra[intra_pairs[2]]
        diff_loss = loss_fn['FP_INTRA'](emb_intra_in1, emb_intra_in2, emb_intra_bt2, params.constant) # DONE: 实现loss_fn['FP_INTRA']
                    # + loss_fn['FP_INTRA'](prot_emb_intra_in1, prot_emb_intra_in2, prot_emb_intra_bt2) # IDEA: 蛋白质表征
        print("back:", BCEloss.item(), KLloss.item(), dgi_loss.item(), diff_loss.item())
        curr_loss = BCEloss + params.beta_loss * KLloss + params.gamma_loss * dgi_loss + params.delta_loss * diff_loss
    else:
        print("back:", BCEloss.item(), KLloss.item(), dgi_loss.item())
        curr_loss = BCEloss + params.beta_loss * KLloss + params.gamma_loss * dgi_loss

    curr_loss.backward()

    opt.step()
    print('Train epoch: {} Loss: {:.6f}'.format(epoch, curr_loss.item()))
    with open(f'results/{loss_save_file}', 'a+') as f:
        f.write(f'{BCEloss.item()},{KLloss.item()},{dgi_loss.item()},{curr_loss.item()}\n')
    return emb_intra, emb_inter


def predicting(model_intra, model_inter,
               intra_feats, inter_feats,
               pos_g, neg_g,
               multi_res=False):
    model_intra.eval()
    model_inter.eval()
    if multi_res:
        pos_pred, neg_pred = model_inter(pos_g, inter_feats), model_inter(neg_g, inter_feats)
        res = {}
        for k in pos_g.canonical_etypes[:-2]:
            res[k] = (torch.cat([torch.ones(pos_pred[k].shape[0]), torch.zeros(neg_pred[k].shape[0])]).cpu().numpy(),
                      torch.cat([pos_pred[k], neg_pred[k]]).detach().cpu().numpy())
        return res

    pos_score1 = torch.hstack(tuple(model_intra(pos_g, intra_feats).values()))
    neg_score1 = torch.hstack(tuple(model_intra(neg_g, intra_feats).values()))
    pos_score2 = torch.hstack(tuple(model_inter(pos_g, inter_feats).values()))
    neg_score2 = torch.hstack(tuple(model_inter(neg_g, inter_feats).values()))
    labels = torch.cat([torch.ones(pos_score1.shape[0]), torch.zeros(neg_score1.shape[0])]).numpy()
    return labels, torch.cat([pos_score1, neg_score1]).detach().cpu().numpy(), \
           torch.cat([pos_score2, neg_score2]).detach().cpu().numpy()


def save_id_mapping(pathname,
                    id2drug, drug2id,
                    id2target, target2id,
                    id2relation, relation2id):
    np.save(f'{pathname}_id2drug.npy', id2drug)
    np.save(f'{pathname}_drug2id.npy', drug2id)
    np.save(f'{pathname}_id2target.npy', id2target)
    np.save(f'{pathname}_target2id.npy', target2id)
    np.save(f'{pathname}_id2relation.npy', id2relation)
    np.save(f'{pathname}_relation2id.npy', relation2id)

def load_fp_contrastive_pairs(dataset, drug2id):
    df = pd.read_csv(f'data/{dataset}/mfp/cluster_pairs.csv', names=['mol1', 'mol2', 'mol3'])
    df['mol1'] = df['mol1'].map(drug2id)
    df['mol2'] = df['mol2'].map(drug2id)
    df['mol3'] = df['mol3'].map(drug2id)
    df.dropna(inplace=True)
    mols1, mols2, mols3 = df['mol1'].tolist(), df['mol2'].tolist(), df['mol3'].tolist()
    return mols1, mols2, mols3

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    params = parser.parse_args()
    print(params)

    if not os.path.isdir('results'):
        os.mkdir('results')
    if not os.path.isdir('trained_models'):
        os.mkdir('trained_models')

    time_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))

    # IDEA: generate_macro_mol_graph_datasets实现后取消注释
    # params.aln_path = '/data/rzy/drugbank_prot/full_drugbank/aln'
    # params.npy_path = '/data/rzy/drugbank_prot/full_drugbank/pconsc4'

    params.small_mol_db_path = f'./data/{params.dataset}/lmdb_files/smile_graph_db_{params.SMILES_featurizer}'
    params.macro_mol_db_path = f'./data/{params.dataset}/lmdb_files/prot_graph_db'

    print('small molecule db_path:', params.small_mol_db_path)
    print('macro molecule db_path:', params.macro_mol_db_path)

    # if not processed, build intra-view graphs
    # 如果对应路径没有这些数据，调用utils/generate_intra_graph_db.py中的方法生成小分子和蛋白质的内部图数据集
    if not os.path.isdir(params.small_mol_db_path):
        print("small molcule db_path not exist")
        generate_small_mol_graph_datasets(params)
    if not os.path.isdir(params.macro_mol_db_path):
        print("macro molcule db_path not exist")
        generate_macro_mol_graph_datasets(params)

    print("Train")

    # load intra-view graph dataset
    # 调用utils/intra_graph_dataset.py中的方法加载小分子和蛋白质的内部图数据集
    # IntraGraphDataset类继承自torch.utils.data.Dataset，在此处会调用__init__方法，
    # 在下面对图进行索引的时候会调用__getitem__方法
    small_mol_graphs = IntraGraphDataset(db_path=params.small_mol_db_path, db_name='small_mol')
    macro_mol_graphs = IntraGraphDataset(db_path=params.macro_mol_db_path, db_name='macro_mol')

    # 获取内部特征图尺寸数据
    params.atom_insize = small_mol_graphs.get_nfeat_dim()
    params.bond_insize = small_mol_graphs.get_efeat_dim()
    params.aa_node_insize = macro_mol_graphs.get_nfeat_dim()
    params.aa_edge_insize = macro_mol_graphs.get_efeat_dim()

    # load the inter-view graph
    # 调用utils/hete_data_utils.py中的方法加载外层视角的互作用图数据集
    # pos_adj_dict和neg_adj_dict是多层数组，第一层是三元组，
    # 三元组的第一个和第三项可能是"drug"或"target"中的一个，
    # 第二项则是药物互作用的类型；第二层是scipy.sparse.csc_matrix，
    # 代表了这种三元组构成的图的邻接矩阵
    # dd_dt_tt_triplets是多层数组，第一层是train/valid/test，第二层是pos/neg，
    # 第三层是dd/dt/tt，且只有train+pos三种都有，其余仅有dd，最后才是药物ID-药物ID-互作用关系ID三元组的list
    # triplets中没有第三层，而是合并起来，其余与dd_dt_tt_triplets相同
    # relation2id除了ddi的类型，还有'dt'和'tt'两种
    pos_adj_dict, neg_adj_dict, \
    triplets, dd_dt_tt_triplets, \
    drug2id, target2id, relation2id, \
    id2drug, id2target, id2relation, \
    drug_cnt, target_cnt, small_cnt = dd_dt_tt_build_inter_graph_from_links(
        dataset=params.dataset,
        split=params.split
    )
    with open('trained_models/numbers.json', 'w') as f:
        json.dump({'drug_cnt': drug_cnt, 'target_cnt': target_cnt, 'small_cnt': small_cnt}, f, indent=4)

    # init pos/neg inter-graph
    # 调用utils/hete_data_utils.py中的方法将小分子-蛋白质的互作用图转换为dgl图
    # 注意relation2d会被更新，并在train_pos_graph[1]中保存
    train_pos_graph, train_neg_graph = ssp_multigraph_to_dgl(
        drug_cnt, target_cnt,
        adjs=pos_adj_dict,
        relation2id=relation2id
    ), ssp_multigraph_to_dgl(
        drug_cnt, target_cnt,
        adjs=neg_adj_dict,
        relation2id=relation2id
    )

    params.rel2id = train_pos_graph[1] # params.rel2id 与 relation2id 一致
    params.num_rels = len(params.rel2id)
    id2relation = {v: k for k, v in relation2id.items()}
    # params.id2rel = { # 没找到这个变量在哪里会用到
    #     v: train_pos_graph[0].to_canonical_etype(k) for k, v in params.rel2id.items()
    # }
    train_pos_graph, train_neg_graph = train_pos_graph[0], train_neg_graph[0]
    # 此时这两个graph都是dgl.heterograph了
    dgl.save_graphs(f'trained_models/{params.dataset}_{params.split}_graph.dgl', train_pos_graph)

    # add edges in valid set, whose 'mask' = 1

    if not params.disable_cuda and torch.cuda.is_available():
        params.device = torch.device('cuda:%d' % params.gpu)
        train_pos_graph = train_pos_graph.to(params.device)
        train_neg_graph = train_neg_graph.to(params.device)
    else:
        params.device = torch.device('cpu')
    print(f"Training device is {torch.cuda.current_device()}")

    params.intra_enc1 = 'afp'
    params.intra_enc2 = 'afp'  # 'rnn'
    params.loss = 'focal'
    params.is_test = False

    # 建立小分子和蛋白质的内部图list
    # 前面说的调用__getitem__方法，这里就出现了
    # 这里[1]和[2]的区别还要追溯到build_seq_to_graph与build_mol_to_graph的返回值datum的区别
    small_intra_g_list = [small_mol_graphs[id2drug[i]][1] for i in range(small_cnt)]
    target_intra_g_list = [macro_mol_graphs[id2target[i]][2] for i in range(target_cnt)]

    # init molecule graphs for all molecules in inter_graph
    mol_graphs = {
        'small': small_intra_g_list,  # d_id = idx
        'target': target_intra_g_list  # t_id = idx
    }
    if small_cnt < drug_cnt: # 生物药
        mol_graphs['bio'] = [macro_mol_graphs[id2drug[i]][2] for i in
                             range(small_cnt, drug_cnt)]  # d_id = small_cnt+idx

    model_file_name = f'{time_str}_model_{params.dataset}{params.split}.model' \
        if params.model_filename is None else params.model_filename
    result_file_name = f'{time_str}_result_{params.dataset}_{params.split}'

    np.save(f'trained_models/triplets_test_pos.npy', triplets['test']['pos'])
    # model/model_config.py 导入模型
    encoder, decoder_intra, decoder_inter, ff_contra_net = initialize_BioMIP(params)
    # 从 utils/hete_data_utils.py 中导入测试图数据
    tgp, tgn = build_valid_test_graph(
        drug_cnt,
        edges=triplets['test']['pos'],
        relation2id=relation2id,
        id2relation=id2relation
    ).to(params.device), build_valid_test_graph(
        drug_cnt,
        edges=triplets['test']['neg'],
        relation2id=relation2id,
        id2relation=id2relation
    ).to(params.device)

    if not params.is_test: # 前面有定义为False
        # init opt, loss
        # 从model/customized_opt.py中导入优化器初始化方法
        opt = build_optimizer(encoder, decoder_intra, decoder_inter, ff_contra_net, params)
        # 从model/customized_loss.py中导入损失函数初始化方法
        loss_fn = select_loss_function(params.loss)  # a loss dict 'loss name': (weight, loss_fuction)
        best_auc = 0.
        best_epoch = -1
        vgp, vgn = build_valid_test_graph(
            drug_cnt,
            edges=triplets['valid']['pos'],
            relation2id=relation2id,
            id2relation=id2relation
        ).to(params.device), build_valid_test_graph(
            drug_cnt,
            edges=triplets['valid']['neg'],
            relation2id=relation2id,
            id2relation=id2relation
        ).to(params.device)
        cnt_trival = 0
        # load_fp_contrastive_pairs函数的实现见本文件上方
        intra_pairs = load_fp_contrastive_pairs(params.dataset, drug2id)
        # encoder.to(params.device) # IDEA: 解决内存限制问题
        decoder_intra.to(params.device)
        decoder_inter.to(params.device)
        ff_contra_net.to(params.device)
        print("Train Begin")
        for epoch in range(1, params.max_epoch + 1):
            emb_intra, emb_inter = train(encoder, decoder_intra, decoder_inter, ff_contra_net, # DONE: 此处dgi_model应改为ff_contra_net
                                         opt, loss_fn,
                                         mol_graphs,
                                         train_pos_graph, train_neg_graph,
                                         f'{result_file_name}_loss.csv',
                                         epoch,
                                         intra_pairs, # DONE: 实现 diff_loss
                                         epo_num_with_fp=20)
            print('predicting for valid data')

            val_G, val_P1, val_P2 = predicting(decoder_intra, decoder_inter,
                                               emb_intra, emb_inter,
                                               vgp, vgn)
            val1 = metrics.roc_auc_score(val_G, val_P1)
            val2 = metrics.roc_auc_score(val_G, val_P2)
            print(f'valid AUROC: ', val1, val2)
            if val2 > best_auc:
                cnt_trival = 0
                best_auc = val2
                best_epoch = epoch
                print(f'AUROC improved at epoch {best_epoch}')
                print(
                    f'val AUROC {val2}, AP {metrics.average_precision_score(val_G, val_P2)} F1: {metrics.f1_score(val_G, eval_threshold(val_G, val_P2)[1])}')
                print('predicting for test data')
                test_G, test_P1, test_P2 = predicting(decoder_intra, decoder_inter,
                                                      emb_intra, emb_inter,
                                                      tgp, tgn)
                # AP

                test_auroc, test_ap, test_auprc, test_f1 = metrics.roc_auc_score(test_G, test_P2), \
                                                           metrics.average_precision_score(test_G, test_P2), \
                                                           calc_aupr(test_G, test_P2), \
                                                           metrics.f1_score(test_G, eval_threshold(test_G, test_P2)[1])
                if not os.path.exists(f'results/{result_file_name}.csv'):
                    with open(f'results/{result_file_name}.csv', 'w') as f:
                        f.write('epoch,auroc,auprc,ap,f1\n')
                with open(f'results/{result_file_name}.csv', 'a+') as f:
                    f.write(f'{epoch},{test_auroc},{test_auprc},{test_ap},{test_f1}\n')
            else:
                if epoch > params.min_epoch:
                    cnt_trival += 1
                if cnt_trival >= params.stop_thresh:
                    print('Stop training due to more than 20 epochs with no improvement')
                    break
    
    # 保存训练结果
    torch.save(encoder.state_dict(), f'trained_models/encoder_{model_file_name}')
    torch.save(decoder_inter.state_dict(), f'trained_models/interdec_{model_file_name}')
    torch.save(decoder_intra.state_dict(), f'trained_models/intradec_{model_file_name}')
    save_id_mapping(f'trained_models/{params.dataset}_{params.split}', id2drug, drug2id, id2target, target2id, id2relation, relation2id)

    emb_intra, emb_inter = encoder(mol_graphs, train_pos_graph)

    if emb_intra['bio'] is not None:
        # np.savetxt(f'emb_vis/{params.dataset}_intra_bio_for_visual.csv', emb_intra['bio'].detach().cpu().numpy(), delimiter=',')
        emb_intra = torch.cat((emb_intra['small'], emb_intra['bio']), dim=0)

    else:
        emb_intra = emb_intra['small']

    emb_inter = emb_inter['drug']
    rel2gt_pred = predicting(decoder_intra, decoder_inter,
                             emb_intra, emb_inter,
                             tgp, tgn,
                             multi_res=True)
    res_list = []

    # print(len(rel2gt_pred.keys()), rel2gt_pred.keys())  # 62
    total_len, tot_auroc, tot_auprc, tot_ap, tot_f1 = 0, 0.0, 0.0, 0.0, 0.0
    count = 0 # for debug
    for k, v in rel2gt_pred.items():
        count += 1 
        # torch.save(v[0], f'trained_models/test_ref_{count}.pt')
        # torch.save(v[1], f'trained_models/test_perdict_{count}.pt')
        _len = v[0].shape[0]
        if _len == 0:
            res_list.append([int(k[1]), 0, 0, 0, 0, 0])
            continue
        try:
            test_auroc, test_ap, test_auprc, test_f1 = metrics.roc_auc_score(v[0], v[1]), \
                                                       metrics.average_precision_score(v[0], v[1]), \
                                                       calc_aupr(v[0], v[1]), \
                                                       metrics.f1_score(v[0], eval_threshold(v[0], v[1])[1])
            total_len += _len
        except ValueError:
            res_list.append([int(k[1]),0, 0, 0, 0, 0])
            continue
        tot_auroc += test_auroc * _len
        tot_auprc += test_auprc * _len
        tot_ap += test_ap * _len
        tot_f1 += test_f1 * _len
        res_list.append([int(k[1]), _len, test_auroc, test_auprc, test_ap, test_f1])
    pd.DataFrame(res_list).to_csv(f'results/{result_file_name}_multi.csv', index=False,
                                  header=['rel_name', 'test_len', 'auroc', 'auprc', 'ap', 'f1'])
    with open(f'results/{result_file_name}.csv', 'a+') as f:
        f.write(
            f'final,{params.dataset},'
            f'{tot_auroc / total_len},'
            f'{tot_auprc / total_len},'
            f'{tot_ap / total_len},'
            f'{tot_f1 / total_len}\n'
        )
    
    # 方便观察与比对结果
    end_time_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))
    with open(f'results/{params.dataset}_summary.txt', 'a+') as f:
        f.write(
            f'Train dataset: {params.dataset}\nTrain start time: {time_str}\n'
            f'Train end time: {end_time_str}\n'
            f'Epoch Number: {epoch}\n'
            f'Delta: {params.delta_loss}\n'
            f'Constant: {params.constant}\n'
            f'Average F1-score: {tot_f1 / total_len}\n'
            f'Average AUROC: {tot_auroc / total_len}\n'
            f'Average AUPRC: {tot_auprc / total_len}\n'
            f'Average Precision score: {tot_ap / total_len}\n\n'
        )