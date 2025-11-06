from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configurations import get_form_collection, get_user_collection
from Routes import adminRoute, formRoute, accessCode

app = FastAPI()

# ✅ Add this BEFORE defining routes or including routers


origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
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

@app.post("/insert_dummy")
def insert_sample():
    form_col = get_form_collection()
    form_col.insert_one({"title": "Demo Form", "status": "draft"})
    return {"message": "Inserted sample data!"}

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/test-db")
def test_db():
    user_col = get_user_collection()
    test_user = {"name": "Dwiti", "role": "backend engineer"}
    result = user_col.insert_one(test_user)
    return {"inserted_id": str(result.inserted_id)}

# ✅ Include routers after middleware
app.include_router(adminRoute.admin_auth_route)
app.include_router(formRoute.form_route)
app.include_router(accessCode.create_access_code_route)
