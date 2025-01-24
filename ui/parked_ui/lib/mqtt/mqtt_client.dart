import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'mqtt_state.dart';

class MQTTManager {
  final MQTTAppState _currentState;
  final String _host;
  final String _topic;
  late final MqttServerClient _client;

  MQTTManager({
    required String host,
    required String topic,
    required MQTTAppState state,
  })  : _host = host,
        _topic = topic,
        _currentState = state {
    _initializeMQTTClient();
  }

  void _initializeMQTTClient() {
    _client = MqttServerClient(_host, '');
    _client.port = 1883;
    _client.keepAlivePeriod = 20;
    _client.secure = false;
    _client.logging(on: true);


    _client.onConnected = onConnected;
    _client.onDisconnected = onDisconnected;
    _client.onSubscribed = onSubscribed;

    _client.connectionMessage = MqttConnectMessage()
        .withClientIdentifier('FlutterClient')
        .startClean()
        .withWillQos(MqttQos.atLeastOnce);
  }

  Future<bool> connect() async {
    try {
      _currentState.setAppConnectionState(MQTTAppConnectionState.connecting);
      await _client.connect();
      return true;
    } on Exception {
      _currentState.setAppConnectionState(MQTTAppConnectionState.disconnected);
      return false;
    }
  }

  void disconnect() {
    _client.disconnect();
  }

  void publish(String message) {
    final builder = MqttClientPayloadBuilder();
    builder.addString(message);
    _client.publishMessage(_topic, MqttQos.exactlyOnce, builder.payload!);
  }

void onConnected() {
  _currentState.setAppConnectionState(MQTTAppConnectionState.connected);



  _client.updates!.listen((List<MqttReceivedMessage<MqttMessage?>>? messages) {
    if (messages != null && messages.isNotEmpty) {
      final MqttPublishMessage recMess =
          messages[0].payload as MqttPublishMessage;
      final String message =
          MqttPublishPayload.bytesToStringAsString(recMess.payload.message);

      _currentState.setReceivedText(message);
    }
  });
}


void onDisconnected() {
  if (_client.connectionStatus!.returnCode ==
      MqttConnectReturnCode.noneSpecified) {
  } 
  _currentState.setAppConnectionState(MQTTAppConnectionState.disconnected);

  // Optionally reconnect
  Future.delayed(const Duration(seconds: 3), () {
    connect();
  });
}


  void onSubscribed(String topic) {
  }
}
