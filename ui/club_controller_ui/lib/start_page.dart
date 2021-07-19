import 'websocket.dart';
import 'client_communication.dart';
import 'package:flutter/material.dart';
import 'controller_page.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Define a custom Form widget.
class WebsocketAddressForm extends StatefulWidget {
  final TextEditingController controller;
  final VoidCallback onPressed;

  WebsocketAddressForm({required this.controller, required this.onPressed});

  @override
  _WebsocketAddressFormState createState() {
    return _WebsocketAddressFormState();
  }
}

class _WebsocketAddressFormState extends State<WebsocketAddressForm> {
  // Create a global key that uniquely identifies the Form widget
  // and allows validation of the form.
  //
  // Note: This is a `GlobalKey<FormState>`,
  // not a GlobalKey<WebsocketAddressFormState>.
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    // Build a Form widget using the _formKey created above.
    return Form(
      key: _formKey,
      child: Column(
        children: <Widget>[
          TextFormField(
            decoration: InputDecoration(
                labelText:
                    'Enter server websocket address e.g. ws://localhost:60124'),
            controller: widget.controller,
            // The validator receives the text that the user has entered.
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter a valid websocket address.';
              }
              return null;
            },
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              primary: ColorScheme.fromSwatch().primary, // background
              onPrimary: Colors.white, // foreground
            ),
            onPressed: () {
              // Validate returns true if the form is valid, or false otherwise.
              if (_formKey.currentState!.validate()) {
                widget.onPressed();
              }
            },
            child: Text('Connect'),
          ),
        ],
      ),
    );
  }
}

class StartPage extends StatefulWidget {
  @override
  _StartPageState createState() => _StartPageState();
}

class _StartPageState extends State<StartPage> {
  static final TextEditingController _textEditingController =
      new TextEditingController();

  late Future<String> _websocketAddress;

  Future<SharedPreferences> _prefs = SharedPreferences.getInstance();

  Future<void> _setWebSocketAddress(String webSocketAddress) async {
    final SharedPreferences prefs = await _prefs;

    setState(() {
      _websocketAddress = prefs
          .setString("websocket_address", webSocketAddress)
          .then((bool success) {
        return webSocketAddress;
      });
    });
  }

  @override
  void initState() {
    super.initState();
    // get stored websocket address
    _websocketAddress = _prefs.then((SharedPreferences prefs) {
      return (prefs.getString('websocket_address') ?? "ws://localhost:60124");
    });
    _websocketAddress.then((value) {
      print("Loaded websocketAddres: $value");
      _textEditingController.text = value;
      _onConnect();
    });
  }

  @override
  void dispose() {
    clientCommunication.removeListener(_onMessageReceived);
    super.dispose();
  }

  /// -------------------------------------------------------------------
  /// This routine handles all messages that are sent by the server.
  /// In this page, only the following action has to be processed
  ///  - connection
  /// -------------------------------------------------------------------
  _onMessageReceived(message) {
    int action = message["action"];
    switch (WebsocketActionId.values[action]) {

      ///
      /// When the websocket connection is established, we start the app
      ///
      case WebsocketActionId.HELLO:
        ScaffoldMessenger.of(context).clearSnackBars();
        // save websocket address for next time
        _setWebSocketAddress(serverAddress!);
        Navigator.push(
            context,
            new MaterialPageRoute(
              builder: (BuildContext context) => new ControllerPage(),
            ));
        break;
      default:
        // ignore all other messages
        break;
    }
  }

  /// -----------------------------------------------------------
  /// If the websocket is not yet connected, let the user enter
  /// the websocket address and connect
  /// -----------------------------------------------------------
  Widget _buildConnect() {
    return new Container(
      padding: const EdgeInsets.all(16.0),
      child: new Column(
        children: <Widget>[
          new WebsocketAddressForm(
              controller: _textEditingController, onPressed: _onConnect)
        ],
      ),
    );
  }

  /// --------------------------------------------------------------
  /// Try to establish the websocket connection, if user clicks connect
  /// --------------------------------------------------------------
  _onConnect() {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('Connecting...')));
    // setup the websocket server address and init the ClientCommunication singleton
    serverAddress = _textEditingController.text;
    clientCommunication
        .init()
        .then((value) => clientCommunication.addListener(_onMessageReceived))
        .catchError((e) => _onConnectionError(e));
  }

  _onConnectionError(e) {
    print(e.toString());
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        backgroundColor: Colors.red,
        content: Text('Couldn\'t connect to given server address')));
  }

  @override
  Widget build(BuildContext context) {
    return new SafeArea(
        bottom: false,
        top: false,
        child: Scaffold(
          appBar: new AppBar(
            title: new Text('Establish connection'),
          ),
          body: _buildConnect(),
        ));
  }
}
