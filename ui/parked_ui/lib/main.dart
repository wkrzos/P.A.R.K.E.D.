import 'package:flutter/material.dart';
import 'package:parked_ui/widgets/login_view.dart';
import 'mqtt/mqtt_state.dart';
import 'package:provider/provider.dart';


void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => MQTTAppState(),
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'MQTT App',
      theme: ThemeData(primarySwatch: Colors.green),
      home: const LoginView(),
    );
  }
}


