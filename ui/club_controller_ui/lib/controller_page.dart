import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:collection/collection.dart';
import 'communication/client_communication.dart';
import 'model/client.dart';
import 'widgets/all_clients_list_widget.dart';
import 'widgets/overall_control_widget.dart';
import 'widgets/led_strip_control_widget.dart';
import 'model/gpio_client.dart';
import 'model/led_strip_client.dart';
import 'model/nec_led_strip_client.dart';

class ControllerPage extends StatefulWidget {
  final String title = "Club Controller";

  @override
  _ControllerPageState createState() => _ControllerPageState();
}

class _ControllerPageState extends State<ControllerPage> {
  TextEditingController _debugController = TextEditingController();

  ///
  /// At first initialization, the client list is empty
  ///
  List<Map<String, dynamic>> _clients = List.empty(growable: true);
  List<LedStripClient> _led_strip_clients = List.empty(growable: true);
  List<NecLedStripClient> _nec_led_strip_clients = List.empty(growable: true);
  List<GpioClient> _gpio_clients = List.empty(growable: true);
  Map<String, dynamic> _ui_config = {};

  @override
  void initState() {
    super.initState();
    clientCommunication.addListener(_onMessageReceived);
    clientCommunication.sendActionId(WebsocketActionId.CLIENT_LIST_REQUEST);
    clientCommunication.sendActionId(WebsocketActionId.UI_CONFIG_REQUEST);
  }

  @override
  void dispose() {
    clientCommunication.removeListener(_onMessageReceived);
    super.dispose();
  }

  /*List<LedStripClient> getLedStripClients(){
    return _clients.where((c) => c.type_id == ClientTypeId.LED_STRIP_CLIENT).toList().cast<LedStripClient>();
  }

  List<GpioClient> getGpioClients(){
    return _clients.where((c) => c.type_id == ClientTypeId.GPIO_CLIENT).toList().cast<GpioClient>();
  }*/

  Client? getClient(Map<String, dynamic> clientJson) {
    Client? client = null;
    switch (ClientTypeId.values[clientJson["type_id"]]) {
      case ClientTypeId.LED_STRIP_CLIENT:
        client = _led_strip_clients
            .firstWhereOrNull((c) => c.uid == clientJson["uid"]);
        break;
      case ClientTypeId.NEC_LED_STRIP_CLIENT:
        client = _nec_led_strip_clients
            .firstWhereOrNull((c) => c.uid == clientJson["uid"]);
        break;
      case ClientTypeId.GPIO_CLIENT:
        client =
            _gpio_clients.firstWhereOrNull((c) => c.uid == clientJson["uid"]);
        break;
      default:
        int type_id = clientJson["type_id"];
        print("Unkown ClientTypeId: $type_id");
    }
    return client;
  }

  void addClient(Map<String, dynamic> clientJson) {
    switch (ClientTypeId.values[clientJson["type_id"]]) {
      case ClientTypeId.LED_STRIP_CLIENT:
        _led_strip_clients.add(LedStripClient.fromJson(clientJson));
        break;
      case ClientTypeId.NEC_LED_STRIP_CLIENT:
        _nec_led_strip_clients.add(NecLedStripClient.fromJson(clientJson));
        break;
      case ClientTypeId.GPIO_CLIENT:
        _gpio_clients.add(GpioClient.fromJson(clientJson));
        break;
      default:
    }
  }

  /// -------------------------------------------------------------------
  /// This routine handles all messages that are sent by the server.
  /// In this page, the following actions have to be processed
  ///  - connection
  /// -------------------------------------------------------------------
  _onMessageReceived(message) {
    int action = message["action"];
    switch (WebsocketActionId.values[action]) {
      case WebsocketActionId.CLIENT_CONNECTED:
        print("CLIENT_CONNECTED");
        setState(() {
          Client? client = getClient(message["client"]);
          if (client != null) {
            client.is_connected = true;
          } else {
            addClient(message["client"]);
          }
        });
        break;

      case WebsocketActionId.CLIENT_DISCONNECTED:
        print("CLIENT_DISCONNECTED");
        setState(() {
          Client? client = getClient(message["client"]);
          if (client != null) {
            client.is_connected = false;
          }
        });
        break;

      case WebsocketActionId.CLIENT_LIST:
        setState(() {
          _led_strip_clients = (message["clients"] as List)
              .where((client) =>
                  ClientTypeId.values[client["type_id"]] ==
                  ClientTypeId.LED_STRIP_CLIENT)
              .map((client) => LedStripClient.fromJson(client))
              .toList(growable: true);
          _nec_led_strip_clients = (message["clients"] as List)
              .where((client) =>
                  ClientTypeId.values[client["type_id"]] ==
                  ClientTypeId.NEC_LED_STRIP_CLIENT)
              .map((client) => NecLedStripClient.fromJson(client))
              .toList(growable: true);
          _gpio_clients = (message["clients"] as List)
              .where((client) =>
                  ClientTypeId.values[client["type_id"]] ==
                  ClientTypeId.GPIO_CLIENT)
              .map((client) => GpioClient.fromJson(client))
              .toList(growable: true);
        });
        break;

      case WebsocketActionId.UI_CONFIG:
        setState(() {
          _ui_config = message["ui"];
        });
        break;

      default:
        // ignore all other messages
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
        bottom: false,
        top: false,
        child: Scaffold(
          appBar: AppBar(
            title: Text(widget.title),
          ),
          body: Container(
            padding: const EdgeInsets.all(20.0),
            child: SingleChildScrollView(
              scrollDirection: Axis.vertical,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Card(
                    child: Column(
                      children: [
                        Text(
                          "Overall control",
                          style: Theme.of(context).textTheme.headline4,
                        ),
                        OverallControl(
                            ui_config: _ui_config,
                            clientCommunication: clientCommunication)
                      ],
                    ),
                  ),
                  Card(
                    child: AllClientsControlList(
                        gpioClients: _gpio_clients,
                        ledStripClients: _led_strip_clients,
                        necLedStripClients: _nec_led_strip_clients,
                        clientCommunication: clientCommunication),
                  ),
                  Form(
                    child: TextFormField(
                      controller: _debugController,
                      decoration: InputDecoration(
                          labelText: 'Send message with given action id'),
                    ),
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      primary: ColorScheme.fromSwatch().primary, // background
                      onPrimary: Colors.white, // foreground
                    ),
                    onPressed: () {
                      clientCommunication.sendActionId(WebsocketActionId
                          .values[int.parse(_debugController.text)]);
                    },
                    child: Text('Send'),
                  ),
                ],
              ),
            ),
          ),
        ));
  }
}

class ClientList extends StatefulWidget {
  final String title = "Club Controller";

  @override
  _ControllerPageState createState() => _ControllerPageState();
}
