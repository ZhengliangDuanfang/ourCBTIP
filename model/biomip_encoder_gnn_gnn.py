import dgl
import torch
import torch.nn as nn

from .inter_encoder.dgl_rgcn import RGCN
from .intra_encoder.intra_GNN import Intra_AttentiveFP


class BioMIP_encoder(nn.Module):
    def __init__(self, params):
        super().__init__()
        self.params = params
        # Create two sets of intra-GNNs for small- and macro-molecules respectively
        self.small_intra = Intra_AttentiveFP(
            node_feat_size=params.atom_insize, # 即特征向量F的长度
            edge_feat_size=params.bond_insize,
            graph_feat_size=params.intra_out_dim # 默认128
        )
        self.macro_intra = Intra_AttentiveFP(
            node_feat_size=params.aa_node_insize,
            edge_feat_size=params.aa_edge_insize,
            graph_feat_size=params.intra_out_dim
        )

        self.init_inter_with_intra = True  # params.init_inter_with_intra
        # Create a stack of inter-GNNs
        self.inter_gnn = RGCN(params.inp_dim,
                              params.inp_dim,
                              params.emb_dim,
                              rel_names=params.rel2id
                              ).to(params.device)

    def forward(self, mol_structs, pos_graph): 
        # mol_structs的结构见train_main.py中mol_graphs的初始化
        # pos_graph为DGLHeteroGraph
        small_bg = dgl.batch(mol_structs['small'])#.to(self.params.device)
        small_mol_feats = self.small_intra(small_bg, small_bg.ndata['nfeats'].to(torch.float32),
                                           small_bg.edata['efeats'].to(torch.float32))
        target_mol_feats = None
        if 'target' in mol_structs:
            target_bg = dgl.batch(mol_structs['target'])#.to(self.params.device)
            target_mol_feats = self.macro_intra(target_bg, target_bg.ndata['nfeats'].to(torch.float32),
                                                target_bg.edata['efeats'].to(torch.float32))
        bio_mol_feats = None
        if 'bio' in mol_structs:
            bio_bg = dgl.batch(mol_structs['bio'])#.to(self.params.device)
            bio_mol_feats = self.macro_intra(bio_bg, bio_bg.ndata['nfeats'].to(torch.float32),
                                             bio_bg.edata['efeats'].to(torch.float32))
        pos_graph.nodes['drug'].data['intra'] = torch.cat([small_mol_feats, bio_mol_feats], 0).to(self.params.device) \
            if 'bio' in mol_structs else small_mol_feats.to(self.params.device)
        if 'target' in mol_structs:
            pos_graph.nodes['target'].data['intra'] = target_mol_feats.to(self.params.device)
        return {
                   'small': small_mol_feats.to(self.params.device),
                   'bio': bio_mol_feats.to(self.params.device) if bio_mol_feats is not None else None,
                   'target': target_mol_feats.to(self.params.device) if target_mol_feats is not None else None,
               }, self.inter_gnn(pos_graph)
