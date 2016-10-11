import os, sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
from db.schema import *
from mylibs.utils import get_logger


#engine = create_engine('sqlite:///' + os.path.join(root,'db/eos-tests.db'),echo=True) 

test_db = sessionmaker(bind=create_engine('sqlite:///' + os.path.join(root,'tests/eos.db'),echo=True))()
prod_db =  sessionmaker(bind=create_engine('sqlite:///' + os.path.join(root,'db/eos.db'),echo=True))()


log.info('cheking data table')
q_ = 




# Перенос данных между таблицами
# from_db = sessionmaker(bind=create_engine('sqlite:///' + os.path.join(root,'tests/eos.db'),echo=True))()
# to_db =  sessionmaker(bind=create_engine('sqlite:///' + os.path.join(root,'tests/test.db'),echo=True))()



# arr = from_db.query(PidBad).all()[:5]
# from_db.close()
# print (arr)
# for i in  arr:
# 	i = i.__dict__
# 	print (i.keys())
# 	del i['id']
# 	del i['_sa_instance_state']
# 	to_db.add(PidBad(**i))
# 	to_db.commit()