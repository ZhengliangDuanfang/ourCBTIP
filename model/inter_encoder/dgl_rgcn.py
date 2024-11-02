# Define a Heterograph Conv model
import dgl.nn.pytorch as dglnn
import torch.nn as nn
import torch.nn.functional as F


class RGCN(nn.Module): # question: 为什么只有两层？
    def __init__(self, in_feats, hid_feats, out_feats, rel_names):
        super().__init__()
        # https://docs.dgl.ai/en/0.6.x/api/python/nn.pytorch.html#heterographconv
        self.conv1 = dglnn.HeteroGraphConv({
            rel: dglnn.GraphConv(in_feats, hid_feats) # 同一类边共享一个convolution module
            for rel in rel_names}, aggregate='sum')
        self.conv2 = dglnn.HeteroGraphConv({
            rel: dglnn.GraphConv(hid_feats, out_feats)
            for rel in rel_names}, aggregate='sum')

    def forward(self, graph):
        intra_feats = {
            'drug': graph.nodes['drug'].data['intra'], # 后者为一个tensor([feature, feature, ...])
            'target': graph.nodes['target'].data['intra']
        } if len(graph.ntypes) > 1 else {
            'drug': graph.nodes['drug'].data['intra']
        }
        h = self.conv1(graph, intra_feats)

        h = {k: F.relu(v) for k, v in h.items()}
        h = self.conv2(graph, h)
        return h
