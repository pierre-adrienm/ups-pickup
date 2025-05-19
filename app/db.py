from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Pickup(Base):
    __tablename__ = 'pickups'

    pickup_id = Column(String, primary_key=True)
    nom = Column(String)
    adresse = Column(String)
    telephone = Column(String)
    date = Column(String)
    heure = Column(String)
    poids_total = Column(Float)
    nombr_Colis = Column(Integer)
    etat = Column(String)
    horodatage = Column(DateTime)

def get_engine():
    return create_engine("postgresql://upsuser:upspass@db:5432/upsdb")

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ Table 'pickups' créée ou déjà existante.")
