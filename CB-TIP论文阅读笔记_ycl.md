## 图与图神经网络

### 图

一个有向图$\mathcal{G}=(\mathcal{V},\mathcal{E},\psi, \phi)$包含四个集合：节点集合$\mathcal{V}$ ，边集合$\mathcal{E}$ ，节点类型集合$T_{\mathcal{V}}$ ，边类型集合$T_\mathcal{E}$ 。其中，节点与节点类型之间存在映射函数$\psi (v)\in T_\mathcal{V}$，边与边类型之间存在映射函数$\phi(v)\in T_\mathcal{E}$ 。

有向图的拓扑结构（节点-边关系）用**邻接矩阵**表示。矩阵元素为1表示对应节点之间存在边，否则不存在。

在拓扑关系之外，节点与边的多种属性记录在节点属性矩阵和边属性矩阵中。（论文没有展开介绍。）本论文中用到的节点和边类型不为单一的图称为**异构图**。

### 图神经网络

以图的节点、边、节点属性、边属性为输入，学习节点$v\in \mathcal{V}$的表示$\mathbf{h}(v)$或者整张图$\mathcal{G}$的表示$h_\mathcal{G}$。

现代（这里没说本文是不是）图神经网络遵循“信息传递”策略，每一层通过某节点的相邻节点和相邻边的信息计算该节点的信息。假设第k层节点$v$的表示为$\mathbf{h}^{(k)}(v)$，则层之间迭代方法为：

$$
\mathbf{Msg}^{(k)}(v) = AGGREGATE^{(k)} (\{ \mathbf{h}^{(k−1)}(u):u \in \mathcal{N} (v) \}) 
\\
\mathbf{h}^{(k)}(v) = COMBINE^{(k)} ( \mathbf{h}^{(k−1)}(v),\mathbf{Msg}^{(k)}(v) )
$$

其中$\mathbf{Msg}$表示邻域信息，$\mathbf{h}^{(k)}(v)$表示节点$v$在第$k$层中的表示，$\mathcal{N}$表示节点$v$的直接邻居集合。如果最后一层记作第$K$层，则$\mathbf{h}(v)=\mathbf{h}^{(k)}(v)$，$h_\mathcal{G}=READOUT(\{\mathbf{h}^{(K)}(v)|v\in \mathcal{V}\})$。

## 分子表示

小分子：SMILES表达式，其它没多讲

蛋白质大分子：

*   PDB文件

*   氨基酸序列到PDB：“AlphaFold”、ColabFold等

*   PDB到原子层级的图：“BagPype”

*   PDB到残基层级的图：“DGraphDTI”、“致力于寻找变构靶点信号通路的模型”


## 药物互作用识别

本文使用基于计算的方法中，基于图表示学习的方法。

### 基于图表示学习方法

多数方法：“将药物看作图中的节点、药物的特性数据看做看作节点属性、已知药物互作用看作边，将药物互作用预测转化为对图中节点之间链路 存在性的预测[48,51,53]”

*   “Decagon[51]和 KGNN[53]”：“在药物互作用图中额外引入了药物与 靶点蛋白、靶点蛋白之间、药物与基因之间的关系”


少数方法：“将分子看做分子图，直接从分子结构中学习含有任务相关的化学信息药物表示”

*   “CoAttention[58]设计了共同注意力机制”

*   “Bi-GNN[55]” “将药物互作用网络看做包含内层分子结构和外层已知互作用的 双视角图”

*   “DSN-DDI[49]同时从单个药物的分子图和药物对中提取影响互作用的关键药物结构”

***

“图 4.2 药物互作用识别系统” 这个图特别有用

## 数据预处理

输入：“两大类药物和与内源蛋白质的分子线性表达式以及互作用数据”

输入来源：DrugBank的XML文件

处理工具：“DBparser”

化学药分子线性表达式：SMILES

生物药/内源蛋白质分子线性表达式：氨基酸序列

互作用：文本$\rightarrow$事件类型

$\rightarrow$数据清洗$\rightarrow$从String数据库补充内源蛋白质互作用

## 内层视角分子图构造

注：后续训练外层图时，每个内层分子图都会转化为分子指纹，且转化方法会随着训练而调整

### 小分子内层图

输入SMILES表达式$\rightarrow$RDKit转换为分子图$\rightarrow$dgl-lifesci附加原子与化学键属性到分子图$\rightarrow$输出内层分子结构图

### 大分子内层图

包括生物药与内源蛋白质

