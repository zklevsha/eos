from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()

class Data(Base):
	__tablename__ = "data"

	id = Column(Integer, primary_key=True)
	pn = Column(String,unique=True)
	description = Column(String)
	endOfSaleData = Column(String)
	endOfNewServiceAttachmentDate = Column(String)
	endOfNewServiceContractRenewalDate = Column(String)
	lastDateOfSupport = Column(String)
	replacement = Column(String)
	sourceTitle = Column(String)
	sourceLink = Column(String)

class PidSummary(Base):
	__tablename__ = 'pid_summary'

	id = Column(Integer, primary_key=True)
	pn = Column(String,unique=True,nullable=False)
	status = Column(String)
	endOfSaleDate = Column(String)
	endOfSupportDate = Column(String)
	series = Column(String)
	sourceTitle = Column(String)
	sourceLink = Column(String)

class PidBad(Base):
	__tablename__ = 'pid_bad'

	id = Column(Integer, primary_key=True)
	pn = Column(String,unique=True)
	sourceTitle = Column(String)
	sourceLink = Column(String)



	