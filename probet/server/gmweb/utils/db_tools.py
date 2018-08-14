
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

objEngine = create_engine("mysql+mysqlconnector://root:baobaobuku@127.0.0.1:3306/probet_data",encoding='utf-8')

Session = sessionmaker(bind=objEngine,class_=Session)
session = Session()



