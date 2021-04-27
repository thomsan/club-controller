import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

///
/// Application-level global variable to access the WebSockets
///
WebSocketNotifications socket = new WebSocketNotifications();

///
/// Put your WebSockets server IP address and port number
///
String? serverAddress; //"ws://$hostname:60124";

class WebSocketNotifications {
  static final WebSocketNotifications _socket =
      new WebSocketNotifications._internal();

  factory WebSocketNotifications() {
    return _socket;
  }

  WebSocketNotifications._internal();

  ///
  /// The WebSocket "open" channel
  ///
  WebSocketChannel? _channel;

  ///
  /// Is the connection established?
  ///
  bool _isOn = false;

  ///
  /// Listeners
  /// List of methods to be called when a new message
  /// comes in.
  ///
  ObserverList<Function> _listeners = new ObserverList<Function>();

  /// ----------------------------------------------------------
  /// Initialization the WebSockets connection with the server
  /// ----------------------------------------------------------

  Future<void> initCommunication() async {
    try {
      ///
      /// Just in case, close any previous communication
      ///
      reset();

      ///
      /// Open a new WebSocket communication
      ///
      _channel = new WebSocketChannel.connect(Uri.parse(serverAddress!));

      ///
      /// Start listening to new notifications / messages
      ///
      _channel!.stream.listen(_onReceptionOfMessageFromServer);
    } catch (e) {
      ///
      /// General error handling
      /// TODO
      ///
      return Future.error(e);
    }
  }

  /// ----------------------------------------------------------
  /// Closes the WebSocket communication
  /// ----------------------------------------------------------
  reset() {
    if (_channel != null) {
      _channel!.sink.close();
      _isOn = false;
    }
  }

  /// ---------------------------------------------------------
  /// Sends a message to the server
  /// ---------------------------------------------------------
  send(String message) {
    if (_channel != null && _isOn) {
      _channel!.sink.add(message);
    }
  }

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

  /// ----------------------------------------------------------
  /// Callback which is invoked each time that we are receiving
  /// a message from the server
  /// ----------------------------------------------------------
  _onReceptionOfMessageFromServer(message) {
    _isOn = true;
    _listeners.forEach((Function callback) {
      callback(message);
    });
  }
}
