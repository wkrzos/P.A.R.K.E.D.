import 'package:flutter/material.dart';
import '../mqtt/mqtt_client.dart';
import '../mqtt/mqtt_state.dart';
import 'package:provider/provider.dart';

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
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('MQTT Messages')),
      body: Column(
        children: [
          Expanded(
            // Rebuilds when the state changes
            child: Consumer<MQTTAppState>(
              builder: (_, state, __) {
                final messages = state.getHistoryText.split('\n').where((m) => m.isNotEmpty);
                return ListView.builder(
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    return ListTile(
                      title: Text(messages.elementAt(index)),
                    );
                  },
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: ElevatedButton(
              onPressed: widget.manager.disconnect,
              child: const Text('Disconnect'),
            ),
          ),
        ],
      ),
    );
  }
}
