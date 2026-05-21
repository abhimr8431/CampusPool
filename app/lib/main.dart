import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'screens/register_screen.dart';
import 'screens/verify_screen.dart';
import 'screens/find_ride_screen.dart';
import 'screens/post_ride_screen.dart';
import 'screens/my_requests_screen.dart';
import 'screens/incoming_requests_screen.dart';
import 'screens/profile_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CampusPoolApp());
}

class CampusPoolApp extends StatelessWidget {
  const CampusPoolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CampusPool',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1D9E75)),
        useMaterial3: true,
        fontFamily: 'SF Pro Display',
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1D9E75),
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF1D9E75),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
        ),
      ),
      home: const SplashScreen(),
      routes: {
        '/login':              (_) => const LoginScreen(),
        '/register':           (_) => const RegisterScreen(),
        '/home':               (_) => const HomeScreen(),
        '/verify':             (_) => const VerifyScreen(),
        '/find-ride':          (_) => const FindRideScreen(),
        '/post-ride':          (_) => const PostRideScreen(),
        '/my-requests':        (_) => const MyRequestsScreen(),
        '/incoming-requests':  (_) => const IncomingRequestsScreen(),
        '/profile':            (_) => const ProfileScreen(),
      },
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkLogin();
  }

  Future<void> _checkLogin() async {
    await Future.delayed(const Duration(seconds: 1));
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');
    if (mounted) {
      Navigator.pushReplacementNamed(context, token != null ? '/home' : '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFF1D9E75),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.electric_moped, size: 72, color: Colors.white),
            SizedBox(height: 16),
            Text('CampusPool',
                style: TextStyle(color: Colors.white, fontSize: 28,
                    fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('College ride sharing',
                style: TextStyle(color: Colors.white70, fontSize: 15)),
          ],
        ),
      ),
    );
  }
}
