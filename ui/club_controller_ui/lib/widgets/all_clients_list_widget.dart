import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:flutter/material.dart';

import 'package:club_controller_ui/model/gpio_client.dart';
import 'package:club_controller_ui/model/led_strip_client.dart';
import 'package:club_controller_ui/model/nec_led_strip_client.dart';
import 'gpio_control_widget.dart';
import 'led_strip_control_widget.dart';
import 'nec_led_strip_control_widget.dart';

import 'package:club_controller_ui/color_helper.dart';

class AllClientsControlList extends StatelessWidget {
  final List<GpioClient> gpioClients;
  final List<LedStripClient> ledStripClients;
  final List<NecLedStripClient> necLedStripClients;
  final ClientCommunication clientCommunication;

  AllClientsControlList(
      {Key? key,
      required this.gpioClients,
      required this.ledStripClients,
      required this.necLedStripClients,
      required this.clientCommunication})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Card(
          child: LedStripControlList(
              ledStripClients: ledStripClients,
              clientCommunication: clientCommunication),
        ),
        Card(
          child: NecLedStripControlList(
              necLedStripClients: necLedStripClients,
              clientCommunication: clientCommunication),
        ),
        Card(
          child: GpioControlList(
              gpioClients: gpioClients,
              clientCommunication: clientCommunication),
        ),
      ],
    );
  }
}

class LedStripControlList extends StatelessWidget {
  final List<LedStripClient> ledStripClients;
  final ClientCommunication clientCommunication;

  LedStripControlList(
      {Key? key,
      required this.ledStripClients,
      required this.clientCommunication})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
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
                ledStripParameters: LedStripParameters(
                    client: client,
                    onClientValueChanged: () {
                      clientCommunication.send(
                          WebsocketActionId.CLIENT_VALUE_UPDATED,
                          {"client": client.toJson()});
                    }),
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
  final ClientCommunication clientCommunication;

  NecLedStripControlList(
      {Key? key,
      required this.necLedStripClients,
      required this.clientCommunication})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          "Nec Led Strips",
          style: Theme.of(context).textTheme.headline4,
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
  final List<GpioClient> gpioClients;
  final ClientCommunication clientCommunication;

  GpioControlList(
      {Key? key, required this.gpioClients, required this.clientCommunication})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
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
