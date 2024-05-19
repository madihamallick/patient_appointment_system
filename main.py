from fastapi import FastAPI, HTTPException, Depends, status, APIRouter, Request
from pydantic import BaseModel
from typing import Annotated, Optional, Dict, Any
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
import datetime
import stripe
from sqlalchemy import func
from fastapi.responses import JSONResponse, RedirectResponse
import requests
import os

app = FastAPI()
router = APIRouter()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

models.Base.metadata.create_all(bind=engine)

stripe.api_key = "sk_test_51Lcu5QSCn8hXCgcZIgjde51Vmgexkk3XbTKu482mjoelMOW7xM6qoua6mKAOaQvJAe3yTq8k9GElS5GzfFWH1L8z00TVuojh4a"


class PostUserBase(BaseModel):
    name: str
    email: str
    password: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    google_id: Optional[str] = None
    github_id: Optional[str] = None


class UserBase(PostUserBase):
    id: Optional[int] = None


class PostPatientBase(BaseModel):
    name: str
    email: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    problem: Optional[str] = None
    user_id: int


class PatientBase(PostPatientBase):
    id: Optional[int] = None


class PatientWithAppointments(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    problem: Optional[str] = None
    user_id: int
    total_appointments: int


class PostAppointmentBase(BaseModel):
    appointment_date: str
    price: int
    payment_status: bool
    payment_link: Optional[str] = None
    note: Optional[str] = None
    patient_id: int
    user_id: int


class AppointmentBase(PostAppointmentBase):
    id: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/auth/google")
async def login(request: Request):
    url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri=http://localhost:8000/callback&scope=email%20profile&access_type=offline"
    return RedirectResponse(url=url)

@router.get("/callback")
async def oauth_callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "http://localhost:8000/callback"
    }
    response = requests.post(token_url, data=payload)
    tokens = response.json()
    access_token = tokens["access_token"]

    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    user = db.query(models.User).filter(models.User.google_id == user_info['id']).first()
    if user:
        return JSONResponse(content={"message": "Signed in successfully"})
    else:
        new_user = models.User(**user_info)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(content={"message": "Signed up successfully"})


def search_patients(search_term: str, db:  Session = Depends(get_db)):
    return db.query(models.Patient).filter(models.Patient.name.contains(search_term)).all()

def model_to_dict(instance):
    return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}


# signup user
@app.post("/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: PostUserBase, db:  Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return model_to_dict(db_user)


# signin user
@app.post("/users/signin", response_model=UserBase)
def signin(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.password!= password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return model_to_dict(user)


@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(patient: PostPatientBase, db:  Session = Depends(get_db)):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return model_to_dict(db_patient)


@app.post("/appointments/", status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: PostAppointmentBase, db:  Session = Depends(get_db)):
    db_appointment = models.Appointment(**appointment.dict())

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    try:
        redirect_url = f"http://localhost:3000/paymentdone/{db_appointment.id}"
        charge = stripe.PaymentLink.create(
            line_items=[{"price": 'price_1PGhUzSCn8hXCgcZUxmFWCdo', "quantity": 1}],
            after_completion={"type": "redirect", "redirect": {"url": redirect_url}},
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


@app.get("/patients/", response_model=list[PatientWithAppointments])
def read_patients(db: Session = Depends(get_db)):
    patients_with_appointments = db.query(
        models.Patient,
        func.count(models.Appointment.patient_id).label("total_appointments")
    ).outerjoin(
        models.Appointment,
        models.Patient.id == models.Appointment.patient_id
    ).group_by(
        models.Patient.id
    ).all()

    patients = []
    for patient, total_appointments in patients_with_appointments:
        patient_data = model_to_dict(patient)
        patient_data["total_appointments"] = total_appointments
        patients.append(patient_data)

    return patients


@app.get("/patients/{patient_id}", response_model=PatientBase)
def read_patient(patient_id: int, db:  Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return model_to_dict(db_patient)


@app.get("/patients/{patient_id}/details", response_model=Dict[str, Any])
def read_patient_details(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).options(joinedload(models.Patient.appointments)).get(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_details = model_to_dict(db_patient)
    appointments = [model_to_dict(appointment) for appointment in db_patient.appointments]
    patient_details["appointments"] = appointments

    return patient_details


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
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()

    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    for appointment in db_patient.appointments:
        db.delete(appointment)
    db.delete(db_patient)
    db.commit()
    return {"detail": f"Patient with ID {patient_id} and their appointments have been deleted."}


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


@app.patch("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db_appointment.appointment_status = "complete"
    db.commit()
    return model_to_dict(db_appointment)


@app.patch("/appointments/{appointment_id}/payment")
def mark_payment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db_appointment.payment_status = True
    db.commit()
    return model_to_dict(db_appointment)