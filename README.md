当前的code分支用于修改代码，保证项目运行，完善项目功能。

运行指令参考：`python train_main.py -d CB-DB -sp 811-1 --gpu 2 --beta_loss 0.3 --gamma_loss 0.001 --alpha_loss 1 -lr 0.001 --max_epoch 500`

### 环境搭建

创建conda环境：运行指令 `conda env create -f torch17_chembiotip.yaml`。

安装可用于GPU的dgl库：运行指令 `wget https://conda.anaconda.org/dglteam/linux-64/dgl-cuda11.0-0.7.0-py37_0.tar.bz2` ，
然后运行 `conda install dgl-cuda11.0-0.7.0-py37_0.tar.bz2`。