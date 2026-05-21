import 'package:flutter/material.dart';
import '../services/api_service.dart';

class MyRequestsScreen extends StatefulWidget {
  const MyRequestsScreen({super.key});
  @override
  State<MyRequestsScreen> createState() => _MyRequestsScreenState();
}

class _MyRequestsScreenState extends State<MyRequestsScreen> {
  List<dynamic> _requests = [];
  bool _loading = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    final res = await ApiService.getMyRequests();
    setState(() { _requests = res['requests'] ?? []; _loading = false; });
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'accepted': return const Color(0xFF1D9E75);
      case 'declined': return Colors.red;
      case 'expired':  return Colors.orange;
      default:         return Colors.blue;
    }
  }

  IconData _statusIcon(String status) {
    switch (status) {
      case 'accepted': return Icons.check_circle_outline;
      case 'declined': return Icons.cancel_outlined;
      case 'expired':  return Icons.timer_off_outlined;
      default:         return Icons.hourglass_top_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Ride Requests'),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)],
      ),
      body: _loading
        ? const Center(child: CircularProgressIndicator(color: Color(0xFF1D9E75)))
        : _requests.isEmpty
          ? const Center(
              child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                Icon(Icons.route_outlined, size: 64, color: Colors.grey),
                SizedBox(height: 12),
                Text('No ride requests yet', style: TextStyle(color: Colors.grey)),
                SizedBox(height: 6),
                Text('Find a ride and send a request',
                    style: TextStyle(color: Colors.grey, fontSize: 12)),
              ]))
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _requests.length,
                itemBuilder: (_, i) {
                  final r     = _requests[i];
                  final rider = r['rider'] ?? {};
                  final ride  = r['ride']  ?? {};
                  final fare  = r['fare']  ?? {};
                  final status = r['status'] ?? 'pending';

                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                      side: BorderSide(
                        color: status == 'accepted'
                          ? const Color(0xFF1D9E75) : Colors.grey.shade200,
                        width: status == 'accepted' ? 1.5 : 0.5)),
                    elevation: 1,
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(children: [
                            CircleAvatar(
                              backgroundColor: const Color(0xFFE1F5EE),
                              child: Text(
                                (rider['name'] ?? 'R')[0],
                                style: const TextStyle(color: Color(0xFF0F6E56),
                                    fontWeight: FontWeight.bold)),
                            ),
                            const SizedBox(width: 10),
                            Expanded(child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                              Text(rider['name'] ?? 'Unknown Rider',
                                style: const TextStyle(fontWeight: FontWeight.w600,
                                    fontSize: 15)),
                              Text(rider['vehicle'] ?? '',
                                style: const TextStyle(color: Colors.grey,
                                    fontSize: 12)),
                            ])),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: _statusColor(status).withOpacity(0.1),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                    color: _statusColor(status).withOpacity(0.3))),
                              child: Row(mainAxisSize: MainAxisSize.min, children: [
                                Icon(_statusIcon(status),
                                    size: 13, color: _statusColor(status)),
                                const SizedBox(width: 4),
                                Text(status[0].toUpperCase() + status.substring(1),
                                  style: TextStyle(fontSize: 12,
                                      color: _statusColor(status),
                                      fontWeight: FontWeight.w500)),
                              ]),
                            ),
                          ]),
                          const SizedBox(height: 10),
                          const Divider(height: 1),
                          const SizedBox(height: 10),
                          Row(children: [
                            const Icon(Icons.schedule, size: 14, color: Colors.grey),
                            const SizedBox(width: 4),
                            Text(ride['departure_time'] ?? '',
                                style: const TextStyle(fontSize: 12, color: Colors.grey)),
                            const SizedBox(width: 16),
                            const Icon(Icons.local_gas_station_outlined,
                                size: 14, color: Color(0xFF1D9E75)),
                            const SizedBox(width: 4),
                            Text('You pay: ₹${fare["passenger_pays"] ?? 0}',
                                style: const TextStyle(fontSize: 12,
                                    color: Color(0xFF1D9E75),
                                    fontWeight: FontWeight.w600)),
                          ]),
                          if (status == 'accepted') ...[
                            const SizedBox(height: 10),
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: const Color(0xFFE1F5EE),
                                borderRadius: BorderRadius.circular(8)),
                              child: Row(children: [
                                const Icon(Icons.phone_outlined,
                                    size: 16, color: Color(0xFF1D9E75)),
                                const SizedBox(width: 8),
                                Text('Contact rider: ${rider["phone"] ?? "—"}',
                                  style: const TextStyle(fontSize: 12,
                                      color: Color(0xFF0F6E56))),
                              ]),
                            ),
                          ],
                        ]),
                    ),
                  );
                },
              ),
            ),
    );
  }
}