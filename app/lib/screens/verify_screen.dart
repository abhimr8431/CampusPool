import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../services/api_service.dart';

class VerifyScreen extends StatefulWidget {
  const VerifyScreen({super.key});
  @override
  State<VerifyScreen> createState() => _VerifyScreenState();
}

class _VerifyScreenState extends State<VerifyScreen> {
  final _emailCtrl = TextEditingController();
  final _otpCtrl   = TextEditingController();

  bool _idUploaded     = false;
  bool _faceMatched    = false;
  bool _emailVerified  = false;
  bool _loading        = false;
  String? _msg;
  bool _msgSuccess     = false;

  @override
  void initState() { super.initState(); _loadStatus(); }

  Future<void> _loadStatus() async {
    final res = await ApiService.getVerifyStatus();
    setState(() {
      _idUploaded    = res['id_uploaded']    ?? false;
      _faceMatched   = res['face_matched']   ?? false;
      _emailVerified = res['email_verified'] ?? false;
    });
  }

  Future<void> _pickId() async {
    final img = await ImagePicker().pickImage(
        source: ImageSource.gallery, imageQuality: 90);
    if (img == null) return;
    setState(() { _loading = true; _msg = null; });
    final res = await ApiService.uploadIdCard(File(img.path));
    setState(() {
      _loading     = false;
      _idUploaded  = res['passed'] ?? false;
      _msg         = res['message'];
      _msgSuccess  = _idUploaded;
    });
  }

  Future<void> _pickSelfie() async {
    final img = await ImagePicker().pickImage(
        source: ImageSource.camera, imageQuality: 90);
    if (img == null) return;
    setState(() { _loading = true; _msg = null; });
    final res = await ApiService.uploadSelfie(File(img.path));
    setState(() {
      _loading     = false;
      _faceMatched = res['matched'] ?? false;
      _msgSuccess  = _faceMatched;
      _msg = _faceMatched
        ? 'Face matched! Confidence: ${res["confidence"]}%'
        : (res['message'] ?? 'Face did not match');
    });
  }

  Future<void> _sendOtp() async {
    if (_emailCtrl.text.isEmpty) return;
    setState(() => _loading = true);
    final res = await ApiService.sendOtp(_emailCtrl.text.trim());
    setState(() {
      _loading    = false;
      _msg        = res['message'] ?? res['error'];
      _msgSuccess = res['message'] != null;
    });
  }

  Future<void> _verifyOtp() async {
    if (_otpCtrl.text.length != 6) {
      setState(() { _msg = 'Enter 6-digit OTP'; _msgSuccess = false; });
      return;
    }
    setState(() => _loading = true);
    final res = await ApiService.verifyOtp(
        _emailCtrl.text.trim(), _otpCtrl.text.trim());
    setState(() {
      _loading       = false;
      _emailVerified = res['message']?.toString().contains('verified') ?? false;
      _msg           = res['message'] ?? res['error'];
      _msgSuccess    = _emailVerified;
    });
  }

  bool get _allDone => _idUploaded && _faceMatched && _emailVerified;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ID Verification')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          if (_msg != null)
            Container(
              margin: const EdgeInsets.only(bottom: 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _msgSuccess
                  ? const Color(0xFFE1F5EE) : const Color(0xFFFAEEDA),
                borderRadius: BorderRadius.circular(10)),
              child: Row(children: [
                Icon(_msgSuccess ? Icons.check_circle_outline : Icons.warning_outlined,
                  color: _msgSuccess ? const Color(0xFF1D9E75) : const Color(0xFFBA7517),
                  size: 18),
                const SizedBox(width: 8),
                Expanded(child: Text(_msg!,
                  style: TextStyle(
                    color: _msgSuccess ? const Color(0xFF0F6E56) : const Color(0xFF633806),
                    fontSize: 13))),
              ]),
            ),

