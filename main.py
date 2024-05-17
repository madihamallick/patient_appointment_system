from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated, Optional
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
import datetime
import stripe

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)

models.Base.metadata.create_all(bind=engine)

stripe.api_key = "sk_test_51Lcu5QSCn8hXCgcZIgjde51Vmgexkk3XbTKu482mjoelMOW7xM6qoua6mKAOaQvJAe3yTq8k9GElS5GzfFWH1L8z00TVuojh4a"


class UserBase(BaseModel):
    name: str
    email: str
    password: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    google_id: Optional[str] = None
    github_id: Optional[str] = None

class PatientBase(BaseModel):
    name: str
    email: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    problem: Optional[str] = None
    user_id: int

class AppointmentBase(BaseModel):
    appointment_date: datetime.date
    price: int
    payment_status: bool
    payment_link: Optional[str] = None
    note: Optional[str] = None
    patient_id: int
    user_id: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def search_patients(search_term: str, db:  Session = Depends(get_db)):
    return db.query(models.Patient).filter(models.Patient.name.contains(search_term)).all()

def model_to_dict(instance):
    return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}

@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserBase, db:  Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return model_to_dict(db_user)


@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientBase, db:  Session = Depends(get_db)):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return model_to_dict(db_patient)


@app.post("/appointments/", status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentBase, db:  Session = Depends(get_db)):
    db_appointment = models.Appointment(**appointment.dict())

    try:
        charge = stripe.PaymentLink.create(
            line_items=[{"price": 'price_1PGhUzSCn8hXCgcZUxmFWCdo', "quantity": 1}],
            after_completion={"type": "redirect", "redirect": {"url": "https://example.com"}},
        )
        db_appointment.payment_link = charge['url']

    except Exception as e:
        print(f"Error generating Stripe payment link: {e}")

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return model_to_dict(db_appointment)


@app.get("/users/", response_model=list[UserBase])
def read_users(db:  Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [model_to_dict(user) for user in users]

@app.get("/users/{user_id}", response_model=UserBase)
def read_user(user_id: int, db:  Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return model_to_dict(db_user)


@app.get("/patients/", response_model=list[PatientBase])
def read_patients(db:  Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return [model_to_dict(patient) for patient in patients]


@app.get("/patients/{patient_id}", response_model=PatientBase)
def read_patient(patient_id: int, db:  Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return model_to_dict(db_patient)


@app.get("/patients/{patient_id}/details", response_model=PatientBase)
def read_patient_details(patient_id: int, db:  Session = Depends(get_db)):
    db_patient = db.query(models.Patient).options(joinedload(models.Patient.appointments)).get(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return model_to_dict(db_patient)


@app.post("/patients/search/", response_model=list[PatientBase])
def read_patients(search_term: str, db: Session = Depends(get_db)):
    results = search_patients(search_term, db)
    if not results:
        raise HTTPException(status_code=404, detail="No patients found")
    return [model_to_dict(result) for result in results]


@app.get("/appointments/", response_model=list[AppointmentBase])
def read_appointments(db:  Session = Depends(get_db)):
    appointments = db.query(models.Appointment).all()
    return [model_to_dict(appointment) for appointment in appointments]


@app.get("/appointments/{appointment_id}", response_model=AppointmentBase)
def read_appointment(appointment_id: int, db:  Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return model_to_dict(db_appointment)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db:  Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id)
    if db_user.first() is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.delete(synchronize_session=False)
    db.commit()


@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db:  Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id)
    if db_patient.first() is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_patient.delete(synchronize_session=False)
    db.commit()


@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db:  Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    if db_appointment.first() is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db_appointment.delete(synchronize_session=False)
    db.commit()


@app.get("/patient/{patient_id}/appointments", status_code=status.HTTP_200_OK)
def get_appointments(patient_id: int, db: Session = Depends(get_db)):
    try:
        appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()
        return [model_to_dict(appointment) for appointment in appointments]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/user/{user_id}/appointments", status_code=status.HTTP_200_OK)
def get_appointments(user_id: int, db: Session = Depends(get_db)):
    try:
        appointments = db.query(models.Appointment).filter(models.Appointment.user_id == user_id).all()
        return [model_to_dict(appointment) for appointment in appointments]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/user/{user_id}/patients", status_code=status.HTTP_200_OK)
def get_patients(user_id: int, db: Session = Depends(get_db)):
    try:
        patients = db.query(models.Patient).filter(models.Patient.user_id == user_id).all()
        return [model_to_dict(patient) for patient in patients]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


