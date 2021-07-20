import 'package:flutter/material.dart';
import 'package:club_controller_ui/model/gpio_client.dart';
import 'package:club_controller_ui/communication/client_communication.dart';

class GPIOControl extends StatefulWidget {
  final Text title;
  final showInMainUI;
  final GpioClient client;
  final List<int> gpio_modes;
  final List<bool> gpio_values;
  Function(List<bool>) onValueChanged;

  GPIOControl(
      {Key? key,
      required this.title,
      required this.showInMainUI,
      required this.client,
      required this.gpio_modes,
      required this.gpio_values,
      required this.onValueChanged})
      : super(key: key);

  @override
  _GPIOControlState createState() => _GPIOControlState();
}

class _GPIOControlState extends State<GPIOControl> {
  bool _showDetails = false;

  @override
  Widget build(BuildContext context) {
    return Padding(
        padding: const EdgeInsets.symmetric(vertical: 5.0),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Expanded(
                  flex: 1,
                  child: CircleAvatar(
                    backgroundColor: ColorScheme.fromSwatch().primary,
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: widget.title,
                ),
                Expanded(
                  flex: 3,
                  child: GpioButtons(
                    gpio_modes: widget.gpio_modes,
                    gpio_values: widget.gpio_values,
                    onPressed: widget.onValueChanged,
                  ),
                ),
                IconButton(
                  onPressed: () => {
                    setState(() {
                      this._showDetails = !this._showDetails;
                    })
                  },
                  icon: _showDetails
                      ? Icon(
                          Icons.expand_less,
                          size: 24.0,
                          semanticLabel: 'Collapse',
                        )
                      : Icon(
                          Icons.expand_more,
                          size: 24.0,
                          semanticLabel: 'Expand',
                        ),
                ),
              ],
            ),
            AnimatedContainer(
              duration: Duration(milliseconds: 200),
              child: _showDetails
                  ? Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        Text(
                          "Show in main menu",
                          textAlign: TextAlign.center,
                        ),
                        Checkbox(
                            value: widget.showInMainUI,
                            onChanged: (newShowInMainUI) => {
                                  clientCommunication.send(
                                      WebsocketActionId
                                          .MAIN_UI_COMPONENT_UPDATED,
                                      {
                                        "uid": widget.client.uid,
                                        "show_in_main_ui": newShowInMainUI
                                      })
                                }),
                      ],
                    )
                  : Center(),
            )
          ],
        ));
  }
}

class GpioButtons extends StatelessWidget {
  final List<int> gpio_modes;
  final List<bool> gpio_values;
  final Function(List<bool>)? onPressed;

  GpioButtons(
      {Key? key,
      required this.gpio_modes,
      required this.gpio_values,
      this.onPressed})
      : super(key: key);

  List<Widget> _buildGpioButtonList() {
    List<ElevatedButton> gpio_buttons =
        []; // this will hold Rows according to available lines
    gpio_modes.asMap().forEach((index, mode) {
      if (mode == GPIOMode.OUTPUT.index) {
        gpio_buttons.add(ElevatedButton(
          child: null,
          style: ElevatedButton.styleFrom(
            primary: gpio_values[index]
                ? ColorScheme.fromSwatch().primary
                : Colors.black54, // background
            onPrimary: Colors.white, // foreground
          ),
          onPressed: () {
            gpio_values[index] = !gpio_values[index];
            onPressed!(gpio_values);
          },
        ));
      }
    });
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
