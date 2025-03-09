from fastapi import FastAPI
from config.config import connect_to_mongo, close_mongo_connection
from routes.auth_route import auth_router
from routes.user_route import user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="E-commerce Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Autorise le frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "Welcome to E-Commerce API"}

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
