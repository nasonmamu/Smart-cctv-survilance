# gps.py
import random

class GPS:
    def get_coordinates(self):
        # Mock coordinates for demonstration
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        return lat, lon
