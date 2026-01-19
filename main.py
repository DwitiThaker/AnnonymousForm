from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes import adminRoute, formRoute, adminEmailRoutes, response

from Routes.selectable_users import router as selectable_users_router
from Routes.send_to_selectedusers import router as send_to_selected_users_router

app = FastAPI()

origins = [
    "http://localhost:3000",  
    "http://localhost:5173",  
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
app.include_router(selectable_users_router)
app.include_router(send_to_selected_users_router)



