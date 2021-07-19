import 'package:flutter/material.dart';
import 'package:club_controller_ui/model/gpio_client.dart';

class GPIOControl extends StatelessWidget {
  final Text title;
  final List<int> gpio_modes;
  final List<bool> gpio_values;
  Function(List<bool>) onValueChanged;

  GPIOControl(
      {Key? key,
      required this.title,
      required this.gpio_modes,
      required this.gpio_values,
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
              backgroundColor: ColorScheme.fromSwatch().primary,
            ),
          ),
          Expanded(
            flex: 2,
            child: title,
          ),
          Expanded(
            flex: 3,
            child: GpioButtons(
              gpio_modes: gpio_modes,
              gpio_values: gpio_values,
              onPressed: onValueChanged,
            ),
          ),
        ],
      ),
    );
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
