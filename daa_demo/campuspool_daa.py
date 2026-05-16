"""
CampusPool — Complete DAA Presentation Script
==============================================
Run this standalone to demo all algorithms for your college presentation.

Algorithms demonstrated:
  1. Haversine Distance       — real world distance between GPS points
  2. Greedy Matching          — O(n^2) passenger-rider matching
  3. Dijkstra Shortest Path   — O((V+E) log V) optimal route finding
  4. Fare Calculator          — vehicle-mileage based cost splitting

No need for a separate graph file — networkx handles graph internals.
This script generates 3 output images for your presentation.
"""

import math
import heapq
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
COLLEGE      = {'id': 0, 'lat': 12.9237, 'lon': 77.4988, 'name': 'RVCE'}
MAX_DETOUR   = 1.5      # km — max detour a rider will take
FUEL_PRICES  = {'petrol': 103.0, 'diesel': 90.0}
DARK_BG      = '#0f1117'
CARD_BG      = '#1a1d27'
GREEN        = '#1D9E75'
BLUE         = '#378ADD'
RED          = '#E24B4A'
YELLOW       = '#FAC775'
GRAY         = '#555966'
WHITE        = '#f0f0ea'

# ─────────────────────────────────────────────
# SAMPLE DATA  (Bangalore coords near RVCE)
# ─────────────────────────────────────────────
@dataclass
class Vehicle:
    name:         str
    mileage_kmpl: float
    fuel_type:    str = 'petrol'

@dataclass
class Student:
    id:       int
    name:     str
    lat:      float
    lon:      float
    is_rider: bool
    vehicle:  Optional[Vehicle] = None
    matched:  Optional[int]     = None

students = [
    Student(1,  'Aarav R',   12.9352, 77.6245, True,  Vehicle('Honda Activa', 40)),
    Student(2,  'Priya K',   12.9512, 77.5987, True,  Vehicle('Scooty Pep+',  55)),
    Student(3,  'Suresh M',  12.9180, 77.6102, True,  Vehicle('Pulsar 150',   45)),
    Student(4,  'Divya N',   12.9401, 77.5801, True,  Vehicle('TVS Jupiter',  50)),
    Student(5,  'Sneha T',   12.9370, 77.6190, False),
    Student(6,  'Rahul S',   12.9490, 77.5950, False),
    Student(7,  'Meera P',   12.9160, 77.6080, False),
    Student(8,  'Kiran B',   12.9420, 77.5820, False),
    Student(9,  'Ananya G',  12.9340, 77.6150, False),
    Student(10, 'Vijay L',   12.9530, 77.6010, False),
]

# ─────────────────────────────────────────────
# ALGORITHM 1: HAVERSINE DISTANCE
# ─────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2) -> float:
    """Real-world distance in km between two GPS coordinates."""
    R    = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat/2)**2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ─────────────────────────────────────────────
# ALGORITHM 2: FARE CALCULATOR
# ─────────────────────────────────────────────
def calculate_fare(dist_km, mileage_kmpl, fuel_type='petrol', riders=2):
    price      = FUEL_PRICES[fuel_type]
    fuel_used  = dist_km / mileage_kmpl
    total      = fuel_used * price
    per_rider  = total / riders
    return {
        'distance_km':    round(dist_km, 2),
        'fuel_used_L':    round(fuel_used, 3),
        'total_cost':     round(total, 2),
        'passenger_pays': round(per_rider, 2),
        'formula':        f'{dist_km:.1f} ÷ {mileage_kmpl} × ₹{price} ÷ {riders}'
    }

# ─────────────────────────────────────────────
# ALGORITHM 3: GREEDY MATCHING  O(n^2)
# ─────────────────────────────────────────────
def greedy_match(students):
    """
    Greedy algorithm:
    1. Sort passengers by distance to college (priority)
    2. For each passenger, find nearest rider with min detour <= MAX_DETOUR
    3. Mark both as matched, move to next
    Time Complexity: O(n^2)
    Space Complexity: O(n)
    """
    riders     = [s for s in students if s.is_rider]
    passengers = [s for s in students if not s.is_rider]
    used       = set()
    matches    = []

    # Step 1: Sort passengers — greedy priority (closest to college first)
    passengers.sort(key=lambda p: haversine(p.lat, p.lon, COLLEGE['lat'], COLLEGE['lon']))

    for passenger in passengers:
        best_rider  = None
        best_detour = float('inf')

        # Step 2: Find best rider for this passenger
        for rider in riders:
            if rider.id in used:
                continue
            direct  = haversine(rider.lat, rider.lon, COLLEGE['lat'], COLLEGE['lon'])
            via_p   = (haversine(rider.lat, rider.lon, passenger.lat, passenger.lon) +
                       haversine(passenger.lat, passenger.lon, COLLEGE['lat'], COLLEGE['lon']))
            detour  = via_p - direct

            if detour <= MAX_DETOUR and detour < best_detour:
                best_detour = detour
                best_rider  = rider

        # Step 3: Record match
        if best_rider:
            best_rider.matched  = passenger.id
            passenger.matched   = best_rider.id
            used.add(best_rider.id)

            route_dist = (haversine(best_rider.lat, best_rider.lon,
                                    passenger.lat, passenger.lon) +
                          haversine(passenger.lat, passenger.lon,
                                    COLLEGE['lat'], COLLEGE['lon']))
            fare = calculate_fare(route_dist, best_rider.vehicle.mileage_kmpl,
                                  best_rider.vehicle.fuel_type)
            matches.append({
                'rider':     best_rider,
                'passenger': passenger,
                'detour':    round(best_detour, 3),
                'route_km':  round(route_dist, 2),
                'fare':      fare
            })
    return matches

