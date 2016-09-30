
from sqlalchemy import create_engine
from schema import PidBad,PidSummary,Data,ParsedPages,Base

engine = create_engine('sqlite:///eos.db',echo=True) 

Base.metadata.create_all(engine)