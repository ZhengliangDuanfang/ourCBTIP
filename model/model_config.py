from model import GNN_GNN_GNN
from model import FF_MI_max
from model import MultiInnerProductDecoder


def initialize_BioMIP(params):
    # 此处GNN_GNN_GNN即为BioMIP_encoder，来自model/biomip_encoder_gnn_gnn.py
    return GNN_GNN_GNN(params), \
           MultiInnerProductDecoder(params.inp_dim, params.num_rels, params).to(params.device), \
           MultiInnerProductDecoder(params.inp_dim, params.num_rels, params).to(params.device), \
           FF_MI_max(params).to(params.device)