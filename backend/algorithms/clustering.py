"""
CampusPool — Zone Clustering Algorithm
========================================
Groups students into geographic zones/clusters before matching.
This reduces the matching problem from O(n²) to O(k × (n/k)²)
where k = number of clusters.

Algorithm: K-Means style clustering using GPS coordinates.

Why clustering helps:
  - 500 students → direct greedy matching = 250,000 comparisons
  - With 10 zones → 10 × 2,500 = 25,000 comparisons (10× faster)

Used in:
  - routes/rides.py  → group nearby riders before matching
  - daa_demo         → show zone visualization
"""

import math
import random
from typing import List, Dict


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R    = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─────────────────────────────────────────────
# 1. SIMPLE RADIUS CLUSTERING
#    Group students within a fixed radius of each other
#    Used for real-time "find nearby rides"
# ─────────────────────────────────────────────

def cluster_by_radius(students: list, radius_km: float = 2.0) -> list:
    """
    Groups students who live within radius_km of each other.

    Time Complexity : O(n²)
    Space Complexity: O(n)

    students: list of dicts → {id, lat, lon, name, is_rider}
    Returns : list of clusters, each cluster is a list of students
    """
    clustered = set()
    clusters  = []

    for student in students:
        if student['id'] in clustered:
            continue

        cluster = [student]
        clustered.add(student['id'])

        for other in students:
            if other['id'] in clustered:
                continue
            dist = haversine(
                student['lat'], student['lon'],
                other['lat'],   other['lon']
            )
            if dist <= radius_km:
                cluster.append(other)
                clustered.add(other['id'])

        clusters.append(cluster)

    return clusters


# ─────────────────────────────────────────────
# 2. K-MEANS GEOGRAPHIC CLUSTERING
#    Divides city into k zones, assigns each student
#    to the nearest zone center
# ─────────────────────────────────────────────

def kmeans_cluster(students: list, k: int = 5,
                   max_iterations: int = 100) -> dict:
    """
    K-Means clustering on GPS coordinates.
    Divides students into k geographic zones.

    Time Complexity : O(k × n × iterations)
    Space Complexity: O(k + n)

    Returns: {
      'clusters': {zone_id: [students]},
      'centroids': [{lat, lon}],
      'iterations': n
    }
    """
    if len(students) < k:
        k = len(students)

    # Step 1: Random initial centroids
    centroids = random.sample(
        [{'lat': s['lat'], 'lon': s['lon']} for s in students], k
    )

    assignments = {}
    iterations  = 0

    for _ in range(max_iterations):
        iterations += 1
        new_assignments = {}

        # Step 2: Assign each student to nearest centroid
        for student in students:
            min_dist  = float('inf')
            nearest_k = 0
            for i, centroid in enumerate(centroids):
                dist = haversine(
                    student['lat'], student['lon'],
                    centroid['lat'], centroid['lon']
                )
                if dist < min_dist:
                    min_dist  = dist
                    nearest_k = i
            new_assignments[student['id']] = nearest_k

        # Step 3: Check convergence
        if new_assignments == assignments:
            break
        assignments = new_assignments

        # Step 4: Recalculate centroids
        for i in range(k):
            members = [s for s in students if assignments[s['id']] == i]
            if members:
                centroids[i] = {
                    'lat': sum(s['lat'] for s in members) / len(members),
                    'lon': sum(s['lon'] for s in members) / len(members)
                }

    # Build cluster dict
    clusters = {i: [] for i in range(k)}
    for student in students:
        zone = assignments.get(student['id'], 0)
        clusters[zone].append(student)

    return {
        'clusters':   clusters,
        'centroids':  centroids,
        'iterations': iterations,
        'k':          k
    }


# ─────────────────────────────────────────────
# 3. ZONE-BASED PRE-FILTER
#    Before running Greedy matching, filter only
#    students in the same zone — reduces comparisons
# ─────────────────────────────────────────────

def get_zone_for_location(lat: float, lon: float,
                          centroids: list) -> int:
    """Find which zone a new location belongs to."""
    min_dist = float('inf')
    zone     = 0
    for i, centroid in enumerate(centroids):
        dist = haversine(lat, lon, centroid['lat'], centroid['lon'])
        if dist < min_dist:
            min_dist = dist
            zone     = i
    return zone


def filter_students_by_zone(passenger_lat: float, passenger_lon: float,
                             all_students: list,
                             centroids: list,
                             expand_to_adjacent: bool = True) -> list:
    """
    Returns only students in same zone as passenger.
    If expand_to_adjacent=True, also includes neighboring zones
    to avoid missing nearby students near zone borders.
    """
    passenger_zone = get_zone_for_location(
        passenger_lat, passenger_lon, centroids
    )

    if not expand_to_adjacent:
        return [s for s in all_students
                if get_zone_for_location(s['lat'], s['lon'],
                                         centroids) == passenger_zone]

    # Include 2 closest zones
    zone_distances = []
    for i, centroid in enumerate(centroids):
        dist = haversine(passenger_lat, passenger_lon,
                         centroid['lat'], centroid['lon'])
        zone_distances.append((dist, i))
    zone_distances.sort()
    nearby_zones = {z[1] for z in zone_distances[:2]}

    return [s for s in all_students
            if get_zone_for_location(s['lat'], s['lon'],
                                     centroids) in nearby_zones]


# ─────────────────────────────────────────────
# 4. QUICK TEST
# ─────────────────────────────────────────────

if __name__ == '__main__':
    # Sample students near Bangalore
    test_students = [
        {'id': 1, 'lat': 12.9352, 'lon': 77.6245, 'name': 'Aarav',  'is_rider': True},
        {'id': 2, 'lat': 12.9512, 'lon': 77.5987, 'name': 'Priya',  'is_rider': True},
        {'id': 3, 'lat': 12.9180, 'lon': 77.6102, 'name': 'Suresh', 'is_rider': True},
        {'id': 4, 'lat': 12.9370, 'lon': 77.6190, 'name': 'Sneha',  'is_rider': False},
        {'id': 5, 'lat': 12.9490, 'lon': 77.5950, 'name': 'Rahul',  'is_rider': False},
        {'id': 6, 'lat': 12.9160, 'lon': 77.6080, 'name': 'Meera',  'is_rider': False},
    ]

    print('--- Radius Clustering (2km) ---')
    clusters = cluster_by_radius(test_students, radius_km=2.0)
    for i, c in enumerate(clusters):
        print(f'  Cluster {i+1}: {[s["name"] for s in c]}')

    print('\n--- K-Means Clustering (k=2) ---')
    result = kmeans_cluster(test_students, k=2)
    for zone, members in result['clusters'].items():
        print(f'  Zone {zone}: {[s["name"] for s in members]}')
    print(f'  Converged in {result["iterations"]} iterations')