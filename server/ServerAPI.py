from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Events Backend (Demo)")

# מאפשר קריאות מכל מקור (בדמו)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Halls endpoint ---
@app.get("/DB/halls/get_halls")
async def get_halls():
    """החזרת כל האולמות (דוגמה)"""
    halls = [
        {"id": 1, "name": "Grand Hall", "capacity": 300, "location": "Tel Aviv"},
        {"id": 2, "name": "Small Hall", "capacity": 80, "location": "Jerusalem"},
        {"id": 3, "name": "Beachfront Hall", "capacity": 150, "location": "Haifa"}
    ]
    return halls
