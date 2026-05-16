"""
CampusPool — Core DAA Algorithms
=================================
1. Haversine distance          — real-world km between two coordinates
2. Fare calculator             — based on vehicle mileage, not fixed rate
3. Greedy matching             — O(n^2), pairs passengers with nearest rider
4. Dijkstra shortest path      — optimal route: rider -> pickup -> college
"""

import math
import heapq
import networkx as nx
import os
from dotenv import load_dotenv

load_dotenv()

FUEL_PRICES = {
    'petrol': float(os.getenv('FUEL_PRICE_PETROL', 103.0)),
    'diesel': float(os.getenv('FUEL_PRICE_DIESEL', 90.0)),
}
MAX_DETOUR_KM = 1.5


# ─────────────────────────────────────────────
# 1. HAVERSINE DISTANCE
# ─────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─────────────────────────────────────────────
# 2. FARE CALCULATOR
# ─────────────────────────────────────────────

def calculate_fare(distance_km: float, mileage_kmpl: float,
                   fuel_type: str = 'petrol', riders: int = 2) -> dict:
    """
    Fare = (distance / mileage) * fuel_price / total_riders
    Rider cannot charge more than this calculated amount.
    """
    if mileage_kmpl <= 0:
        raise ValueError('mileage_kmpl must be > 0')

    fuel_price   = FUEL_PRICES.get(fuel_type, FUEL_PRICES['petrol'])
    fuel_used    = distance_km / mileage_kmpl
    total_cost   = fuel_used * fuel_price
    per_rider    = total_cost / riders

    return {
        'distance_km':    round(distance_km, 2),
        'fuel_used_L':    round(fuel_used, 3),
        'total_cost':     round(total_cost, 2),
        'passenger_pays': round(per_rider, 2),
        'breakdown':      (
            f"{distance_km:.1f}km ÷ {mileage_kmpl}kmpl "
            f"× ₹{fuel_price}/L ÷ {riders} riders = ₹{per_rider:.0f}"
        )
    }


# ─────────────────────────────────────────────
# 3. GREEDY MATCHING ALGORITHM  O(n^2)
# ─────────────────────────────────────────────

def greedy_match(riders: list, passengers: list,
                 college_lat: float, college_lon: float) -> list:
    """
    Greedy approach:
      - Sort passengers by distance to college (priority = closest first)
      - For each passenger, find the nearest available rider
        whose detour is within MAX_DETOUR_KM
      - Time complexity: O(n^2) where n = number of students
    
    riders: list of dicts with keys: id, lat, lon, vehicle (name, mileage_kmpl, fuel_type)
    passengers: list of dicts with keys: id, lat, lon
    Returns: list of match dicts
    """
    matched     = []
    used_riders = set()

    # Sort passengers by proximity to college — greedy priority
    passengers_sorted = sorted(
        passengers,
        key=lambda p: haversine(p['lat'], p['lon'], college_lat, college_lon)
    )

    for passenger in passengers_sorted:
        best_rider  = None
        best_detour = float('inf')

        for rider in riders:
            if rider['id'] in used_riders:
                continue

            # How far rider deviates from direct path to pick up passenger
            direct_dist = haversine(rider['lat'], rider['lon'],
                                    college_lat, college_lon)
            via_pass    = (haversine(rider['lat'], rider['lon'],
                                     passenger['lat'], passenger['lon']) +
                           haversine(passenger['lat'], passenger['lon'],
                                     college_lat, college_lon))
            detour = via_pass - direct_dist

            if detour <= MAX_DETOUR_KM and detour < best_detour:
                best_detour = detour
                best_rider  = rider

        if best_rider:
            used_riders.add(best_rider['id'])

            # Calculate total route distance: rider -> passenger -> college
            route_distance = (
                haversine(best_rider['lat'], best_rider['lon'],
                          passenger['lat'], passenger['lon']) +
                haversine(passenger['lat'], passenger['lon'],
                          college_lat, college_lon)
            )

            vehicle   = best_rider.get('vehicle', {})
            mileage   = vehicle.get('mileage_kmpl', 40)
            fuel_type = vehicle.get('fuel_type', 'petrol')
            fare      = calculate_fare(route_distance, mileage, fuel_type, riders=2)

            matched.append({
                'rider':          best_rider,
                'passenger':      passenger,
                'detour_km':      round(best_detour, 3),
                'route_distance': round(route_distance, 2),
                'fare':           fare
            })

    return matched


# ─────────────────────────────────────────────
# 4. DIJKSTRA SHORTEST PATH
# ─────────────────────────────────────────────

def build_location_graph(locations: list) -> nx.Graph:
    """
    Build a complete weighted graph from a list of locations.
    locations: list of dicts with keys: id, lat, lon
    Edge weight = haversine distance in km
    """
    G = nx.Graph()
    for loc in locations:
        G.add_node(loc['id'], lat=loc['lat'], lon=loc['lon'])

    for i, loc1 in enumerate(locations):
        for loc2 in locations[i + 1:]:
            dist = haversine(loc1['lat'], loc1['lon'],
                             loc2['lat'], loc2['lon'])
            G.add_edge(loc1['id'], loc2['id'], weight=round(dist, 4))
    return G


def dijkstra_route(G: nx.Graph, start_id, via_id, end_id) -> dict:
    """
    Find shortest path: start -> via -> end using Dijkstra.
    Returns total distance and full node path.
    Time complexity: O((V + E) log V)
    """
    try:
        dist1  = nx.dijkstra_path_length(G, start_id, via_id,  weight='weight')
        dist2  = nx.dijkstra_path_length(G, via_id,   end_id,  weight='weight')
        path1  = nx.dijkstra_path(G, start_id, via_id,  weight='weight')
        path2  = nx.dijkstra_path(G, via_id,   end_id,  weight='weight')
        full   = path1 + path2[1:]  # remove duplicate mid node
        return {
            'total_km': round(dist1 + dist2, 3),
            'path':     full,
            'segment1': round(dist1, 3),
            'segment2': round(dist2, 3)
        }
    except nx.NetworkXNoPath:
        return {'error': 'No path found', 'total_km': 0, 'path': []}


# ─────────────────────────────────────────────
# 5. FIND NEARBY RIDES  (called from /api/rides/find)
# ─────────────────────────────────────────────

def find_nearby_rides(passenger_lat: float, passenger_lon: float,
                      all_rides: list, max_km: float = 2.0) -> list:
    """
    Filter rides whose origin is within max_km of passenger location.
    Sort by proximity. Returns list of rides with distance added.
    """
    nearby = []
    for ride in all_rides:
        dist = haversine(passenger_lat, passenger_lon,
                         ride['origin']['lat'], ride['origin']['lon'])
        if dist <= max_km:
            ride['distance_from_you'] = round(dist, 2)
            nearby.append(ride)

    nearby.sort(key=lambda r: r['distance_from_you'])
    return nearby