# ─────────────────────────────────────────────
# ALGORITHM 4: DIJKSTRA SHORTEST PATH
# ─────────────────────────────────────────────
def build_graph(students) -> nx.Graph:
    """
    Build complete weighted graph.
    Nodes = student locations + college
    Edges = haversine distance between every pair
    """
    G     = nx.Graph()
    nodes = [(s.id, s.lat, s.lon) for s in students]
    nodes.append((0, COLLEGE['lat'], COLLEGE['lon']))   # node 0 = college

    for nid, lat, lon in nodes:
        G.add_node(nid, lat=lat, lon=lon)

    for i, (id1, lat1, lon1) in enumerate(nodes):
        for id2, lat2, lon2 in nodes[i+1:]:
            G.add_edge(id1, id2, weight=round(haversine(lat1, lon1, lat2, lon2), 4))
    return G

def dijkstra_route(G, start, via, end):
    """
    Optimal route: start -> via -> end
    Uses networkx Dijkstra internally (priority queue / min-heap)
    Time Complexity: O((V + E) log V)
    """
    d1  = nx.dijkstra_path_length(G, start, via, weight='weight')
    d2  = nx.dijkstra_path_length(G, via,   end, weight='weight')
    p1  = nx.dijkstra_path(G, start, via, weight='weight')
    p2  = nx.dijkstra_path(G, via,   end, weight='weight')
    return round(d1 + d2, 3), p1 + p2[1:]

# ─────────────────────────────────────────────
# PRINT RESULTS TO TERMINAL
# ─────────────────────────────────────────────
def print_results(matches, G):
    sep = '─' * 60
    print(f'\n{sep}')
    print('   CAMPUSPOOL — DAA Algorithm Results')
    print(sep)
    print(f'  Total students : {len(students)}')
    print(f'  Riders         : {sum(s.is_rider for s in students)}')
    print(f'  Passengers     : {sum(not s.is_rider for s in students)}')
    print(f'  Matches made   : {len(matches)}')
    print(f'  Algorithm      : Greedy O(n²) + Dijkstra O((V+E)logV)')
    print(f'  Max detour     : {MAX_DETOUR} km')
    print(sep)

    for i, m in enumerate(matches, 1):
        rider     = m['rider']
        passenger = m['passenger']
        dist, path = dijkstra_route(G, rider.id, passenger.id, 0)

        print(f'\n  ✓ Match #{i}')
        print(f'    Rider     : {rider.name} — {rider.vehicle.name} ({rider.vehicle.mileage_kmpl} kmpl)')
        print(f'    Passenger : {passenger.name}')
        print(f'    Detour    : {m["detour"]} km')
        print(f'    Route     : Rider({rider.id}) → Pickup({passenger.id}) → RVCE(0)')
        print(f'    Dijkstra path nodes: {" → ".join(str(n) for n in path)}')
        print(f'    Total dist: {m["route_km"]} km')
        f = m['fare']
        print(f'    Fare      : {f["formula"]}')
        print(f'    Fuel used : {f["fuel_used_L"]} L  |  Total: ₹{f["total_cost"]}')
        print(f'    Passenger pays: ₹{f["passenger_pays"]}')

    unmatched = [s for s in students if not s.is_rider and s.matched is None]
    if unmatched:
        print(f'\n  ✗ Unmatched ({len(unmatched)}): {", ".join(s.name for s in unmatched)}')
        print(f'    (No rider within {MAX_DETOUR}km detour — increase MAX_DETOUR to match more)')
    print(f'\n{sep}\n')

