
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../services/api_service.dart';

class FindRideScreen extends StatefulWidget {
  const FindRideScreen({super.key});
  @override
  State<FindRideScreen> createState() => _FindRideScreenState();
}

class _FindRideScreenState extends State<FindRideScreen> {
  List<dynamic> _rides = [];
  bool _loading        = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchRides();
  }

  Future<void> _fetchRides() async {
    setState(() { _loading = true; _error = null; });
    try {
      Position pos = await Geolocator.getCurrentPosition();
      final res    = await ApiService.findRides(pos.latitude, pos.longitude);
      setState(() => _rides = res['rides'] ?? []);
    } catch (e) {
      // Use fixed coords if location permission denied
      final res = await ApiService.findRides(12.9370, 77.6190);
      setState(() => _rides = res['rides'] ?? []);
    }
    setState(() => _loading = false);
  }

  Future<void> _sendRequest(Map ride) async {
    final res = await ApiService.sendRequest(
      ride['ride_id'], 12.9370, 77.6190
    );
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(res['message'] ?? 'Request sent'),
      backgroundColor: res['message'] != null
          ? const Color(0xFF1D9E75) : Colors.red,
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Find a Ride'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _fetchRides)
        ],
      ),
      body: _loading
        ? const Center(child: CircularProgressIndicator(color: Color(0xFF1D9E75)))
        : _rides.isEmpty
          ? const Center(child: Text('No rides available near you right now'))
          : RefreshIndicator(
              onRefresh: _fetchRides,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _rides.length,
                itemBuilder: (_, i) => _RideCard(
                  ride: _rides[i],
                  onRequest: () => _sendRequest(_rides[i]),
                ),
              ),
            ),
    );
  }
}

class _RideCard extends StatelessWidget {
  final Map ride;
  final VoidCallback onRequest;
  const _RideCard({required this.ride, required this.onRequest});

  @override
  Widget build(BuildContext context) {
    final rider = ride['rider'] ?? {};
    final fare  = ride['fare']  ?? {};
    final bool verified = rider['verified'] ?? false;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Rider info row
            Row(children: [
              CircleAvatar(
                backgroundColor: const Color(0xFFE1F5EE),
                child: Text(
                  (rider['name'] ?? 'U').substring(0, 1),
                  style: const TextStyle(color: Color(0xFF0F6E56), fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(width: 10),
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(rider['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                Row(children: [
                  Text('${rider["year"] ?? ""} yr · ${rider["branch"] ?? ""}',
                      style: const TextStyle(color: Colors.grey, fontSize: 12)),
                  if (verified) ...[
                    const SizedBox(width: 6),
                    const Icon(Icons.verified, color: Color(0xFF1D9E75), size: 14),
                    const Text(' Verified', style: TextStyle(color: Color(0xFF1D9E75), fontSize: 11)),
                  ]
                ]),
              ]),
              const Spacer(),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                Text('₹${fare["passenger_pays"] ?? 0}',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold,
                        color: Color(0xFF1D9E75))),
                const Text('fuel split', style: TextStyle(fontSize: 10, color: Colors.grey)),
              ]),
            ]),
            const SizedBox(height: 10),
            const Divider(height: 1),
            const SizedBox(height: 10),

            // Ride details
            Wrap(spacing: 16, children: [
              _chip(Icons.two_wheeler, ride['vehicle_name'] ?? ''),
              _chip(Icons.schedule, ride['departure_time'] ?? ''),
              _chip(Icons.star, '${rider["rating"] ?? 5.0}'),
              _chip(Icons.near_me, '${ride["distance_from_you"] ?? 0} km away'),
            ]),
            const SizedBox(height: 10),

            // Fare breakdown
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFE1F5EE),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                fare['breakdown'] ?? '',
                style: const TextStyle(fontSize: 11, color: Color(0xFF0F6E56)),
              ),
            ),
            const SizedBox(height: 10),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onRequest,
                child: const Text('Request to Join'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(IconData icon, String label) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Icon(icon, size: 14, color: Colors.grey),
      const SizedBox(width: 3),
      Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
    ],
  );
}
