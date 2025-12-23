from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from configurations import get_form_collection, get_user_collection
from Routes import adminRoute, formRoute, adminEmailRoutes, response

app = FastAPI()



origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   # works with specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "FastAPI is running successfully"}


app.include_router(adminRoute.admin_auth_route)
app.include_router(formRoute.form_route)
# app.include_router(accessCode.create_access_code_route)
app.include_router(response.form_response)
app.include_router(adminEmailRoutes.admin_email)
