from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.config import connect_to_mongo, close_mongo_connection
from routes.auth_route import auth_router
from routes.user_route import user_router
from routes.cart_route import cart_router
from routes.product_route import product_router

app = FastAPI(title="E-commerce Platform")

origins = [
    "http://localhost:3000",  # Frontend React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])

@app.get("/")
async def root():
    return {"message": "Welcome to E-Commerce API"}

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    print("MongoDB connection closed")
