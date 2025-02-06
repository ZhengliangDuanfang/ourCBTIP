from model import GNN_GNN_GNN
from model import MultiInnerProductDecoder
from utils.arg_parser import parser
from utils.intra_graph_dataset import IntraGraphDataset
from utils.hete_data_utils import build_valid_test_graph
import torch
import json
import numpy as np

def load_id_mapping(pathname):
    id2drug = np.load(f'{pathname}_id2drug.npy', allow_pickle=True).item()
    drug2id = np.load(f'{pathname}_drug2id.npy', allow_pickle=True).item()
    id2target = np.load(f'{pathname}_id2target.npy', allow_pickle=True).item()
    target2id = np.load(f'{pathname}_target2id.npy', allow_pickle=True).item()
    id2relation = np.load(f'{pathname}_id2relation.npy', allow_pickle=True).item()
    relation2id = np.load(f'{pathname}_relation2id.npy', allow_pickle=True).item()
    return id2drug, drug2id, id2target, target2id, id2relation, relation2id

if __name__ == '__main__':
    params = parser.parse_args()
    params.split = '811-1'
    if params.dataset != 'CB-DB' or params.split != '811-1':
        raise NotImplementedError
    if params.dataset == 'CB-DB':
        params.small_mol_db_path = f'./data/{params.dataset}/lmdb_files/smile_graph_db_{params.SMILES_featurizer}'
        params.macro_mol_db_path = f'./data/{params.dataset}/lmdb_files/prot_graph_db'
        model_file_name = 'CB-DB-test.model'

    if not params.disable_cuda and torch.cuda.is_available():
        params.device = torch.device('cuda:%d' % params.gpu)
    else:
        params.device = torch.device('cpu')

    # 调用utils/intra_graph_dataset.py中的方法加载小分子和蛋白质的内部图数据集
    small_mol_graphs = IntraGraphDataset(db_path=params.small_mol_db_path, db_name='small_mol')
    macro_mol_graphs = IntraGraphDataset(db_path=params.macro_mol_db_path, db_name='macro_mol')

    # 获取内部特征图尺寸数据
    params.atom_insize = small_mol_graphs.get_nfeat_dim()
    params.bond_insize = small_mol_graphs.get_efeat_dim()
    params.aa_node_insize = macro_mol_graphs.get_nfeat_dim()
    params.aa_edge_insize = macro_mol_graphs.get_efeat_dim()

    with open('trained_models/numbers.json', 'r') as f:
        numbers = json.load(f)
    drug_cnt, target_cnt, small_cnt = numbers['drug_cnt'], numbers['target_cnt'], numbers['small_cnt']
    id2drug, drug2id, id2target, target2id, id2relation, relation2id = \
        load_id_mapping(f'trained_models/{params.dataset}_{params.split}')
    params.rel2id = relation2id
    params.num_rels = len(params.rel2id)

    small_intra_g_list = [small_mol_graphs[id2drug[i]][1] for i in range(small_cnt)]
    target_intra_g_list = [macro_mol_graphs[id2target[i]][2] for i in range(target_cnt)]

    # init molecule graphs for all molecules in inter_graph
    mol_graphs = {
        'small': small_intra_g_list,  
        'target': target_intra_g_list 
    }
    if small_cnt < drug_cnt: 
        mol_graphs['bio'] = [macro_mol_graphs[id2drug[i]][2] for i in
                             range(small_cnt, drug_cnt)]
        
    # TODO
    # train_pos_graph 需要从 ssp_multigraph_to_dgl 生成
    # edges 为输入

    encoder = GNN_GNN_GNN(params)
    decoder_inter = MultiInnerProductDecoder(params.inp_dim, params.num_rels, params)
    # decoder_intra = MultiInnerProductDecoder(params.inp_dim, params.num_rels, params)
    encoder.load_state_dict(torch.load(f'trained_models/encoder_{model_file_name}'))
    decoder_inter.load_state_dict(torch.load(f'trained_models/interdec_{model_file_name}'))
    # decoder_intra.load_state_dict(torch.load(f'trained_models/intradec_{model_file_name}'))

    raise NotImplementedError
    emb_intra, emb_inter = encoder(mol_graphs, train_pos_graph)
    emb_inter = emb_inter['drug']
    input_graph = build_valid_test_graph(drug_cnt, edges, relation2id, id2relation)
    result = decoder_inter(input_graph, emb_inter)

# # python predict.py --dataset CB-DB --split 811-1 --gpu 2