          // Step 1 - ID Card
          _stepCard(
            step: 1, title: 'Upload College ID Card',
            subtitle: 'Front side · name, roll number, college name must be visible',
            done: _idUploaded,
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _loading ? null : _pickId,
                icon: const Icon(Icons.upload_file),
                label: Text(_idUploaded ? 'Re-upload ID Card' : 'Choose from Gallery'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _idUploaded
                    ? Colors.grey.shade200 : const Color(0xFF1D9E75),
                  foregroundColor: _idUploaded ? Colors.black87 : Colors.white)),
            ),
          ),

          // Step 2 - Selfie
          _stepCard(
            step: 2, title: 'Selfie with ID Card',
            subtitle: 'Hold your ID next to your face · we verify it\'s you',
            done: _faceMatched,
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: (!_idUploaded || _loading) ? null : _pickSelfie,
                icon: const Icon(Icons.camera_alt),
                label: Text(_faceMatched ? 'Retake Selfie' : 'Open Camera'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _faceMatched
                    ? Colors.grey.shade200 : const Color(0xFF1D9E75),
                  foregroundColor: _faceMatched ? Colors.black87 : Colors.white)),
            ),
          ),

          // Step 3 - Email OTP
          _stepCard(
            step: 3, title: 'Verify College Email',
            subtitle: 'We send an OTP to your college email address',
            done: _emailVerified,
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Expanded(
                  child: TextField(
                    controller: _emailCtrl,
                    keyboardType: TextInputType.emailAddress,
                    decoration: InputDecoration(
                      hintText: 'yourname@rvce.edu.in',
                      prefixIcon: const Icon(Icons.email_outlined,
                          color: Color(0xFF1D9E75)),
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10)),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(
                            color: Color(0xFF1D9E75), width: 2)))),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _loading ? null : _sendOtp,
                  child: const Text('Send OTP')),
              ]),
              const SizedBox(height: 10),
              Row(children: [
                Expanded(
                  child: TextField(
                    controller: _otpCtrl,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    decoration: InputDecoration(
                      hintText: '6-digit OTP',
                      counterText: '',
                      prefixIcon: const Icon(Icons.pin_outlined,
                          color: Color(0xFF1D9E75)),
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10)),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: const BorderSide(
                            color: Color(0xFF1D9E75), width: 2)))),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _loading ? null : _verifyOtp,
                  child: const Text('Verify')),
              ]),
            ]),
          ),

          // All done banner
          if (_allDone)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1D9E75),
                borderRadius: BorderRadius.circular(14)),
              child: const Row(children: [
                Icon(Icons.verified, color: Colors.white, size: 32),
                SizedBox(width: 12),
                Expanded(child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('Fully Verified!',
                    style: TextStyle(color: Colors.white,
                        fontWeight: FontWeight.bold, fontSize: 16)),
                  Text('Your trust score has been updated.',
                    style: TextStyle(color: Colors.white70, fontSize: 12)),
                ])),
              ]),
            ),

          if (_loading)
            const Padding(
              padding: EdgeInsets.all(20),
              child: Center(child: CircularProgressIndicator(
                  color: Color(0xFF1D9E75)))),
        ]),
      ),
    );
  }

  Widget _stepCard({required int step, required String title,
      required String subtitle, required bool done, required Widget child}) =>
    Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        border: Border.all(
          color: done ? const Color(0xFF1D9E75) : Colors.grey.shade200,
          width: done ? 1.5 : 0.5),
        borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            CircleAvatar(
              radius: 15,
              backgroundColor: done
                ? const Color(0xFF1D9E75) : Colors.grey.shade200,
              child: done
                ? const Icon(Icons.check, color: Colors.white, size: 16)
                : Text('$step',
                    style: const TextStyle(fontWeight: FontWeight.bold,
                        fontSize: 13)),
            ),
            const SizedBox(width: 10),
            Expanded(child: Text(title,
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14))),
          ]),
          Padding(
            padding: const EdgeInsets.only(left: 40, top: 4, bottom: 12),
            child: Text(subtitle,
              style: const TextStyle(color: Colors.grey, fontSize: 12))),
          Padding(padding: const EdgeInsets.only(left: 40), child: child),
        ]),
      ),
    );

  @override
  void dispose() {
    _emailCtrl.dispose(); _otpCtrl.dispose(); super.dispose();
  }
}