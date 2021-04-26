import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'websocket.dart';

///
/// Application-level global variable
///
ClientCommunication clientCommunication = ClientCommunication._internal();

enum ClientTypeId {
  LED_STRIP_CLIENT,
  CONTROLLER_CLIENT,
  GPIO_CLIENT,
  SMOKE_MACHINE_CLIENT,
}

enum WebsocketActionId {
  HELLO,
  CLIENT_LIST_REQUEST,
  CLIENT_LIST,
  CLIENT_CONNECTED,
  CLIENT_DISCONNECTED,
  CLIENT_VALUE_UPDATED,
  ALL_LED_STRIPS_UPDATED,
  UI_CONFIG_REQUEST,
  UI_CONFIG,
  UI_CONFIG_UPDATED,
}

class ClientCommunication {
  static final ClientCommunication _clientCommunication =
      new ClientCommunication._internal();

  factory ClientCommunication() {
    return _clientCommunication;
  }

  ClientCommunication._internal() {}

  Future<void> init() {
    socket.addListener(_onMessageReceived);
    return socket.initCommunication();
  }

  /// ----------------------------------------------------------
  /// Common handler for all received messages, from the server
  /// ----------------------------------------------------------
  _onMessageReceived(serverMessage) {
    ///
    /// As messages are sent as a String
    /// let's deserialize it to get the corresponding
    /// JSON object
    ///
    Map<String, dynamic> message = json.decode(serverMessage);
    int action = message["action"];
    print("Received message: ");
    print(message);
    switch (WebsocketActionId.values[action]) {

      ///
      /// For any other incoming message, we need to
      /// dispatch it to all the listeners
      ///
      default:
        _listeners.forEach((Function callback) {
          callback(message);
        });
        break;
    }
  }

  /// ----------------------------------------------------------
  /// Common method to send requests to the server
  /// ----------------------------------------------------------
  send(WebsocketActionId action, Map<String, dynamic> data) {
    ///
    /// Send the action to the server
    /// To send the message, we need to serialize the JSON
    ///
    socket.send(json.encode({"action": action.index, "data": data}));
  }

  sendActionId(WebsocketActionId action) {
    socket.send(json.encode({"action": action.index}));
  }

  /// ==========================================================
  ///
  /// Listeners to allow the different pages to be notified
  /// when messages come in
  ///
  ObserverList<Function> _listeners = new ObserverList<Function>();

  /// ---------------------------------------------------------
  /// Adds a callback to be invoked in case of incoming
  /// notification
  /// ---------------------------------------------------------
  addListener(Function callback) {
    _listeners.add(callback);
  }

  removeListener(Function callback) {
    _listeners.remove(callback);
  }
}
