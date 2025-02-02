from fastapi import FastAPI, Depends, File, UploadFile
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import shutil
import os

# Initialize FastAPI
app = FastAPI()

# Database Configuration
DATABASE_URL = "sqlite:///./triovation.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Create "uploads" folder if not exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define Outfit Model (Database Table)
class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Outfit name
    category = Column(String)  # Outfit category
    image_filename = Column(String, nullable=True)  # Store image filename

# Create the database table
Base.metadata.create_all(bind=engine)

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API to Upload an Outfit Image
@app.post("/upload-outfit/")
async def upload_outfit(name: str, category: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    
    # Save file to uploads folder
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save outfit details to the database
    db_outfit = Outfit(name=name, category=category, image_filename=file.filename)
    db.add(db_outfit)
    db.commit()
    
    return {"message": "Outfit uploaded successfully", "image_url": f"/uploads/{file.filename}"}

# API to Retrieve All Outfits
@app.get("/get-outfits/")
def get_outfits(db: Session = Depends(get_db)):
    outfits = db.query(Outfit).all()
    return {"outfits": [{"id": outfit.id, "name": outfit.name, "category": outfit.category, "image_url": f"/uploads/{outfit.image_filename}" if outfit.image_filename else None} for outfit in outfits]}

# Serve Uploaded Images
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Home Route
@app.get("/")
def home():
    return {"message": "Welcome to Triovation Backend with Image Uploads!"}

