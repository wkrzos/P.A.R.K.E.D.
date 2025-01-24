import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../mqtt/mqtt_state.dart';
import '../mqtt/mqtt_client.dart';
import 'main_view.dart';

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final TextEditingController _hostTextController = TextEditingController();
  final TextEditingController _topicTextController = TextEditingController();

  @override
  void dispose() {
    _hostTextController.dispose();
    _topicTextController.dispose();
    super.dispose();
  }



void _connect() async {
  final host = _hostTextController.text.trim();
  final topic = _topicTextController.text.trim();

  if (host.isEmpty || topic.isEmpty) {
    _showErrorDialog('Please provide both host and topic.');
    return;
  }

  // Get the app state
  final appState = Provider.of<MQTTAppState>(context, listen: false);
  final manager = MQTTManager(host: host, topic: topic, state: appState);


  // Attempt to connect
  final connected = await manager.connect();
  if (connected) {
    // Navigate to MainView if connection is successful
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => MainView(manager: manager, mqttAppState: appState),
      ),
    );
  } else {
    // Show an error dialog if connection fails
    _showErrorDialog('Failed to connect to the MQTT broker. Please try again.');
  }
}

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('MQTT Login')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _hostTextController,
              decoration: const InputDecoration(
                labelText: 'Host',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _topicTextController,
              decoration: const InputDecoration(
                labelText: 'Topic',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _connect,
              child: const Text('Connect'),
            ),
          ],
        ),
      ),
    );
  }
}
