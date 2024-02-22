from app import app
from pathlib import Path
from models.models import Location

BASE_DIR =  Path(__file__).resolve(strict=True).parent
STATIC_DIR = BASE_DIR / "static"
FILES_DIR = STATIC_DIR / "files"

# Dicc english months
DICC_MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

# Locations
with app.app_context():
    LOCATIONS = {location.id: location.place for location in Location.get_all()}
