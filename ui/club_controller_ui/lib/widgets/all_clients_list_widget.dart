import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:club_controller_ui/model/client.dart';
import 'package:flutter/material.dart';

import 'package:club_controller_ui/model/gpio_client.dart';
import 'package:club_controller_ui/model/led_strip_client.dart';
import 'package:club_controller_ui/model/nec_led_strip_client.dart';
import 'gpio_control_widget.dart';
import 'led_strip_control_widget.dart';
import 'nec_led_strip_control_widget.dart';

import 'package:club_controller_ui/color_helper.dart';

bool hideClientList(List<Client> clients, bool onlyMainComponents, uiConfig) {
  return clients.isEmpty ||
      uiConfig["main_ui_components"] == null ||
      uiConfig["main_ui_components"].isEmpty ||
      onlyMainComponents &&
          clients
              .where((c) => uiConfig["main_ui_components"]
                  .where((ui_c) =>
                      ui_c["uid"] == c.uid && ui_c["show_in_main_ui"] == true)
                  .isNotEmpty)
              .isEmpty;
}

class AllClientsControlList extends StatelessWidget {
  final List<GpioClient> gpioClients;
  final List<LedStripClient> ledStripClients;
  final List<NecLedStripClient> necLedStripClients;
  final Map<String, dynamic> uiConfig;

  AllClientsControlList(
      {Key? key,
      required this.gpioClients,
      required this.ledStripClients,
      required this.necLedStripClients,
      required this.uiConfig})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        gpioClients.isEmpty
            ? Center()
            : Card(
                child: GpioControlList(
                  uiConfig: uiConfig,
                  gpioClients: gpioClients,
                ),
              ),
        ledStripClients.isEmpty
            ? Center()
            : Card(
                child: LedStripControlList(
                  ledStripClients: ledStripClients,
                  uiConfig: uiConfig,
                ),
              ),
        necLedStripClients.isEmpty
            ? Center()
            : Card(
                child: NecLedStripControlList(
                  necLedStripClients: necLedStripClients,
                  uiConfig: uiConfig,
                ),
              ),
      ],
    );
  }
}

bool isMainUiComponent(client, uiConfig) {
  return uiConfig["main_ui_components"] != null &&
      uiConfig["main_ui_components"]
          .where((ui_c) =>
              ui_c["uid"] == client.uid && ui_c["show_in_main_ui"] == true)
          .isNotEmpty;
}

class LedStripControlList extends StatelessWidget {
  final List<LedStripClient> ledStripClients;
  final Map<String, dynamic> uiConfig;

  LedStripControlList(
      {Key? key, required this.ledStripClients, required this.uiConfig})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          "Led Strips",
          style: Theme.of(context).textTheme.headline5,
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
                showInMainUI: isMainUiComponent(client, uiConfig),
                ledStripParameters: LedStripParameters(
                    client: client,
                    onClientValueChanged: () {
                      clientCommunication.send(
                          WebsocketActionId.CLIENT_VALUE_UPDATED,
                          {"client": client.toJson()});
                    }),
                ledStripPresets: uiConfig["led_strip_presets"] != null &&
                        uiConfig["led_strip_presets"].isNotEmpty
                    ? uiConfig["led_strip_presets"]
                    : [],
                onColorChanged: (new_color) {
                  client.color = toJsonColor(new_color);
                  clientCommunication.send(
                      WebsocketActionId.CLIENT_VALUE_UPDATED,
                      {"client": client.toJson()});
                },
                onColorAdded: (new_colors) {
                  client.color_templates =
                      new_colors.map((color) => toJsonColor(color)).toList();
                  clientCommunication.send(
                      WebsocketActionId.CLIENT_VALUE_UPDATED,
                      {"client": client.toJson()});
                },
                onColorRemoved: (new_colors) {
                  client.color_templates =
                      new_colors.map((color) => toJsonColor(color)).toList();
                  clientCommunication.send(
                      WebsocketActionId.CLIENT_VALUE_UPDATED,
                      {"client": client.toJson()});
                },
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class NecLedStripControlList extends StatelessWidget {
  final List<NecLedStripClient> necLedStripClients;
  final Map<String, dynamic> uiConfig;

  NecLedStripControlList(
      {Key? key, required this.necLedStripClients, required this.uiConfig})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          "Nec Led Strips",
          style: Theme.of(context).textTheme.headline5,
        ),
        Column(
          children: necLedStripClients.map((client) {
            return Card(
              child: NecLedStripControl(
                color: client.is_connected
                    ? client.color
                    : toJsonColor(Colors.black54),
                colors: client.color_templates,
                title: Text(client.name,
                    style: client.is_connected
                        ? Theme.of(context).textTheme.bodyText1
                        : TextStyle(
                            color: Colors.black54,
                            decoration: TextDecoration.lineThrough,
                          )),
                showInMainUI: isMainUiComponent(client, uiConfig),
                client: client,
                onAvatarTap: () {
                  clientCommunication.sendNecCommand(
                      client.toJson(), "0xFF02FD");
                },
                onColorChanged: (new_color) {
                  client.color = new_color;
                  clientCommunication.send(
                      WebsocketActionId.CLIENT_VALUE_UPDATED,
                      {"client": client.toJson()});
                  clientCommunication.sendNecCommand(
                      client.toJson(), new_color["nec"]);
                },
                onTextInput: (text) {
                  clientCommunication.sendNecCommand(client.toJson(), text);
                },
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class GpioControlList extends StatelessWidget {
  final Map<String, dynamic> uiConfig;
  final List<GpioClient> gpioClients;

  GpioControlList({Key? key, required this.uiConfig, required this.gpioClients})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          "GPIOs",
          style: Theme.of(context).textTheme.headline5,
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
                showInMainUI: isMainUiComponent(client, uiConfig),
                client: client,
                gpio_modes: client.gpio_modes,
                gpio_values: client.gpio_values,
                onValueChanged: (new_gpios) {
                  client.gpio_values = new_gpios;
                  clientCommunication.send(
                      WebsocketActionId.CLIENT_VALUE_UPDATED,
                      {"client": client.toJson()});
                },
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}
