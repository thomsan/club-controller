import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:club_controller_ui/model/gpio_client.dart';
import 'package:club_controller_ui/model/led_strip_client.dart';
import 'package:club_controller_ui/model/nec_led_strip_client.dart';
import 'package:club_controller_ui/widgets/strobe_control_widget.dart';
import 'package:flutter/material.dart';
import 'all_clients_list_widget.dart';
import 'led_strip_control_widget.dart';
import '../color_helper.dart';

class MainControl extends StatelessWidget {
  final List<GpioClient> gpioClients;
  final List<LedStripClient> ledStripClients;
  final List<NecLedStripClient> necLedStripClients;
  final Map<String, dynamic> ui_config;

  MainControl(
      {Key? key,
      required this.gpioClients,
      required this.ledStripClients,
      required this.necLedStripClients,
      required this.ui_config})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Card(
          child: Column(children: [
            LedStripControl(
              color: ui_config["color"] != null
                  ? fromJsonColor(ui_config["color"])
                  : Color.fromARGB(0, 0, 0, 0),
              colors: ui_config["color_templates"] != null
                  ? (ui_config["color_templates"] as List)
                      .map((color) => fromJsonColor(color))
                      .toList()
                  : [
                      fromJsonColor({"r": 255, "g": 255, "b": 255}),
                    ],
              title: Text("All Led strips",
                  style: Theme.of(context).textTheme.bodyText1),
              ledStripParameters: null,
              ledStripPresets: [],
              showInMainUI: false,
              onColorChanged: (new_color) {
                // TODO only send a certain number of requests per second
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
            StrobeControl(
              color: ui_config["color"] != null
                  ? fromJsonColor(ui_config["color"])
                  : Color.fromARGB(0, 0, 0, 0),
              onColorChanged: (new_color) {
                // TODO only send a certain number of requests per second
                clientCommunication.send(
                    WebsocketActionId.STROBE_CONFIG_UPDATED,
                    {"color": toJsonColor(new_color)});
              },
              title: Text("Strobe all",
                  style: Theme.of(context).textTheme.bodyText1),
              strobeParameters: StrobeParameters(
                delayMs: 100,
                color: fromJsonColor({"r": 127, "g": 127, "b": 127}),
                onStrobeDelayChanged: (newDelay) => {},
                onStrobeColorChanged: (newColor) => {},
              ),
            ),
            Card(
              child: AllClientsControlList(
                  gpioClients: gpioClients,
                  ledStripClients: ledStripClients,
                  necLedStripClients: necLedStripClients,
                  uiConfig: this.ui_config),
            ),
            // TODO add smoke machine
          ]),
        ),
      ],
    );
  }
}
