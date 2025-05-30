from argparse import Namespace
import torch

def get_params():
    params = {
        'dataset': 'CB-DB',
        'split': '811-1',
        'gpu': 0,
        'disable_cuda': False,
        'load_model': True,
        'model_filename': 'CB-DB-test.model',
        'SMILES_featurizer': 'afp',
        'intra_out_dim': 128,
        'inp_dim': 128,
        'emb_dim': 128,
        'mode': 'two_pred',
        'max_epoch': 500,
        'min_epoch': 200,
        'stop_thresh': 20,
        'learning_rate': 0.001,
        'alpha_loss': 1.0,
        'beta_loss': 0.3,
        'gamma_loss': 0.001,
        'delta_loss': 0.0,
        'constant': 0.0,
    }

    # 创建类似argparse.Namespace的对象
    args = Namespace(**params)
    return args
