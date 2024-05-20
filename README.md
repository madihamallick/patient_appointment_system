## Process to run the code

create mysql db `patient_appointment_system`


### If you make any changes in model 🖥️

```
alembic revision --autogenerate -m "Changes in the models"
alembic upgrade head
```


### For running the project locally 🏃

```
source venv/bin/activate
uvicorn main:app --reload
```

```
cd frontend
npm i
npm start
```


### Deployed LINK  🔗

https://patient-appointment-system.vercel.app/
