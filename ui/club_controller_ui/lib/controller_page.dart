import 'dart:io';

import 'client_communication.dart';
import 'package:flutter/material.dart';
import 'start_page.dart';
import 'dart:convert';
import 'model/client.dart';
import 'package:flutter_colorpicker/flutter_colorpicker.dart';

Color fromJsonColor(color) {
  return Color.fromARGB(255, color["r"], color["g"], color["b"]);
}

Map<String, int> toJsonColor(color) {
  return {"r": color.red, "g": color.green, "b": color.blue};
}

Future<dynamic> showColorPicker(
    BuildContext context, Color color, Function(Color) onCollorChanged) {
  return showDialog(
    context: context,
    builder: (BuildContext context) {
      return AlertDialog(
        titlePadding: const EdgeInsets.all(0.0),
        contentPadding: const EdgeInsets.all(0.0),
        content: SingleChildScrollView(
          child: ColorPicker(
            pickerColor: color,
            onColorChanged: onCollorChanged,
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
}

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
        print(message["client"]);
        setState(() {
          LedStripClient client = _led_strip_clients.asMap().values.firstWhere(
              (c) => c.uid == message["client"]["uid"],
              orElse: null);
          if (client != null) {
            // known client
            client.is_connected = true;
          } else {
            switch (message["client"]["type_id"]) {
              case ClientTypeId.LED_STRIP_CLIENT:
                _led_strip_clients
                    .add(LedStripClient.fromJson(message["client"]));
                break;
              case ClientTypeId.GPIO_CLIENT:
                _gpio_clients.add(GpioClient.fromJson(message["client"]));
                break;
              default:
            }
          }
        });
        break;

      case WebsocketActionId.CLIENT_DISCONNECTED:
        print("CLIENT_DISCONNECTED");
        print(message["client"]);
        setState(() {
          Client? client = null;
          switch (message["client"]["type_id"]) {
            case ClientTypeId.LED_STRIP_CLIENT:
              client = _led_strip_clients.asMap().values.firstWhere(
                  (c) => c.uid == message["client"]["uid"],
                  orElse: null);
              break;
            case ClientTypeId.GPIO_CLIENT:
              client = _gpio_clients.asMap().values.firstWhere(
                  (c) => c.uid == message["client"]["uid"],
                  orElse: null);
              break;
            default:
          }

          if (client != null) {
            client.is_connected = false;
          }
        });
        break;

      case WebsocketActionId.CLIENT_LIST:
        setState(() {
          _led_strip_clients = (message["clients"] as List)
              .where((client) =>
                  // TODO validate client["typeId"]
                  ClientTypeId.values[client["type_id"]] ==
                  ClientTypeId.LED_STRIP_CLIENT)
              .map((client) => LedStripClient.fromJson(client))
              .toList(growable: true);
          _gpio_clients = (message["clients"] as List)
              .where((client) =>
                  // TODO validate client["typeId"]
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
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Expanded(
              child: Card(
                child: Column(
                  children: [
                    Text(
                      "Overall control",
                      style: Theme.of(context).textTheme.headline4,
                    ),
                    OverallControl(ui_config: _ui_config)
                  ],
                ),
              ),
            ),
            LedStripControlList(ledStripClients: _led_strip_clients),
            GpioControlList(gpioClients: _gpio_clients),
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

class ColorTemplates extends StatelessWidget {
  final List<Color> colors;
  final Function(Color)? onPressed;
  final Function(Color)? onLongPressed;
  ColorTemplates(
      {Key? key, required this.colors, this.onPressed, this.onLongPressed})
      : super(key: key);

  List<Widget> _buildColorTemplateList() {
    List<ElevatedButton> color_buttons =
        []; // this will hold Rows according to available lines
    for (var color in colors) {
      color_buttons.add(ElevatedButton(
          child: null,
          style: ElevatedButton.styleFrom(
            primary: color, // background
            onPrimary: Colors.white, // foreground
          ),
          onPressed: () {
            onPressed!(color);
          },
          onLongPress: () {
            onLongPressed!(color);
          }));
    }
    return color_buttons;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5.0),
      child: Row(
        children: _buildColorTemplateList(),
      ),
    );
  }
}

class GpioButtons extends StatelessWidget {
  final List<bool> gpios;
  final Function(List<bool>)? onPressed;

  GpioButtons({Key? key, required this.gpios, this.onPressed})
      : super(key: key);

  List<Widget> _buildGpioButtonList() {
    List<ElevatedButton> gpio_buttons =
        []; // this will hold Rows according to available lines
    for (var gpio in gpios) {
      gpio_buttons.add(ElevatedButton(
        child: null,
        style: ElevatedButton.styleFrom(
          primary: gpio ? Colors.blueAccent : Colors.black54, // background
          onPrimary: Colors.white, // foreground
        ),
        onPressed: () {
          onPressed!(gpios);
        },
      ));
    }
    return gpio_buttons;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5.0),
      child: Row(
        children: _buildGpioButtonList(),
      ),
    );
  }
}

class OverallControl extends StatelessWidget {
  final Map<String, dynamic> ui_config;

  OverallControl({Key? key, required this.ui_config}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Column(children: [
          Expanded(
            child: LedStripControl(
              color: fromJsonColor(ui_config["color"]),
              colors: (ui_config["color_templates"] as List)
                  .map((color) => fromJsonColor(color))
                  .toList(),
              title: Text("All Led strips",
                  style: Theme.of(context).textTheme.bodyText1),
              onColorChanged: (new_color) {
                clientCommunication.send(WebsocketActionId.UI_CONFIG_UPDATED,
                    {"color": toJsonColor(new_color)});
                clientCommunication.send(
                    WebsocketActionId.ALL_LED_STRIPS_UPDATED,
                    {"color": toJsonColor(new_color)});
              },
              onColorAdded: (new_colors) {
                clientCommunication.send(WebsocketActionId.UI_CONFIG_UPDATED, {
                  "color_templates":
                      new_colors.map((color) => toJsonColor(color)).toList()
                });
              },
              onColorRemoved: (new_colors) {
                clientCommunication.send(WebsocketActionId.UI_CONFIG_UPDATED, {
                  "color_templates":
                      new_colors.map((color) => toJsonColor(color)).toList()
                });
              },
            ),
          ),
        ]),
      ),
    );
  }
}

class LedStripControl extends StatelessWidget {
  final Color color;
  final List<Color> colors;
  final Text title;
  Function(Color) onColorChanged;
  Function(List<Color>) onColorAdded;
  Function(List<Color>) onColorRemoved;

  LedStripControl(
      {Key? key,
      required this.color,
      required this.colors,
      required this.title,
      required this.onColorChanged,
      required this.onColorAdded,
      required this.onColorRemoved})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Expanded(
            flex: 1,
            child: GestureDetector(
              onTap: () {
                showColorPicker(context, color, onColorChanged);
              },
              onLongPress: () {
                colors.add(color);
                onColorAdded(colors);
              },
              child: CircleAvatar(
                backgroundColor: color,
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: title,
          ),
          Expanded(
            flex: 3,
            child: ColorTemplates(
              colors: colors,
              onPressed: onColorChanged,
              onLongPressed: (color) {
                colors.remove(color);
                onColorRemoved(colors);
              },
            ),
          ),
        ],
      ),
    );
  }
}

