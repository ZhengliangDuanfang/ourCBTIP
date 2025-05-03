当前的code分支用于修改代码，保证项目运行，完善项目功能。

运行指令参考：`python train_main.py -d CB-DB -sp 811-1 --gpu 0 --alpha_loss 1 --beta_loss 0.3 --gamma_loss 0.001 --delta_loss 1 --constant 0.5 -lr 0.001 --max_epoch 500`

运行结果位于`results`文件夹中，性能度量参数结果位于以月份开头、结尾不带`multi`的CSV文件中。

### 环境搭建

创建conda环境：运行指令 `conda env create -f torch17_chembiotip.yaml`。

安装可用于GPU的dgl库：运行指令 `wget https://conda.anaconda.org/dglteam/linux-64/dgl-cuda11.0-0.7.0-py37_0.tar.bz2` ，
然后运行 `conda install dgl-cuda11.0-0.7.0-py37_0.tar.bz2`。

切换环境：运行指令`conda activate torch17_biomip`

### 数据准备

训练部分，将存有`mdb`文件的内容从`prot_graph_db.zip`和`smile_graph_db_afp.zip`解压至同样位于`lmdb_files`文件夹下的同名文件夹中；运行`utils/sample_neg_split.py`完成数据的分拆，参数分别为数据集名称与`811`。运行指令`python calc_fp.py`，计算分子指纹并存储在`data/CB-DB/`文件夹下，并按照指纹距离将分子按簇分组。运行指令`python constract_pp_nn.py`，构建正负样本的图神经网络数据集。

开始训练前，`data`文件夹下结构应大致如下：

```
data
├── calc_fp.py
├── constract_pp_nn.py
└── CB-DB
    ├── biotech_seqs.csv
    ├── ddi_neg.csv
    ├── ddi_pos.csv
    ├── DTIs.csv
    ├── SMILESstrings.csv
    ├── target_seqs.csv
    ├── TTIs.csv
    ├── lmdb_files
    │   ├── prot_graph_db.zip
    |   ├── smile_graph_db_afp.zip
    │   ├── prot_graph_db
    │   │   ├── data.mdb
    │   │   └── lock.mdb
    │   └── smile_graph_db_afp
    │       ├── data.mdb
    │       └── lock.mdb   
    └── split-811-1
        ├── test_neg.txt
        ├── test_pos.txt
        ├── train_neg.txt
        ├── train_pos.txt
        ├── valid_neg.txt
        └── valid_pos.txt

```
