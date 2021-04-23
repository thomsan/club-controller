import 'client_communication.dart';
import 'package:flutter/material.dart';
import 'start_page.dart';
import 'dart:convert';
import 'model/client.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';

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
  List<LedStripClient> _led_strip_clients = List.empty(growable: true);

  @override
  void initState() {
    super.initState();
    clientCommunication.addListener(_onMessageReceived);
    clientCommunication.sendActionId(WebsocketActionId.CLIENT_LIST_REQUEST);
  }

  @override
  void dispose() {
    clientCommunication.removeListener(_onMessageReceived);
    super.dispose();
  }

  /// -------------------------------------------------------------------
  /// This routine handles all messages that are sent by the server.
  /// In this page, the following actions have to be processed
  ///  - connection
  /// -------------------------------------------------------------------
  _onMessageReceived(message) {
    print("_ControllerPageState message received");
    int action = message["action"];
    switch (WebsocketActionId.values[action]) {
      case WebsocketActionId.CLIENT_LIST:
        String clients_json = json.encode(message["clients"]);
        print("clients_json");
        print(clients_json);
        Iterable list = json.decode(clients_json);
        print("list");
        print(list);
        setState(() {
          _led_strip_clients = list
              .where((client) =>
                  // TODO validate client["typeId"]
                  ClientTypeId.values[client["type_id"]] ==
                  ClientTypeId.LED_STRIP_CLIENT)
              .map((_client) => LedStripClient.fromJson(_client))
              .toList(growable: true);
          print("Setting state: ");
          print(_led_strip_clients);
        });
        break;

      case WebsocketActionId.CLIENT_CONNECTED:
        print("CLIENT_CONNECTED");
        print(message["client"]);
        setState(() {
          LedStripClient client = _led_strip_clients.asMap().values.firstWhere(
              (c) => c.uid == message["client"]["uid"],
              orElse: null);
          if (client != null) {
            // known client
            client.is_connected = true;
          } else {
            // new client
            _led_strip_clients.add(LedStripClient.fromJson(message["client"]));
          }
          print("Setting state: ");
          print(_led_strip_clients);
        });
        break;

      case WebsocketActionId.CLIENT_DISCONNECTED:
        print("CLIENT_DISCONNECTED");
        print(message["client"]);
        setState(() {
          LedStripClient client = _led_strip_clients.asMap().values.firstWhere(
              (c) => c.uid == message["client"]["uid"],
              orElse: null);
          if (client != null) {
            client.is_connected = false;
          }
          //.removeWhere((c) => c.uid == message["client"]["uid"]);
          print("Setting state: ");
          print(_led_strip_clients);
        });
        break;

      default:
        // ignore all other messages
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            LedStripList(ledStripClients: _led_strip_clients),
            Form(
              child: TextFormField(
                controller: _debugController,
                decoration: InputDecoration(
                    labelText: 'Send message with given action id'),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                clientCommunication.sendActionId(
                    WebsocketActionId.values[int.parse(_debugController.text)]);
              },
              child: Text('Send'),
            ),
          ],
        ),
      ),
    );
  }
}

class ClientList extends StatefulWidget {
  final String title = "Club Controller";

  @override
  _ControllerPageState createState() => _ControllerPageState();
}

class LedStripItem extends StatelessWidget {
  LedStripItem({
    required this.client,
  }) : super(key: ObjectKey(client));

  final LedStripClient client;

  Color _getColor(BuildContext context) {
    // The theme depends on the BuildContext because different
    // parts of the tree can have different themes.
    // The BuildContext indicates where the build is
    // taking place and therefore which theme to use.

    return client.is_connected //
        ? Theme.of(context).primaryColor
        : Colors.black54;
  }

  TextStyle? _getTextStyle(BuildContext context) {
    if (client.is_connected) return null;

    return TextStyle(
      color: Colors.black54,
      decoration: TextDecoration.lineThrough,
    );
  }

