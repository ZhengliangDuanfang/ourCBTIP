import torch.nn as nn
import torch

def triplet_loss(u, u_plus, u_minus, C):
    d_plus = torch.norm(u - u_plus, p=2, dim=1) ** 2
    d_minus = torch.norm(u - u_minus, p=2, dim=1) ** 2
    return torch.sum(torch.relu(d_plus - d_minus + C))

def select_loss_function(loss_select):
    return {
        'ERROR': nn.BCEWithLogitsLoss(reduction='none'),  # if loss_select == 'focal' else BCEFocalLoss(),
        'DIFF': nn.KLDivLoss(reduction='none'),
        'FP_INTRA': triplet_loss
    }
