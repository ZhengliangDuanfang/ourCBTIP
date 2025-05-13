class Config:
	"""
	通用配置
	"""
	# 本地数据库链接配置
	# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:2004wangyang@localhost:3306/srtp'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