  Color fromJsonColor(color) {
    return Color.fromARGB(255, color["r"], color["g"], color["b"]);
  }

  Map<String, int> toJsonColor(color) {
    return {"r": color.red, "g": color.green, "b": color.blue};
  }

  void changeColor(Color color) {
    client.color = toJsonColor(color);
    clientCommunication.send(
        WebsocketActionId.CLIENT_VALUE_UPDATED, {"client": client.toJson()});
  }

  void addColorTemplate(Map<String, int> color) {
    client.color_templates.add(color);
    clientCommunication.send(
        WebsocketActionId.CLIENT_VALUE_UPDATED, {"client": client.toJson()});
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Expanded(
            flex: 1,
            child: CircleAvatar(
              backgroundColor: _getColor(context),
            ),
          ),
          Expanded(
            flex: 2,
            child: Text(client.name, style: _getTextStyle(context)),
          ),
          Expanded(
            flex: 3,
            child: Row(
              children: _buildColorTemplateList(),
            ),
          ),
          DropdownButton(
            items: <String>['Add new color template', 'Change color']
                .map<DropdownMenuItem<String>>((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (value) {
              switch (value) {
                case 'Add new color template':
                  addColorTemplate(client.color);
                  break;
                case 'Change color':
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return AlertDialog(
                        titlePadding: const EdgeInsets.all(0.0),
                        contentPadding: const EdgeInsets.all(0.0),
                        content: SingleChildScrollView(
                          child: ColorPicker(
                            pickerColor: fromJsonColor(client.color),
                            onColorChanged: changeColor,
                            colorPickerWidth: 300.0,
                            pickerAreaHeightPercent: 0.7,
                            enableAlpha: true,
                            displayThumbColor: true,
                            showLabel: true,
                            paletteType: PaletteType.hsv,
                            pickerAreaBorderRadius: const BorderRadius.only(
                              topLeft: const Radius.circular(2.0),
                              topRight: const Radius.circular(2.0),
                            ),
                          ),
                        ),
                      );
                    },
                  );
                  break;
                default:
              }
            },
          ),
          ElevatedButton(
            child: const Icon(
              Icons.more_vert,
              size: 16.0,
            ),
            onPressed: () {
              showDialog(
                context: context,
                builder: (BuildContext context) {
                  return AlertDialog(
                    titlePadding: const EdgeInsets.all(0.0),
                    contentPadding: const EdgeInsets.all(0.0),
                    content: SingleChildScrollView(
                      child: ColorPicker(
                        pickerColor: fromJsonColor(client.color),
                        onColorChanged: changeColor,
                        colorPickerWidth: 300.0,
                        pickerAreaHeightPercent: 0.7,
                        enableAlpha: true,
                        displayThumbColor: true,
                        showLabel: true,
                        paletteType: PaletteType.hsv,
                        pickerAreaBorderRadius: const BorderRadius.only(
                          topLeft: const Radius.circular(2.0),
                          topRight: const Radius.circular(2.0),
                        ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }

  List<Widget> _buildColorTemplateList() {
    List<ElevatedButton> color_buttons =
        []; // this will hold Rows according to available lines
    for (var color in client.color_templates) {
      color_buttons.add(ElevatedButton(
        child: null,
        style: ElevatedButton.styleFrom(
          primary: fromJsonColor(color), // background
          onPrimary: Colors.white, // foreground
        ),
        onPressed: () {
          changeColor(fromJsonColor(color));
        },
      ));
    }
    return color_buttons;
  }
}

class LedStripList extends StatelessWidget {
  final List<LedStripClient> ledStripClients;

  LedStripList({Key? key, required this.ledStripClients}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: ListView(
        padding: EdgeInsets.symmetric(vertical: 8.0),
        children: ledStripClients.map((client) {
          return LedStripItem(
            client: client,
          );
        }).toList(),
      ),
    );
  }
}
