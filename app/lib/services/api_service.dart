import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

// 10.0.2.2 = localhost on Android emulator.
// If you run on a real Android phone, replace this with your PC's local IP,
// e.g. 'http://192.168.1.5:5000/api'.
const String _androidEmulatorUrl = 'http://10.0.2.2:5000/api';
const String _localhostUrl = 'http://127.0.0.1:5000/api';

String get baseUrl {
  if (Platform.isAndroid) return _androidEmulatorUrl;
  return _localhostUrl;
}

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

  static const Duration _requestTimeout = Duration(seconds: 10);

  static Future<Map<String, dynamic>> _processResponse(Future<http.Response> future) async {
    try {
      final res = await future.timeout(_requestTimeout);
      return jsonDecode(res.body);
    } on SocketException {
      return {'error': 'Unable to reach the server. Check your backend or network connection.'};
    } on TimeoutException {
      return {'error': 'Request timed out. Please try again.'};
    } on FormatException {
      return {'error': 'Received invalid data from the server.'};
    } catch (e) {
      return {'error': 'Request failed: ${e.toString()}'};
    }
  }

  // ── AUTH ─────────────────────────────────────
  static Future<Map<String, dynamic>> register(Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> login(String email, String password) async {
    final data = await _processResponse(http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    ));
    if (data['token'] != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('token', data['token']);
      await prefs.setString('user', jsonEncode(data['user']));
    }
    return data;
  }

  static Future<Map<String, dynamic>> sendOtp(String email) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/send-otp'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> verifyOtp(String email, String otp) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/verify-otp'),
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
      Uri.parse('$baseUrl/rides/find?lat=$lat&lon=$lon'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> postRide(Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$baseUrl/rides/post'),
      headers: await _headers(),
      body: jsonEncode(data),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getMyRides() async {
    final res = await http.get(
      Uri.parse('$baseUrl/rides/my-rides'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> cancelRide(String rideId) async {
    final res = await http.patch(
      Uri.parse('$baseUrl/rides/$rideId/cancel'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  // ── REQUESTS ─────────────────────────────────
  static Future<Map<String, dynamic>> sendRequest(
      String rideId, double pLat, double pLon) async {
    final res = await http.post(
      Uri.parse('$baseUrl/requests/send'),
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
      Uri.parse('$baseUrl/requests/$reqId/accept'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> declineRequest(String reqId) async {
    final res = await http.patch(
      Uri.parse('$baseUrl/requests/$reqId/decline'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getIncomingRequests() async {
    final res = await http.get(
      Uri.parse('$baseUrl/requests/incoming'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getMyRequests() async {
    final res = await http.get(
      Uri.parse('$baseUrl/requests/my-requests'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  // ── VERIFY ───────────────────────────────────
  static Future<Map<String, dynamic>> uploadIdCard(File imageFile) async {
    final token   = await getToken();
    final request = http.MultipartRequest(
      'POST', Uri.parse('$baseUrl/verify/upload-id'),
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
      'POST', Uri.parse('$baseUrl/verify/face-match'),
    );
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(await http.MultipartFile.fromPath('selfie', selfieFile.path));
    final response = await request.send();
    final body     = await response.stream.bytesToString();
    return jsonDecode(body);
  }

  static Future<Map<String, dynamic>> getVerifyStatus() async {
    final res = await http.get(
      Uri.parse('$baseUrl/verify/status'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  // ── PROFILE ──────────────────────────────────
  static Future<Map<String, dynamic>> getProfile() async {
    final res = await http.get(
      Uri.parse('$baseUrl/profile/me'),
      headers: await _headers(),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final res = await http.patch(
      Uri.parse('$baseUrl/profile/update'),
      headers: await _headers(),
      body: jsonEncode(data),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> rateUser(String userId, double rating) async {
    final res = await http.post(
      Uri.parse('$baseUrl/profile/rate'),
      headers: await _headers(),
      body: jsonEncode({'user_id': userId, 'rating': rating}),
    );
    return jsonDecode(res.body);
  }
}
