
from sqlalchemy import create_engine
from schema import DataManual,Base

engine = create_engine('sqlite:///eos.db',echo=True) 

Base.metadata.create_all(engine)