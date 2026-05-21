"""
CampusPool — Fare Calculator
==============================
Calculates fuel cost split based on:
  - Actual vehicle mileage (not a fixed rate)
  - Real-time fuel price
  - Number of riders sharing

Formula:
  fuel_used  = distance_km / mileage_kmpl
  total_cost = fuel_used × fuel_price_per_litre
  per_rider  = total_cost / number_of_riders

Used in:
  - algorithms/matching.py  → during greedy matching
  - routes/rides.py         → when posting/finding rides
  - routes/requests.py      → when passenger sends request
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Current fuel prices in ₹ per litre
# Update these manually or fetch from a fuel price API
FUEL_PRICES = {
    'petrol': float(os.getenv('FUEL_PRICE_PETROL', 103.0)),
    'diesel': float(os.getenv('FUEL_PRICE_DIESEL', 90.0)),
    'cng':    float(os.getenv('FUEL_PRICE_CNG',    78.0)),
}

# Default mileage if rider hasn't set their vehicle mileage
DEFAULT_MILEAGE = {
    'bike':    45.0,   # generic bike
    'scooter': 50.0,   # generic scooter
    'car':     18.0,   # generic car
}


def calculate_fare(
    distance_km:   float,
    mileage_kmpl:  float,
    fuel_type:     str = 'petrol',
    riders:        int = 2
) -> dict:
    """
    Main fare calculation function.
    Rider cannot charge more than passenger_pays amount.

    Args:
        distance_km   : total route distance
        mileage_kmpl  : rider's actual vehicle mileage
        fuel_type     : petrol / diesel / cng
        riders        : total people in vehicle (rider + passengers)

    Returns:
        dict with full fare breakdown
    """
    if mileage_kmpl <= 0:
        raise ValueError('mileage_kmpl must be greater than 0')
    if distance_km < 0:
        raise ValueError('distance_km cannot be negative')
    if riders < 2:
        riders = 2   # minimum 2 (rider + 1 passenger)

    fuel_price   = FUEL_PRICES.get(fuel_type, FUEL_PRICES['petrol'])
    fuel_used    = distance_km / mileage_kmpl
    total_cost   = fuel_used * fuel_price
    per_rider    = total_cost / riders

    return {
        'distance_km':      round(distance_km, 2),
        'mileage_kmpl':     mileage_kmpl,
        'fuel_type':        fuel_type,
        'fuel_price_per_L': fuel_price,
        'fuel_used_L':      round(fuel_used, 3),
        'total_cost':       round(total_cost, 2),
        'passenger_pays':   round(per_rider, 2),
        'riders':           riders,
        'breakdown':        (
            f"{distance_km:.1f}km ÷ {mileage_kmpl}kmpl "
            f"× ₹{fuel_price}/L ÷ {riders} riders "
            f"= ₹{round(per_rider)}"
        )
    }


def get_fare_estimate(
    distance_km:  float,
    vehicle_name: str,
    mileage_kmpl: float = 0,
    fuel_type:    str   = 'petrol'
) -> dict:
    """
    Estimate fare when exact mileage isn't known.
    Falls back to default mileage based on vehicle name keywords.
    """
    if mileage_kmpl <= 0:
        name = vehicle_name.lower()
        if any(w in name for w in ['activa', 'scooty', 'jupiter', 'pep', 'access']):
            mileage_kmpl = DEFAULT_MILEAGE['scooter']
        elif any(w in name for w in ['swift', 'wagonr', 'alto', 'baleno', 'i20']):
            mileage_kmpl = DEFAULT_MILEAGE['car']
        else:
            mileage_kmpl = DEFAULT_MILEAGE['bike']

    return calculate_fare(distance_km, mileage_kmpl, fuel_type)


def max_allowed_fare(distance_km: float, mileage_kmpl: float,
                     fuel_type: str = 'petrol') -> float:
    """
    Returns the maximum a rider is allowed to charge per passenger.
    This is enforced — rider cannot charge more than this.
    """
    result = calculate_fare(distance_km, mileage_kmpl, fuel_type, riders=2)
    return result['passenger_pays']


def update_fuel_price(fuel_type: str, new_price: float):
    """
    Update fuel price dynamically.
    Call this daily or when prices change.
    """
    if fuel_type not in FUEL_PRICES:
        raise ValueError(f'Unknown fuel type: {fuel_type}')
    FUEL_PRICES[fuel_type] = new_price
    print(f'Updated {fuel_type} price to ₹{new_price}/L')