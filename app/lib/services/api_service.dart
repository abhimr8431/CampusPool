import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

// 10.0.2.2 = localhost on Android emulator
// Change to your PC's local IP (e.g. 192.168.1.5) for real device
const String BASE_URL = 'http://127.0.0.1:5000/api';

class ApiService {

  // ── GET JWT TOKEN FROM STORAGE ──────────────
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }

  static Future<Map<String, String>> _headers() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // ── AUTH ─────────────────────────────────────
  static Future<Map<String, dynamic>> register(Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    final data = jsonDecode(res.body);
    if (data['token'] != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', data['token']);
      await prefs.setString('user',  jsonEncode(data['user']));
    }
    return data;
  }

  static Future<Map<String, dynamic>> sendOtp(String email) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/auth/send-otp'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> verifyOtp(String email, String otp) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/auth/verify-otp'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'otp': otp}),
    );
    return jsonDecode(res.body);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user');
  }

  // ── RIDES ────────────────────────────────────
  static Future<Map<String, dynamic>> findRides(double lat, double lon) async {
    final res = await http.get(
      Uri.parse('$BASE_URL/rides/find?lat=$lat&lon=$lon'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> postRide(Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/rides/post'),
      headers: await _headers(),
      body: jsonEncode(data),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getMyRides() async {
    final res = await http.get(
      Uri.parse('$BASE_URL/rides/my-rides'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> cancelRide(String rideId) async {
    final res = await http.patch(
      Uri.parse('$BASE_URL/rides/$rideId/cancel'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  // ── REQUESTS ─────────────────────────────────
  static Future<Map<String, dynamic>> sendRequest(
      String rideId, double pLat, double pLon) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/requests/send'),
      headers: await _headers(),
      body: jsonEncode({
        'ride_id':       rideId,
        'passenger_lat': pLat,
        'passenger_lon': pLon,
      }),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> acceptRequest(String reqId) async {
    final res = await http.patch(
      Uri.parse('$BASE_URL/requests/$reqId/accept'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> declineRequest(String reqId) async {
    final res = await http.patch(
      Uri.parse('$BASE_URL/requests/$reqId/decline'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getIncomingRequests() async {
    final res = await http.get(
      Uri.parse('$BASE_URL/requests/incoming'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getMyRequests() async {
    final res = await http.get(
      Uri.parse('$BASE_URL/requests/my-requests'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  // ── VERIFY ───────────────────────────────────
  static Future<Map<String, dynamic>> uploadIdCard(File imageFile) async {
    final token   = await getToken();
    final request = http.MultipartRequest(
      'POST', Uri.parse('$BASE_URL/verify/upload-id'),
    );
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('idCard', imageFile.path));
    final response = await request.send();
    final body     = await response.stream.bytesToString();
    return jsonDecode(body);
  }

  static Future<Map<String, dynamic>> uploadSelfie(File selfieFile) async {
    final token   = await getToken();
    final request = http.MultipartRequest(
      'POST', Uri.parse('$BASE_URL/verify/face-match'),
    );
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('selfie', selfieFile.path));
    final response = await request.send();
    final body     = await response.stream.bytesToString();
    return jsonDecode(body);
  }

  static Future<Map<String, dynamic>> getVerifyStatus() async {
    final res = await http.get(
      Uri.parse('$BASE_URL/verify/status'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  // ── PROFILE ──────────────────────────────────
  static Future<Map<String, dynamic>> getProfile() async {
    final res = await http.get(
      Uri.parse('$BASE_URL/profile/me'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final res = await http.patch(
      Uri.parse('$BASE_URL/profile/update'),
      headers: await _headers(),
      body: jsonEncode(data),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> rateUser(String userId, double rating) async {
    final res = await http.post(
      Uri.parse('$BASE_URL/profile/rate'),
      headers: await _headers(),
      body: jsonEncode({'user_id': userId, 'rating': rating}),
    );
    return jsonDecode(res.body);
  }
}
