import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
# TABLE CLASS DECLARATIONS #########################

#Items table
class Items(Base):
	__tablename__ = 'items'
	id = Column(Integer, primary_key=True)
	name = Column(String(225), nullable=False)
	description = Column(String(1000), nullable=False)
	category = Column(String(225), nullable=False)
	date_added = Column(DateTime, nullable=False)

	@property
	def serialize(self):
		#Returns JSON-serialized representation of this object
		return {
			'name' : self.name,
			'description' : self.description,
			'category' : self.category,
			'date_added' : self.date_added
		}

#Categories Table
class Categories(Base):
	__tablename__ = 'categories'
	id = Column(Integer, primary_key=True)
	name = Column(String(225), nullable=False, primary_key=True)
	description = Column(String(1000), nullable=False)
	date_added = Column(DateTime, nullable=False)
	
### CLOSING CODE ##################################
engine = create_engine('postgresql:///item_catalog.db')

Base.metadata.create_all(engine)
