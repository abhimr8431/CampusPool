import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../services/socket_service.dart';
import 'find_ride_screen.dart';
import 'post_ride_screen.dart';
import 'incoming_requests_screen.dart';
import 'my_requests_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tab = 0;
  Map<String, dynamic>? _user;

  final List<Widget> _screens = [
    const FindRideScreen(),
    const PostRideScreen(),
    const IncomingRequestsScreen(),
    const MyRequestsScreen(),
    const ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    final prefs    = await SharedPreferences.getInstance();
    final userJson = prefs.getString('user');
    if (userJson != null) {
      setState(() => _user = jsonDecode(userJson));
      SocketService.connect(_user!['id']);

      // Rider gets notified of new requests
      SocketService.onNewRequest = (data) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('New ride request from ${data['passenger_name']}!'),
            backgroundColor: const Color(0xFF1D9E75),
            action: SnackBarAction(
              label: 'View',
              textColor: Colors.white,
              onPressed: () => setState(() => _tab = 2),
            ),
          ));
        }
      };

      // Passenger gets notified when rider accepts
      SocketService.onRequestAccepted = (data) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('${data['rider_name']} accepted your request!'),
            backgroundColor: const Color(0xFF1D9E75),
          ));
        }
      };
    }
  }

  @override
  void dispose() {
    SocketService.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_tab],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.search), label: 'Find Ride'),
          NavigationDestination(icon: Icon(Icons.add_circle_outline), label: 'Post Ride'),
          NavigationDestination(icon: Icon(Icons.inbox), label: 'Requests'),
          NavigationDestination(icon: Icon(Icons.route), label: 'My Rides'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }
}
