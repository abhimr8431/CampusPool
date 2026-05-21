import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nameCtrl    = TextEditingController();
  final _emailCtrl   = TextEditingController();
  final _passCtrl    = TextEditingController();
  final _phoneCtrl   = TextEditingController();
  final _rollCtrl    = TextEditingController();
  final _vehicleCtrl = TextEditingController();
  final _mileageCtrl = TextEditingController();
  String _year     = '1st';
  String _branch   = 'CSE';
  String _fuelType = 'petrol';
  bool _loading    = false;
  bool _obscure    = true;
  String? _error;

  final _years    = ['1st', '2nd', '3rd', '4th'];
  final _branches = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE', 'ISE', 'AIML'];
  final _fuels    = ['petrol', 'diesel'];

  Future<void> _register() async {
    if (_nameCtrl.text.isEmpty || _emailCtrl.text.isEmpty ||
        _passCtrl.text.isEmpty || _vehicleCtrl.text.isEmpty ||
        _mileageCtrl.text.isEmpty) {
      setState(() => _error = 'Please fill all required fields');
      return;
    }
    setState(() { _loading = true; _error = null; });
    final res = await ApiService.register({
      'name':        _nameCtrl.text.trim(),
      'email':       _emailCtrl.text.trim().toLowerCase(),
      'password':    _passCtrl.text,
      'phone':       _phoneCtrl.text.trim(),
      'roll_number': _rollCtrl.text.trim(),
      'college':     'RVCE',
      'year':        _year,
      'branch':      _branch,
     'vehicle': {
  'name':         _vehicleCtrl.text.trim(),
  'fuel_type':    _fuelType,
  'mileage_kmpl': double.tryParse(_mileageCtrl.text.trim()) ?? 40.0,
  'reg_number':   '',
},
    });
    setState(() => _loading = false);
    if (res['user_id'] != null) {
      await ApiService.sendOtp(_emailCtrl.text.trim().toLowerCase());
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/login');
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Registered! Check college email for OTP'),
          backgroundColor: Color(0xFF1D9E75)));
      }
    } else {
      setState(() => _error = res['error'] ?? 'Registration failed');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          if (_error != null)
            Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFCEBEB),
                borderRadius: BorderRadius.circular(10)),
              child: Row(children: [
                const Icon(Icons.error_outline, color: Color(0xFFA32D2D), size: 18),
                const SizedBox(width: 8),
                Expanded(child: Text(_error!,
                    style: const TextStyle(color: Color(0xFFA32D2D)))),
              ]),
            ),

          _sectionHeader('Personal details'),
          _field(_nameCtrl,  'Full name',     Icons.person_outline),
          _field(_emailCtrl, 'College email', Icons.email_outlined,
              hint: 'yourname@rvce.edu.in',
              type: TextInputType.emailAddress),
          TextField(
            controller: _passCtrl,
            obscureText: _obscure,
            decoration: InputDecoration(
              labelText: 'Password',
              prefixIcon: const Icon(Icons.lock_outline, color: Color(0xFF1D9E75)),
              suffixIcon: IconButton(
                icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility),
                onPressed: () => setState(() => _obscure = !_obscure)),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF1D9E75), width: 2))),
          ),
          const SizedBox(height: 14),
          _field(_phoneCtrl, 'Phone number',  Icons.phone_outlined,
              type: TextInputType.phone),
          _field(_rollCtrl,  'Roll number',   Icons.badge_outlined,
              hint: '1RV22CS042'),
          Row(children: [
            Expanded(child: _drop('Year',   _year,   _years,
                (v) => setState(() => _year = v!))),
            const SizedBox(width: 12),
            Expanded(child: _drop('Branch', _branch, _branches,
                (v) => setState(() => _branch = v!))),
          ]),

          const SizedBox(height: 8),
          _sectionHeader('Vehicle details'),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFE1F5EE),
              borderRadius: BorderRadius.circular(10)),
            child: const Text(
              'Your vehicle mileage is used to auto-calculate the fare split. '
              'Enter your actual mileage for accurate pricing.',
              style: TextStyle(fontSize: 12, color: Color(0xFF0F6E56))),
          ),
          const SizedBox(height: 14),
          _field(_vehicleCtrl, 'Vehicle name',   Icons.two_wheeler_outlined,
              hint: 'e.g. Honda Activa'),
          _field(_mileageCtrl, 'Mileage (kmpl)', Icons.local_gas_station_outlined,
              hint: 'e.g. 40', type: TextInputType.number),
          _drop('Fuel type', _fuelType, _fuels,
              (v) => setState(() => _fuelType = v!)),

          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _loading ? null : _register,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.all(16)),
              child: _loading
                ? const SizedBox(height: 20, width: 20,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('Create Account', style: TextStyle(fontSize: 16)),
            ),
          ),
          const SizedBox(height: 14),
          Center(child: TextButton(
            onPressed: () => Navigator.pushReplacementNamed(context, '/login'),
            child: const Text('Already have an account? Sign in'),
          )),
        ]),
      ),
    );
  }

  Widget _sectionHeader(String t) => Padding(
    padding: const EdgeInsets.only(top: 8, bottom: 12),
    child: Text(t, style: const TextStyle(fontSize: 15,
        fontWeight: FontWeight.w600)));

  Widget _field(TextEditingController c, String label, IconData icon,
      {String? hint, TextInputType? type}) =>
    Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextField(
        controller: c,
        keyboardType: type,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          prefixIcon: Icon(icon, color: const Color(0xFF1D9E75)),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: Color(0xFF1D9E75), width: 2)))));

  Widget _drop(String label, String value, List<String> items,
      void Function(String?) onChange) =>
    Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: DropdownButtonFormField<String>(
        value: value,
        decoration: InputDecoration(
          labelText: label,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: Color(0xFF1D9E75), width: 2))),
        items: items.map((i) => DropdownMenuItem(value: i, child: Text(i))).toList(),
        onChanged: onChange));

  @override
  void dispose() {
    _nameCtrl.dispose(); _emailCtrl.dispose(); _passCtrl.dispose();
    _phoneCtrl.dispose(); _rollCtrl.dispose(); _vehicleCtrl.dispose();
    _mileageCtrl.dispose(); super.dispose();
  }
}