输入长度为L的氨基酸序列$\rightarrow$ “首先利用蛋白质序列检索比较工具 HHblits[81]生成其与蛋白质序列数据库 UniRef6的多序列比对 （MSA）结果文件，随后用 HHsuite7中的 HHfilter 工具按最大序列一致性等尺度对 MSA 进行过滤并用 BioPython8的 Bio.SeqIO 模块将比对文件转化为适合输入到基于伪似然最大化的蛋白质残基接触图预测工具的格式，接着将比对文件输入到残基接触预测方法”“Pconsc4\[82]和 CCMpred\[83]预测得到大小为 L × L、元素数值均在 \[0, 1] 范围的残基接触图”$\rightarrow$将接触图二值化为邻接矩阵$\rightarrow$为节点附加氨基酸种类等属性\[19]，并将附加属性后的图$B_i$作为的内层分子结构图

## 外层视角分子图的构建

“在实现中，药物-药物互作用被处理为有向边，其类型即药物互作用事件的类型；药物-内源蛋白互作用被处理为“由药物到内源蛋白质的”和“由内源蛋白质到药物的”的有向边，内源蛋白之间互作用被定义为无向边。”

“由于内层视角的药物/内源蛋白质分子结构图是确定的、不需要更新的，系统对内层视角只进行一次构建，将构建好的属性图存储为闪电内存映射型数据库 （LMDB）文件。”

## CB-TIP框架

以所构建的双视角异构图为输入，由基于图表示学习的编码模块和药物互作用预测模块两个顺序的模块构成

### 内层视角分子表征

使用分子图编码器处理小分子和大分子。

分子图编码器的工作过程：对分子图中全部节点生成稠密表示$\rightarrow$从分子图中全部节点的稠密表示生成该分子图的稠密向量作为稠密表示。

具体使用Attentive Fingerprints (“AttentiveFP”)

$$
\mathbf{F}^{(k)}(v)=\mathrm{GRU}^{(k)}\left(\mathbf{Msg}^{(k)}(v),\mathbf{F}^{(k-1)}(v)\right)
\\
\mathbf{Msg}^{(k)}(v)=\mathrm{ELU}\left(\sum_{u\in\mathcal{N}(v)}\mathrm{att}^{(k)}(u,v)\odot\mathrm{M}^{(k)}\odot\mathrm{F}^{(k-1)}(u)\right)
\\ 
\mathbf{att}^{(k)}(u,v)=\mathrm{EdgeSoftmax}(\mathbf{logits}^{(k)}(u,v))=\frac{\exp\left(\mathbf{logits}^{(k)}(u,v)\right)}{\sum_{u\in\mathcal{N}(v)}\exp\left(\mathbf{logits}^{(k)}(u,v)\right)}
\\
\mathbf{logits}^{(k)}(u,v)=\mathrm{LeakyReLU}\left(\mathbf{W}^{(k)}\odot\left[\mathbf{F}(u)^{(k-1)}\oplus\mathbf{F}(v)^{(k-1)}\right]\right)
$$

注意论文中的$\mathbf{F}^{(k-1)}(u)$指的是节点$u$的表示，整个分子图的表示为$\mathbf{F}$。“汇总层在分子图上虚构出一个与该分子图中所有真实节点相连的超级虚拟节点并将超级节点的特征初始化为实际节点特征的总和，这个节点象征整个分子。”

### 外层视角分子表征

$$
\mathbf{Msg}^{(k)}(v)=\underset{r\in \mathcal{R}}\sum \underset{u\in \mathcal{N}^r(v)}\sum \frac{1}{c_{v,r}} \mathbf{D}^{(k)}_r \mathbf{Z}^{(k−1)}(u), \\\mathbf{Z}^{(k)}(v) = \mathrm{ReLU} ( \mathbf{D}^{(k)}_0 \mathbf{Z}^{(k−1)}(v)+\mathbf{Msg}^{(k)}(v) )
$$

初始外层表征$\mathbf{Z}^{(0)}=\mathbf{F}$。后续使用多关系图卷积神经网络（RGCN），迭代更新$\mathbf{Z}^{(k)}$。注意$\mathbf{Msg}$外层求和遍历边的各类型，内层求和遍历通过该类型边与当前点$v$相连的所有点。

### 发生事件概率预测

内层视角打分器和外层视角打分器对三元组 t 给 出的预测值分别记作 $S_{tra}(t)$ 和 $S_{ter}(t)$。对于 $t = 〈d_1, evt, d_2〉$,

$$
\mathrm{S}^{\mathrm{tra}}(t)=\sigma\left(\sum\mathrm{F}(d_1)\odot\mathrm{F}(d_2)\odot\mathrm{W}_{evt}^\mathrm{tra}\right)\\\mathrm{S}^{\mathrm{ter}}(t)=\sigma\left(\sum\mathrm{Z}(d_1)\odot\mathrm{Z}(d_2)\odot\mathrm{W}_{evt}^\mathrm{ter}\right)
$$

注意输入是一个三元组。

### 模型训练策略（损失函数定义）

见原论文。
