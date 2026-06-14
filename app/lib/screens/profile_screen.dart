import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _profile;
  bool _loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    final res = await ApiService.getProfile();
    setState(() { _profile = res; _loading = false; });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
      body: Center(child: CircularProgressIndicator(color: Color(0xFF1D9E75))));
    }

    final p = _profile!;
    final v = p['verification'] ?? {};
    final vehicle = p['vehicle'] ?? {};
    final bool isVerified = v['is_verified'] ?? false;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.verified_user_outlined),
            tooltip: 'Verify ID',
            onPressed: () => Navigator.pushNamed(context, '/verify')),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              await ApiService.logout();
              if (mounted) Navigator.pushReplacementNamed(context, '/login');
            }),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(20, 28, 20, 24),
              color: const Color(0xFF1D9E75),
              child: Column(children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: Colors.white24,
                  child: Text(
                    (p['name'] ?? 'U')[0].toUpperCase(),
                    style: const TextStyle(fontSize: 32, color: Colors.white,
                        fontWeight: FontWeight.bold))),
                const SizedBox(height: 12),
                Text(p['name'] ?? '',
                  style: const TextStyle(color: Colors.white,
                      fontSize: 20, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('${p["college"] ?? ""} · ${p["year"] ?? ""} yr · ${p["branch"] ?? ""}',
                  style: const TextStyle(color: Colors.white70, fontSize: 13)),
                const SizedBox(height: 10),
                if (isVerified)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20)),
                    child: const Row(mainAxisSize: MainAxisSize.min, children: [
                      Icon(Icons.verified, color: Color(0xFF1D9E75), size: 16),
                      SizedBox(width: 4),
                      Text('ID Verified', style: TextStyle(
                        color: Color(0xFF1D9E75), fontWeight: FontWeight.w600,
                        fontSize: 13)),
                    ]))
                else
                  GestureDetector(
                    onTap: () => Navigator.pushNamed(context, '/verify'),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                      decoration: BoxDecoration(
                        color: Colors.white30,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.white54)),
                      child: const Row(mainAxisSize: MainAxisSize.min, children: [
                        Icon(Icons.warning_amber_rounded,
                            color: Colors.white, size: 16),
                        SizedBox(width: 4),
                        Text('Tap to verify ID',
                          style: TextStyle(color: Colors.white, fontSize: 13)),
                      ]))),
              ]),
            ),

            // Stats row
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(children: [
                _stat('${p["total_rides"] ?? 0}', 'Total Rides'),
                _statDivider(),
                _stat('${p["rating"] ?? "5.0"}', 'Rating'),
                _statDivider(),
                _stat('${p["trust_score"] ?? 50}', 'Trust Score'),
              ]),
            ),

            // Details
            _section('Account'),
            _tile(Icons.email_outlined,        'College Email', p['email'] ?? ''),
            _tile(Icons.phone_outlined,         'Phone',        p['phone'] ?? ''),
            _tile(Icons.badge_outlined,         'Roll Number',  p['roll_number'] ?? ''),

            _section('Vehicle'),
            _tile(Icons.two_wheeler,            'Vehicle',
                vehicle['name'] ?? 'Not set'),
            _tile(Icons.local_gas_station_outlined, 'Mileage',
                vehicle['mileage_kmpl'] != null
                  ? '${vehicle["mileage_kmpl"]} kmpl' : 'Not set'),
            _tile(Icons.water_drop_outlined,    'Fuel type',
                (vehicle['fuel_type'] ?? 'petrol').toString().toUpperCase()),

            _section('Verification'),
            _verifyTile('College email',  v['email_verified'] ?? false),
            _verifyTile('ID card upload', v['id_uploaded']    ?? false),
            _verifyTile('Face match',     v['face_matched']   ?? false),

            const SizedBox(height: 20),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, '/verify'),
                  icon: const Icon(Icons.shield_outlined),
                  label: const Text('Complete Verification'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF1D9E75),
                    side: const BorderSide(color: Color(0xFF1D9E75)),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                    padding: const EdgeInsets.all(14))),
              ),
            ),
            const SizedBox(height: 30),
          ]),
        ),
      ),
    );
  }

  Widget _stat(String val, String label) => Expanded(child: Column(children: [
    Text(val, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold,
        color: Color(0xFF1D9E75))),
    const SizedBox(height: 2),
    Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
  ]));

  Widget _statDivider() => Container(
    height: 36, width: 1, color: Colors.grey.shade200,
    margin: const EdgeInsets.symmetric(horizontal: 8));

  Widget _section(String t) => Padding(
    padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
    child: Text(t.toUpperCase(),
      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600,
          color: Colors.grey, letterSpacing: 0.5)));

  Widget _tile(IconData icon, String label, String val) => ListTile(
    dense: true,
    leading: Icon(icon, color: Colors.grey, size: 22),
    title: Text(label,
        style: const TextStyle(fontSize: 12, color: Colors.grey)),
    subtitle: Text(val,
        style: const TextStyle(fontSize: 14, color: Colors.black87)));

  Widget _verifyTile(String label, bool done) => ListTile(
    dense: true,
    leading: Icon(
      done ? Icons.check_circle : Icons.radio_button_unchecked,
      color: done ? const Color(0xFF1D9E75) : Colors.grey, size: 22),
    title: Text(label, style: const TextStyle(fontSize: 14)),
    trailing: done
      ? const Text('Done', style: TextStyle(color: Color(0xFF1D9E75),
          fontSize: 12, fontWeight: FontWeight.w500))
      : const Text('Pending', style: TextStyle(color: Colors.orange,
          fontSize: 12)));
}