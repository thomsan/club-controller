import 'package:flutter/material.dart';
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
      child: Column(
        children: _buildColorTemplateList(),
      ),
    );
  }
}
