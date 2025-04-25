from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_siwadoc import SiwaDoc


db = SQLAlchemy()
cors = CORS()
siwa = SiwaDoc()