# ─────────────────────────────────────────────
# VISUALIZATION 1: MAP + MATCHED ROUTES
# ─────────────────────────────────────────────
def plot_map(matches):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle('CampusPool — Student Locations & Matched Routes',
                 color=WHITE, fontsize=14, fontweight='bold', y=1.01)

    matched_r = {m['rider'].id for m in matches}
    matched_p = {m['passenger'].id for m in matches}

    for ax, title in [(ax1, 'All Students'), (ax2, 'Matched Routes')]:
        ax.set_facecolor(CARD_BG)
        ax.set_title(title, color=WHITE, fontsize=12, pad=8)
        ax.tick_params(colors=WHITE, labelsize=7)
        ax.set_xlabel('Longitude', color=WHITE, fontsize=8)
        ax.set_ylabel('Latitude',  color=WHITE, fontsize=8)
        for sp in ax.spines.values(): sp.set_edgecolor('#333')

    # Left: all students
    for s in students:
        if s.is_rider:
            c = GREEN if s.id in matched_r else GRAY
            ax1.scatter(s.lon, s.lat, c=c, s=130, marker='^', zorder=4,
                        edgecolors=WHITE, linewidths=0.5)
        else:
            c = BLUE if s.id in matched_p else GRAY
            ax1.scatter(s.lon, s.lat, c=c, s=90, marker='o', zorder=3,
                        edgecolors=WHITE, linewidths=0.5)
        ax1.annotate(s.name.split()[0], (s.lon, s.lat),
                     xytext=(4, 4), textcoords='offset points',
                     fontsize=7, color=WHITE, alpha=0.85)

    ax1.scatter(COLLEGE['lon'], COLLEGE['lat'], c=RED, s=220,
                marker='*', zorder=5, edgecolors=WHITE, linewidths=0.8)
    ax1.annotate('RVCE', (COLLEGE['lon'], COLLEGE['lat']),
                 xytext=(5, 5), textcoords='offset points',
                 fontsize=8, color=RED, fontweight='bold')

    legend = [
        mpatches.Patch(color=GREEN, label='Matched rider'),
        mpatches.Patch(color=BLUE,  label='Matched passenger'),
        mpatches.Patch(color=GRAY,  label='Unmatched'),
        mpatches.Patch(color=RED,   label='RVCE college'),
    ]
    ax1.legend(handles=legend, facecolor=CARD_BG, edgecolor='#444',
               labelcolor=WHITE, fontsize=7, loc='lower left')

    # Right: matched routes
    cmap = plt.cm.get_cmap('Set2', max(len(matches), 1))
    for idx, m in enumerate(matches):
        r = m['rider']
        p = m['passenger']
        c = cmap(idx)
        # Draw route line
        ax2.plot([r.lon, p.lon, COLLEGE['lon']],
                 [r.lat, p.lat, COLLEGE['lat']],
                 '-', color=c, linewidth=2, alpha=0.85, zorder=2)
        # Arrowhead: rider -> passenger
        ax2.annotate('', xy=(p.lon, p.lat), xytext=(r.lon, r.lat),
                     arrowprops=dict(arrowstyle='->', color=c, lw=1.5))
        ax2.annotate('', xy=(COLLEGE['lon'], COLLEGE['lat']),
                     xytext=(p.lon, p.lat),
                     arrowprops=dict(arrowstyle='->', color=c, lw=1.5))

        ax2.scatter(r.lon, r.lat, c=[c], s=130, marker='^',
                    zorder=4, edgecolors=WHITE, linewidths=0.5)
        ax2.scatter(p.lon, p.lat, c=[c], s=90, marker='o',
                    zorder=4, edgecolors=WHITE, linewidths=0.5)

        # Fare label
        mid_lon = (r.lon + p.lon) / 2
        mid_lat = (r.lat + p.lat) / 2
        ax2.annotate(f'₹{m["fare"]["passenger_pays"]}',
                     (mid_lon, mid_lat), fontsize=8,
                     color=YELLOW, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.2', fc=CARD_BG, alpha=0.8))
        ax2.annotate(f'{r.name.split()[0]}+{p.name.split()[0]}',
                     (r.lon, r.lat), xytext=(4, -12),
                     textcoords='offset points', fontsize=6.5, color=WHITE)

    ax2.scatter(COLLEGE['lon'], COLLEGE['lat'], c=RED, s=220,
                marker='*', zorder=5, edgecolors=WHITE, linewidths=0.8)
    ax2.annotate('RVCE', (COLLEGE['lon'], COLLEGE['lat']),
                 xytext=(5, 5), textcoords='offset points',
                 fontsize=8, color=RED, fontweight='bold')

    plt.tight_layout()
    out = 'daa_output_map.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print(f'  Saved: {out}')
    return out

# ─────────────────────────────────────────────
# VISUALIZATION 2: GRAPH STRUCTURE
# ─────────────────────────────────────────────
def plot_graph(G, matches):
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(CARD_BG)
    ax.set_title('Graph Structure — Nodes & Weighted Edges',
                 color=WHITE, fontsize=13, pad=10)

    pos = {node: (G.nodes[node]['lon'], G.nodes[node]['lat'])
           for node in G.nodes}

    # Color nodes
    node_colors = []
    node_sizes  = []
    for node in G.nodes:
        if node == 0:
            node_colors.append(RED)
            node_sizes.append(400)
        else:
            s = next((x for x in students if x.id == node), None)
            if s and s.is_rider:
                node_colors.append(GREEN)
                node_sizes.append(200)
            else:
                node_colors.append(BLUE)
                node_sizes.append(150)

    # Draw all edges faint
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#2a2d3a',
                           width=0.4, alpha=0.6)

    # Draw matched route edges brighter
    cmap = plt.cm.get_cmap('Set2', max(len(matches), 1))
    for idx, m in enumerate(matches):
        r, p = m['rider'], m['passenger']
        route_edges = [(r.id, p.id), (p.id, 0)]
        nx.draw_networkx_edges(G, pos, edgelist=route_edges, ax=ax,
                               edge_color=[cmap(idx)], width=2.5, alpha=0.9)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes)

    labels = {}
    for node in G.nodes:
        if node == 0:
            labels[node] = 'RVCE'
        else:
            s = next((x for x in students if x.id == node), None)
            labels[node] = s.name.split()[0] if s else str(node)
    nx.draw_networkx_labels(G, pos, labels, ax=ax,
                            font_size=7, font_color=WHITE)

    legend = [
        mpatches.Patch(color=GREEN, label='Rider node'),
        mpatches.Patch(color=BLUE,  label='Passenger node'),
        mpatches.Patch(color=RED,   label='College node'),
    ]
    ax.legend(handles=legend, facecolor=CARD_BG, edgecolor='#444',
              labelcolor=WHITE, fontsize=8, loc='lower left')

    ax.set_axis_off()
    plt.tight_layout()
    out = 'daa_output_graph.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print(f'  Saved: {out}')
    return out

