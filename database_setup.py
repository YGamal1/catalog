#!/usr/bin/env python2

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, joinedload, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Categorie(Base):
    __tablename__ = 'categorie'
    id = Column(Integer)
    name = Column(String(250), nullable=False, primary_key=True)
   
    
    @property
    def serializable(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class CategorieItem(Base):
    __tablename__ = 'categorie_item'

    name = Column(String(80), nullable=False)
    id = Column (Integer, primary_key=True)
    description = Column(String(250)) 
    categorie_name = Column(String(250), ForeignKey('categorie.name'))
    categorie = relationship(Categorie, backref='items')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serializable(self):
        return {
            'categorie_name': self.categorie_name,
            'description': self.description,
            'item': self.name,
            'id': self.id,
        }


engine = create_engine('postgresql://catalog:catalog/catalog')


Base.metadata.create_all(engine)
