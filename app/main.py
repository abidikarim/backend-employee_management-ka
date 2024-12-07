from fastapi import FastAPI
from app.routers import employee, auth, upload_employees
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(router=employee.router)
app.include_router(router=auth.router)
app.include_router(router=upload_employees.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello point of sale"}
