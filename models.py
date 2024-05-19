from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    mobile = Column(String(256), unique=True, nullable=True)
    username = Column(String(256), unique=True, nullable=False)
    google_id = Column(String(256), unique=True)
    github_id = Column(String(256), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), unique=True, nullable=False)
    mobile = Column(String(256), unique=True, nullable=True)
    username = Column(String(256), unique=True, nullable=False)
    problem = Column(String(256))
    appointments = relationship("Appointment", back_populates="patient", lazy=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    appointment_date = Column(String(256), nullable=False)
    price = Column(Float, nullable=False)
    payment_status = Column(String(50), default="false")
    appointment_status = Column(String(50), default="created")
    payment_link = Column(String(256))
    note = Column(String(256))
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    patient = relationship("Patient", back_populates="appointments", lazy=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)