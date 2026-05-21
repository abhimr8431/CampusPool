import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

const String SOCKET_URL = 'http://10.0.2.2:5000';

class SocketService {
  static IO.Socket? _socket;
  static Function(Map)? onNewRequest;     // rider gets this
  static Function(Map)? onRequestAccepted; // passenger gets this
  static Function(Map)? onRequestDeclined;

  static void connect(String userId) {
    _socket = IO.io(SOCKET_URL, IO.OptionBuilder()
        .setTransports(['websocket'])
        .build());

    _socket!.onConnect((_) {
      print('Socket connected');
    });

    // Rider: new incoming request
    _socket!.on('new_request_$userId', (data) {
      if (onNewRequest != null) onNewRequest!(Map<String, dynamic>.from(data));
    });

    // Passenger: rider accepted
    _socket!.on('request_accepted_$userId', (data) {
      if (onRequestAccepted != null) onRequestAccepted!(Map<String, dynamic>.from(data));
    });

    // Passenger: rider declined
    _socket!.on('request_declined_$userId', (data) {
      if (onRequestDeclined != null) onRequestDeclined!(Map<String, dynamic>.from(data));
    });

    _socket!.onDisconnect((_) => print('Socket disconnected'));
  }

  static void disconnect() {
    _socket?.disconnect();
  }
}
