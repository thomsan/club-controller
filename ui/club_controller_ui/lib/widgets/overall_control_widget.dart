import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:flutter/material.dart';
import 'led_strip_control_widget.dart';
import '../color_helper.dart';

class OverallControl extends StatelessWidget {
  final Map<String, dynamic> ui_config;
  final ClientCommunication clientCommunication;

  OverallControl(
      {Key? key, required this.ui_config, required this.clientCommunication})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
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
          onColorChanged: (new_color) {
            // TODO only send a certain number of requests per second
            clientCommunication.send(WebsocketActionId.UI_CONFIG_UPDATED,
                {"color": toJsonColor(new_color)});
            clientCommunication.send(WebsocketActionId.ALL_LED_STRIPS_UPDATED,
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
        // TODO add smoke machine
      ]),
    );
  }
}
