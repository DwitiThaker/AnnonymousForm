from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes import adminRoute, formRoute, adminEmailRoutes, response

app = FastAPI()



origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "http://localhost:8000",
    "https://feedback-form-zeta-gray.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "FastAPI is running successfully"}


app.include_router(adminRoute.admin_auth_route)
app.include_router(formRoute.form_route)
app.include_router(response.form_response)
app.include_router(adminEmailRoutes.admin_email)
