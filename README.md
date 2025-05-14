原实现：https://github.com/ZillaRU/CB-TIP

本项目的目的是完善CB-TIP模型的原实现，并设计基于网页的演示系统。

## 训练

运行指令参考：`python train_main.py -d CB-DB -sp 811-1 --gpu 0 --alpha_loss 1 --beta_loss 0.3 --gamma_loss 0.001 --delta_loss 0.01 --constant 0.5 -lr 0.001 --max_epoch 1000`

运行结果位于`results`文件夹中，性能度量参数结果位于以月份开头、结尾不带`multi`的CSV文件中。

### 环境搭建

创建conda环境：运行指令 `conda env create -f torch17_biomip.yaml`。

> 如有需要可安装可用于GPU的dgl库：运行指令 `wget https://conda.anaconda.org/dglteam/linux-64/dgl-cuda11.0-0.7.0-py37_0.tar.bz2` ，
> 然后运行 `conda install dgl-cuda11.0-0.7.0-py37_0.tar.bz2`。

切换环境：运行指令`conda activate torch17_biomip`

### 数据准备

将存有`mdb`文件的内容从`prot_graph_db.zip`和`smile_graph_db_afp.zip`解压至同样位于`lmdb_files`文件夹下的同名文件夹中；运行`utils/sample_neg_split.py`完成数据的分拆，参数分别为数据集名称与`811`。运行指令`python calc_fp.py`，计算分子指纹并存储在`data/CB-DB/`文件夹下，并按照指纹距离将分子按簇分组。运行指令`python constract_pp_nn.py`，构建正负样本的图神经网络数据集。

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
    │   ├── prot_graph_db
    │   │   ├── data.mdb
    │   │   └── lock.mdb
    │   └── smile_graph_db_afp
    │       ├── data.mdb
    │       └── lock.mdb   
    ├── mfp
    │   ├── cluster_pairs.csv
    │   ├── cluster_res-average_n=20.csv
    │   ├── cluster_res-complete_n=20.csv
    │   ├── cluster_res-ward_n=20.csv
    │   └── morgan_fp.csv
    └── split-811-1
        ├── test_neg.txt
        ├── test_pos.txt
        ├── train_neg.txt
        ├── train_pos.txt
        ├── valid_neg.txt
        └── valid_pos.txt

```

## 演示

我们搭建了基于 Vue 和 Flask 的前后端演示系统。

### 配置流程

1. 按上文训练步骤配置环境。
2. 确保根目录下`trained_models`目录内容结构如下。如果没有，重新按上文执行训练步骤，系统会自动导出对应文件。
    ```
    trained_models
    ├── CB-DB_811-1_drug2id.npy
    ├── CB-DB_811-1_graph.dgl
    ├── CB-DB_811-1_id2drug.npy
    ├── CB-DB_811-1_id2relation.npy
    ├── CB-DB_811-1_id2target.npy
    ├── CB-DB_811-1_relation2id.npy
    ├── CB-DB_811-1_target2id.npy
    ├── encoder_CB-DB-test.model
    ├── interdec_CB-DB-test.model
    ├── intradec_CB-DB-test.model
    ├── multiple_test.model
    ├── numbers.json
    └── triplets_test_pos.npy
    ```
3. 后端数据库配置
    1. 确认后端数据库连接配置：`myapp/config.py`文件下中包含`SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'`
    2. 在根目录下执行`flask db init`
    3. 在根目录下执行`flask db migrate`
    4. 在根目录下执行`flask db upgrade`
    5. 在根目录下执行`flask init`
4. 后端运行：`flask run`
5. 切换到前端目录：`cd CBTIPFront`
6. 前端环境配置：`npm install`
7. 前端运行：`npm run dev`
8. 如果运行在远程服务器上，可以设置转发：`ssh -N -L 3000:127.0.0.1:5173 <user name>@<ip address>`，需注意将`<user name>`和`<ip address>`分别替换为运行所用的账号以及服务器所在IP地址。按要求输入密钥后，界面无反应属于正常现象。
9. 前端URL：http://localhost:3000/

## 测试环境

- Ubuntu 20.04.6 LTS
- conda 22.9.0
- npm 10.1.0
- nodejs v20.9.0
- CUDA Version: 12.2 
- Nvidia A40 $\times$ 1