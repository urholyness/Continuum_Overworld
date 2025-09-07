from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./esg.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DataQuality(enum.Enum):
    PRIMARY = "primary"
    CARRIER = "carrier"
    DEFAULT = "default"

class HubType(enum.Enum):
    PACKHOUSE = "packhouse"
    XDOCK = "x-dock"
    COLDSTORAGE = "cold-storage"

class EnergySource(enum.Enum):
    SOLAR = "solar"
    GRID = "grid"
    DIESEL = "diesel"
    WIND = "wind"

class TransportMode(enum.Enum):
    TRUCK = "truck"
    RAIL = "rail"
    SHIP = "ship"
    AIR = "air"
    BARGE = "barge"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    cbam_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batches = relationship("Batch", back_populates="project")

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project_tag = Column(String(255))
    commodity = Column(String(255), nullable=False)
    net_mass_kg = Column(Float, nullable=False)
    pkg_mass_kg = Column(Float, default=0)
    harvest_week = Column(String(50))
    ownership = Column(String(50))  # "own" or "3PL"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="batches")
    legs = relationship("Leg", back_populates="batch", cascade="all, delete-orphan")
    hubs = relationship("Hub", back_populates="batch", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="batch", cascade="all, delete-orphan")

class Leg(Base):
    __tablename__ = "legs"
    
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    mode = Column(Enum(TransportMode), nullable=False)
    from_loc = Column(String(255), nullable=False)
    to_loc = Column(String(255), nullable=False)
    distance_km = Column(Float, nullable=False)
    payload_t = Column(Float, nullable=False)
    load_factor_pct = Column(Float, default=100)
    backhaul = Column(Boolean, default=False)
    vehicle_class = Column(String(255))
    energy_type = Column(String(50))
    energy_qty = Column(Float)
    date = Column(DateTime)
    carrier_id = Column(String(100))
    data_quality = Column(Enum(DataQuality), default=DataQuality.DEFAULT)
    factor_pack_id = Column(String(50), default="DEFRA-2024")
    rf_apply = Column(Boolean, default=False)  # For air freight RF uplift
    
    batch = relationship("Batch", back_populates="legs")

class Hub(Base):
    __tablename__ = "hubs"
    
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    type = Column(Enum(HubType), nullable=False)
    kwh = Column(Float, nullable=False)
    energy_source = Column(Enum(EnergySource), nullable=False)
    hours = Column(Float)
    location = Column(String(255))
    
    batch = relationship("Batch", back_populates="hubs")

class Factor(Base):
    __tablename__ = "factors"
    
    id = Column(Integer, primary_key=True)
    pack_id = Column(String(50), nullable=False)  # e.g., "DEFRA-2024"
    source_url = Column(Text)
    version = Column(String(50))
    region = Column(String(100))
    mode = Column(String(50))
    vehicle_class = Column(String(255))
    unit = Column(String(50))  # e.g., "kgCO2e/t.km"
    co2e_per_unit = Column(Float, nullable=False)
    ttw_share = Column(Float)  # Tank-to-Wheel percentage
    wtt_share = Column(Float)  # Well-to-Tank percentage
    rf_uplift = Column(Float)  # Radiative Forcing multiplier for air
    table_ref = Column(String(255))  # Reference to source table
    notes = Column(Text)

class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    iso14083_json = Column(JSON)
    glec_json = Column(JSON)
    ghg_scopes_json = Column(JSON)
    intensity_kgco2e_per_kg = Column(Float)
    cbam_snippet = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("Batch", back_populates="results")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()