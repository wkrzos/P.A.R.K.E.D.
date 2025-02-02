import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../mqtt/mqtt_client.dart';
import '../mqtt/mqtt_state.dart';

class MainView extends StatefulWidget {
  final MQTTManager manager;
  final MQTTAppState mqttAppState;

  const MainView({
    super.key,
    required this.manager,
    required this.mqttAppState,
  });

  @override
  State<MainView> createState() => _MainViewState();
}

class _MainViewState extends State<MainView> {
  late final MQTTManager manager;
  late final MQTTAppState appState;

  @override
  void initState() {
    super.initState();
    manager = widget.manager;
    appState = widget.mqttAppState;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('MQTT Messages')),
      body: Column(
        children: [
          Expanded(
            child: Consumer<MQTTAppState>(
              builder: (_, state, __) {
                final messages = state.getHistoryText.split('\n').where((m) => m.isNotEmpty);
                return ListView(
                  children: messages.map((msg) => ListTile(title: Text(msg))).toList(),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ElevatedButton(
              onPressed: manager.disconnect,
              child: const Text('Disconnect'),
            ),
          ),
        ],
      ),
    );
  }
}
