所需要的python安装包：
1. pip install flask
1. pip install flask_migrate
1. pip install flask_cors
1. pip install flask_sqlalchemy

需要解压缩分子图文件压缩包`data/CB-DB/lmdb_files/prot_graph_db.zip`和`data/CB-DB/lmdb_files/smile_graph_db_afp.zip`到所在目录下。

初始化数据库：
1. 需要在修改一下后端数据库连接配置：CBTIPBackend/myapp/config.py文件下：
`SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'`
2. `flask db init`
3. `flask db migrate`
4. `flask db upgrade`
5. `flask init`

前端包安装：
`npm install`

后端运行：
`flask run`

前端运行：
`npm run dev`

在本地电脑上运行：
`ssh -N -L 3000:127.0.0.1:5173 temp_1@10.71.96.8`

在本地电脑上打开：
http://localhost:3000/
就可以查看前端
