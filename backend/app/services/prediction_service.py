from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

class PredictionService:
    def __init__(self):
        # In a real app, we would inject DB session here to query historical sales
        pass

    async def get_daily_sales_prediction(self, date: datetime, branch_id: int) -> Dict:
        """
        Generate a sales prediction for a specific date using simple heuristics.
        Real implementation would use Moving Average of last 3 weeks.
        """
        
        # 1. Base Metrics (Mocked based on "Avg Day")
        base_covers = 150  # Average customers
        base_revenue = 15000.0  # Average revenue
        
        # 2. Day of Week Factor
        # 0=Mon, 6=Sun
        dow = date.weekday()
        day_factors = {
            0: 0.8, # Mon (Slow)
            1: 0.9, # Tue
            2: 1.0, # Wed (Avg)
            3: 1.0, # Thu
            4: 1.3, # Fri (Busy)
            5: 1.5, # Sat (Peak)
            6: 1.2  # Sun
        }
        factor = day_factors.get(dow, 1.0)
        
        # 3. Weather Simulation (Mock)
        # In real app, we'd fetch forecast API
        weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy"]
        weather = random.choice(weather_conditions)
        
        weather_impact = 0.0
        if weather == "Rainy":
            weather_impact = -0.15 # 15% drop
        elif weather == "Snowy":
            weather_impact = -0.30 # 30% drop
            
        # 4. Calculate Final Prediction
        final_modifier = factor * (1.0 + weather_impact)
        
        predicted_revenue = base_revenue * final_modifier
        predicted_covers = int(base_covers * final_modifier)
        
        # Ingredients Prediction (Simplified BOM)
        # Assume 1kg Cigkofte per 1500 TL revenue (just a ratio)
        kofte_kg = round(predicted_revenue / 1500, 1)
        lavash_packs = int(predicted_covers * 1.2) # 1.2 per customer
        lettuce_kg = round(predicted_covers * 0.1, 1) # 100g per customer
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "day_name": date.strftime("%A"),
            "weather_forecast": weather,
            "prediction": {
                "revenue": round(predicted_revenue, 2),
                "covers": predicted_covers,
                "confidence_score": 0.85
            },
            "prep_advice": {
                "cig_kofte_kg": kofte_kg,
                "lavash_packs": lavash_packs,
                "lettuce_kg": lettuce_kg
            },
            "factors": {
                "day_factor": factor,
                "weather_impact": weather_impact
            }
        }
