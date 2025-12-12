from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import math

app = FastAPI(title="Tutor Finder API", description="Backend for Student-Teacher Location Marketplace")

# --- DATA MODELS (Schemas) ---

# Teacher ka data structure (Location ke sath)
class Teacher(BaseModel):
    id: int
    name: str
    subject: str
    latitude: float
    longitude: float
    is_available: bool = True

# Student ki search request
class SearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0  # Default 5 km range

# --- IN-MEMORY DATABASE (Testing ke liye) ---
teachers_db = [
    {"id": 1, "name": "Rahul Sharma", "subject": "Maths", "latitude": 22.7196, "longitude": 75.8577}, # Indore center
    {"id": 2, "name": "Priya Singh", "subject": "Physics", "latitude": 22.7250, "longitude": 75.8600}, # Thoda door
    {"id": 3, "name": "Amit Verma", "subject": "Chemistry", "latitude": 28.7041, "longitude": 77.1025}, # Delhi (Far away)
]

# --- HELPER FUNCTION: Distance Calculation (Haversine Formula) ---
def calculate_distance(lat1, lon1, lat2, lon2):
    # Do locations ke beech ki doori nikalne ka formula
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) * math.sin(d_lon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Welcome to Tutor Finder API"}

@app.get("/teachers", response_model=List[Teacher])
def get_all_teachers():
    return teachers_db

@app.post("/teachers/nearby")
def find_nearby_teachers(request: SearchRequest):
    """
    Ye endpoint student ki location lega aur radius ke andar
    aane wale teachers ki list dega.
    """
    nearby_teachers = []
    
    for teacher in teachers_db:
        dist = calculate_distance(
            request.latitude, 
            request.longitude, 
            teacher["latitude"], 
            teacher["longitude"]
        )
        
        if dist <= request.radius_km:
            # Teacher ke data me distance bhi add kar dete hain info ke liye
            teacher_with_dist = teacher.copy()
            teacher_with_dist['distance_km'] = round(dist, 2)
            nearby_teachers.append(teacher_with_dist)
            
    if not nearby_teachers:
        return {"message": "No teachers found in this area", "data": []}
        
    return {"count": len(nearby_teachers), "data": nearby_teachers}