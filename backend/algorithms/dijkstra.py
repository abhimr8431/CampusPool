"""
CampusPool — Dijkstra Shortest Path
=====================================
Finds optimal route: Rider location → Passenger pickup → College

Time Complexity  : O((V + E) log V)
Space Complexity : O(V)

Used in:
  - routes/rides.py  → when showing route details to passenger
  - daa_demo         → visualization of matched routes
"""

import heapq
import math
import networkx as nx


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Real-world distance in km between two GPS coordinates."""
    R    = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_graph(locations: list) -> nx.Graph:
    """
    Build a complete weighted graph from student locations.

    locations: list of dicts → {id, lat, lon, name}
    Edge weight = haversine distance in km between every pair.

    Returns: networkx Graph
    """
    G = nx.Graph()

    for loc in locations:
        G.add_node(loc['id'], lat=loc['lat'], lon=loc['lon'], name=loc.get('name', ''))

    for i, loc1 in enumerate(locations):
        for loc2 in locations[i + 1:]:
            dist = haversine(loc1['lat'], loc1['lon'], loc2['lat'], loc2['lon'])
            G.add_edge(loc1['id'], loc2['id'], weight=round(dist, 4))

    return G


def dijkstra_shortest_path(G: nx.Graph, start_id, end_id) -> dict:
    """
    Standard Dijkstra from start to end.
    Time Complexity: O((V + E) log V)

    Returns dict with total distance and node path.
    """
    try:
        dist = nx.dijkstra_path_length(G, start_id, end_id, weight='weight')
        path = nx.dijkstra_path(G, start_id, end_id, weight='weight')
        return {
            'total_km': round(dist, 3),
            'path':     path,
            'found':    True
        }
    except nx.NetworkXNoPath:
        return {'total_km': 0, 'path': [], 'found': False}
    except nx.NodeNotFound as e:
        return {'total_km': 0, 'path': [], 'found': False, 'error': str(e)}


def dijkstra_via_point(G: nx.Graph, start_id, via_id, end_id) -> dict:
    """
    Dijkstra with a mandatory stop (pickup point).
    Route: Rider → Passenger → College

    Runs Dijkstra twice:
      1. start → via   (rider home to passenger pickup)
      2. via   → end   (passenger pickup to college)

    Time Complexity: O(2 * (V + E) log V)
    """
    try:
        # Segment 1: rider → passenger pickup
        dist1 = nx.dijkstra_path_length(G, start_id, via_id, weight='weight')
        path1 = nx.dijkstra_path(G, start_id, via_id, weight='weight')

        # Segment 2: passenger pickup → college
        dist2 = nx.dijkstra_path_length(G, via_id, end_id, weight='weight')
        path2 = nx.dijkstra_path(G, via_id, end_id, weight='weight')

        full_path = path1 + path2[1:]   # remove duplicate via node

        return {
            'total_km':   round(dist1 + dist2, 3),
            'segment1_km': round(dist1, 3),   # rider → pickup
            'segment2_km': round(dist2, 3),   # pickup → college
            'path':        full_path,
            'found':       True
        }
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        return {
            'total_km': 0, 'path': [], 'found': False, 'error': str(e)
        }


def manual_dijkstra(graph_dict: dict, start) -> dict:
    """
    Pure Python Dijkstra (no networkx) — for DAA presentation.
    Shows the algorithm working with a priority queue (min-heap).

    graph_dict format:
    {
      'A': {'B': 1.2, 'C': 3.5},
      'B': {'A': 1.2, 'C': 2.1},
      ...
    }

    Time Complexity : O((V + E) log V)
    Space Complexity: O(V)
    """
    distances  = {node: float('inf') for node in graph_dict}
    distances[start] = 0
    previous   = {node: None for node in graph_dict}
    heap       = [(0, start)]
    visited    = set()

    while heap:
        curr_dist, curr_node = heapq.heappop(heap)

        if curr_node in visited:
            continue
        visited.add(curr_node)

        for neighbor, weight in graph_dict.get(curr_node, {}).items():
            new_dist = curr_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous[neighbor]  = curr_node
                heapq.heappush(heap, (new_dist, neighbor))

    return {'distances': distances, 'previous': previous}


def reconstruct_path(previous: dict, start, end) -> list:
    """Reconstruct shortest path from previous[] map."""
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path if path[0] == start else []