# ─────────────────────────────────────────────
# VISUALIZATION 3: COMPLEXITY ANALYSIS
# ─────────────────────────────────────────────
def plot_complexity():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle('Algorithm Complexity Analysis', color=WHITE,
                 fontsize=13, fontweight='bold')

    n = list(range(1, 101))

    # Greedy O(n^2)
    ax1.set_facecolor(CARD_BG)
    ax1.plot(n, [x**2 for x in n], color=GREEN, lw=2.5, label='Greedy O(n²)')
    ax1.set_title('Greedy Matching — O(n²)', color=WHITE, fontsize=11)
    ax1.set_xlabel('Number of students', color=WHITE, fontsize=9)
    ax1.set_ylabel('Operations',          color=WHITE, fontsize=9)
    ax1.tick_params(colors=WHITE, labelsize=8)
    ax1.legend(facecolor=CARD_BG, labelcolor=WHITE, fontsize=9)
    for sp in ax1.spines.values(): sp.set_edgecolor('#333')

    # Dijkstra O((V+E) log V)
    ax2.set_facecolor(CARD_BG)
    dijkstra = [(x + x**2) * math.log(x+1) for x in n]
    ax2.plot(n, dijkstra, color=BLUE, lw=2.5, label="Dijkstra O((V+E)logV)")
    ax2.set_title("Dijkstra — O((V+E) log V)", color=WHITE, fontsize=11)
    ax2.set_xlabel('Number of nodes (V)',      color=WHITE, fontsize=9)
    ax2.set_ylabel('Operations',               color=WHITE, fontsize=9)
    ax2.tick_params(colors=WHITE, labelsize=8)
    ax2.legend(facecolor=CARD_BG, labelcolor=WHITE, fontsize=9)
    for sp in ax2.spines.values(): sp.set_edgecolor('#333')

    plt.tight_layout()
    out = 'daa_output_complexity.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=DARK_BG)
    plt.close()
    print(f'  Saved: {out}')
    return out

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print('\n  Running CampusPool DAA Demo...')

    # Build graph
    G = build_graph(students)
    print(f'  Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

    # Run greedy matching
    matches = greedy_match(students)

    # Print terminal results
    print_results(matches, G)

    # Generate visualizations
    print('  Generating visualizations...')
    plot_map(matches)
    plot_graph(G, matches)
    plot_complexity()

    print('\n  Done! Open the 3 PNG files to see results.')
    print('  daa_output_map.png        — student map + matched routes')
    print('  daa_output_graph.png      — graph nodes and edges')
    print('  daa_output_complexity.png — algorithm complexity charts\n')
