import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PostRideScreen extends StatefulWidget {
  const PostRideScreen({super.key});
  @override
  State<PostRideScreen> createState() => _PostRideScreenState();
}

class _PostRideScreenState extends State<PostRideScreen> {
  final _originCtrl = TextEditingController();
  final _timeCtrl   = TextEditingController();
  int _seats        = 1;
  bool _loading     = false;
  Map<String, dynamic>? _farePreview;

  Future<void> _post() async {
    if (_originCtrl.text.isEmpty || _timeCtrl.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all fields')));
      return;
    }
    setState(() { _loading = true; _farePreview = null; });
    final res = await ApiService.postRide({
      'origin_lat':     12.9352,
      'origin_lon':     77.6245,
      'origin_name':    _originCtrl.text.trim(),
      'departure_time': _timeCtrl.text.trim(),
      'seats':          _seats,
    });
    setState(() => _loading = false);
    if (res['ride_id'] != null) {
      setState(() => _farePreview = res['estimated_fare']);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Ride posted successfully!'),
        backgroundColor: Color(0xFF1D9E75)));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(res['error'] ?? 'Failed to post ride'),
        backgroundColor: Colors.red));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Post a Ride')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFE1F5EE),
              borderRadius: BorderRadius.circular(12)),
            child: const Row(children: [
              Icon(Icons.info_outline, color: Color(0xFF1D9E75), size: 20),
              SizedBox(width: 10),
              Expanded(child: Text(
                'Fare is auto-calculated from your vehicle mileage. '
                'You cannot charge more than this amount.',
                style: TextStyle(fontSize: 12, color: Color(0xFF0F6E56)))),
            ]),
          ),
          const SizedBox(height: 20),
          _label('Pickup area'),
          TextField(
            controller: _originCtrl,
            decoration: _dec('e.g. Koramangala 5th Block', Icons.location_on_outlined),
          ),
          const SizedBox(height: 14),
          _label('Departure time'),
          TextField(
            controller: _timeCtrl,
            readOnly: true,
            decoration: _dec('Tap to pick time', Icons.schedule),
            onTap: () async {
              final t = await showTimePicker(
                  context: context, initialTime: TimeOfDay.now());
              if (t != null && mounted) _timeCtrl.text = t.format(context);
            },
          ),
          const SizedBox(height: 14),
          _label('Available seats'),
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(12)),
            child: Row(children: [
              IconButton(
                icon: const Icon(Icons.remove),
                onPressed: () { if (_seats > 1) setState(() => _seats--); }),
              Expanded(child: Center(child: Text('$_seats',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)))),
              IconButton(
                icon: const Icon(Icons.add),
                onPressed: () { if (_seats < 3) setState(() => _seats++); }),
            ]),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _loading ? null : _post,
              child: _loading
                ? const SizedBox(height: 20, width: 20,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('Post Ride'),
            ),
          ),
          if (_farePreview != null) ...[
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFE1F5EE),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF1D9E75))),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Estimated fare breakdown',
                  style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF0F6E56))),
                const SizedBox(height: 10),
                _fareRow('Distance',        '${_farePreview!["distance_km"]} km'),
                _fareRow('Fuel used',       '${_farePreview!["fuel_used_L"]} L'),
                _fareRow('Total fuel cost', '₹${_farePreview!["total_cost"]}'),
                const Divider(color: Color(0xFF9FE1CB)),
                _fareRow('Passenger pays',  '₹${_farePreview!["passenger_pays"]}', bold: true),
                const SizedBox(height: 6),
                Text(_farePreview!['breakdown'] ?? '',
                  style: const TextStyle(fontSize: 11, color: Color(0xFF0F6E56))),
              ]),
            ),
          ],
        ]),
      ),
    );
  }

  Widget _label(String t) => Padding(
    padding: const EdgeInsets.only(bottom: 6),
    child: Text(t, style: const TextStyle(fontSize: 13,
        fontWeight: FontWeight.w500, color: Colors.grey)));

  Widget _fareRow(String k, String v, {bool bold = false}) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 3),
    child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
      Text(k, style: TextStyle(fontSize: 13, color: const Color(0xFF0F6E56),
          fontWeight: bold ? FontWeight.w600 : FontWeight.normal)),
      Text(v, style: TextStyle(fontSize: 13,
          color: bold ? const Color(0xFF1D9E75) : const Color(0xFF0F6E56),
          fontWeight: bold ? FontWeight.bold : FontWeight.normal)),
    ]));

  InputDecoration _dec(String hint, IconData icon) => InputDecoration(
    hintText: hint,
    prefixIcon: Icon(icon, color: const Color(0xFF1D9E75)),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(12),
      borderSide: const BorderSide(color: Color(0xFF1D9E75), width: 2)));

  @override
  void dispose() { _originCtrl.dispose(); _timeCtrl.dispose(); super.dispose(); }
}