class GPIOControl extends StatelessWidget {
  final Text title;
  final List<bool> gpios;
  Function(List<bool>) onValueChanged;

  GPIOControl(
      {Key? key,
      required this.title,
      required this.gpios,
      required this.onValueChanged})
      : super(key: key);

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
              backgroundColor: Theme.of(context).accentColor,
            ),
          ),
          Expanded(
            flex: 2,
            child: title,
          ),
          Expanded(
            flex: 3,
            child: GpioButtons(
              gpios: gpios,
              onPressed: onValueChanged,
            ),
          ),
        ],
      ),
    );
  }
}

class LedStripControlList extends StatelessWidget {
  final List<LedStripClient> ledStripClients;

  LedStripControlList({Key? key, required this.ledStripClients})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Column(
          children: [
            Text(
              "Led Strips",
              style: Theme.of(context).textTheme.headline4,
            ),
            Column(
              children: ledStripClients.map((client) {
                return Card(
                  child: LedStripControl(
                    color: client.is_connected
                        ? fromJsonColor(client.color)
                        : Colors.black54,
                    colors: client.color_templates
                        .map((color) => fromJsonColor(color))
                        .toList(),
                    title: Text(client.name,
                        style: client.is_connected
                            ? Theme.of(context).textTheme.bodyText1
                            : TextStyle(
                                color: Colors.black54,
                                decoration: TextDecoration.lineThrough,
                              )),
                    onColorChanged: (new_color) {
                      client.color = toJsonColor(new_color);
                      clientCommunication.send(
                          WebsocketActionId.CLIENT_VALUE_UPDATED,
                          {"client": client.toJson()});
                    },
                    onColorAdded: (new_colors) {
                      client.color_templates = new_colors
                          .map((color) => toJsonColor(color))
                          .toList();
                      clientCommunication.send(
                          WebsocketActionId.CLIENT_VALUE_UPDATED,
                          {"client": client.toJson()});
                    },
                    onColorRemoved: (new_colors) {
                      client.color_templates = new_colors
                          .map((color) => toJsonColor(color))
                          .toList();
                      clientCommunication.send(
                          WebsocketActionId.CLIENT_VALUE_UPDATED,
                          {"client": client.toJson()});
                    },
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class GpioControlList extends StatelessWidget {
  final List<GpioClient> gpioClients;

  GpioControlList({Key? key, required this.gpioClients}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Column(
          children: [
            Text(
              "GPIOs",
              style: Theme.of(context).textTheme.headline4,
            ),
            Column(
              children: gpioClients.map((client) {
                return Card(
                  child: GPIOControl(
                    title: Text(client.name,
                        style: client.is_connected
                            ? Theme.of(context).textTheme.bodyText1
                            : TextStyle(
                                color: Colors.black54,
                                decoration: TextDecoration.lineThrough,
                              )),
                    gpios: client.gpios,
                    onValueChanged: (new_gpios) {
                      client.gpios = new_gpios;
                      clientCommunication.send(
                          WebsocketActionId.CLIENT_VALUE_UPDATED,
                          {"client": client.toJson()});
                    },
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}
