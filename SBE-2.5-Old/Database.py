#!/usr/bin/env python
__author__ = 'dichotomy'

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Blueteam(Base):
    __tablename__ = 'blueteam'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Integer)
    email = Column(String)
    dns = Column(String)

class Host(Base):
    __tablename__ = "host"
    id = Column(Integer, primary_key=True)
    blueteam_id = Column(Integer, ForeignKey('blueteam.id'))
    hostname = Column(String)
    value = Column(Integer)

class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('host.id'))
    name = Column(String)
    port = Column(Integer)
    protocol = Column(String)
    value = Column(Integer)
    username = Column(String)
    password = Column(String)
    uri = Column(String)

class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'))
    name = Column(String)
    value = Column(Integer)
    content = Column(String)


class Flag(Base):
    __tablename__ = "flag"
    id = Column(Integer, primary_key=True)
    blueteam_id = Column(Integer, ForeignKey('blueteam.id'))
    name = Column(String)
    points = Column(Integer)
    value = Column(String)
    answer = Column(String)



if __name__=="__main__":
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///v3_0dbTest.sqlite')
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    bt = Blueteam(name="ALPHA", email="alpha@alpha.net", score=0, dns="10.100.101.100")
    s = session()
    s.add(bt)
    print s.query(Blueteam).all()
