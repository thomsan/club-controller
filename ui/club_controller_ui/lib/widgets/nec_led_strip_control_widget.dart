import 'package:flutter/material.dart';
import 'package:club_controller_ui/color_helper.dart';

class NecColorTemplates extends StatelessWidget {
  final List<Map<String, dynamic>> colors;
  final Function(Map<String, dynamic>)? onPressed;
  NecColorTemplates({Key? key, required this.colors, this.onPressed})
      : super(key: key);

  List<Widget> _buildColorTemplateList() {
    List<ElevatedButton> color_buttons =
        []; // this will hold Rows according to available lines
    for (var color in colors) {
      color_buttons.add(ElevatedButton(
        child: null,
        style: ElevatedButton.styleFrom(
          primary: fromJsonColor(color), // background
          onPrimary: Colors.white, // foreground
        ),
        onPressed: () {
          onPressed!(color);
        },
      ));
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

class NecLedStripControl extends StatelessWidget {
  final TextEditingController _commandController = TextEditingController();
  final Map<String, dynamic> color;
  final List<Map<String, dynamic>> colors;
  final Text title;
  Function(Map<String, dynamic>) onColorChanged;
  Function(String) onTextInput;
  Function() onAvatarTap;

  NecLedStripControl(
      {Key? key,
      required this.color,
      required this.colors,
      required this.title,
      required this.onAvatarTap,
      required this.onColorChanged,
      required this.onTextInput})
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
              onTap: onAvatarTap,
              child: CircleAvatar(
                backgroundColor: fromJsonColor(color),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: title,
          ),
          Expanded(
            flex: 3,
            child: NecColorTemplates(
              colors: colors,
              onPressed: onColorChanged,
            ),
          ),
          Expanded(
            flex: 3,
            child: Column(
              children: [
                Form(
                  child: TextFormField(
                    controller: _commandController,
                    decoration: InputDecoration(
                        labelText: 'Send NEC message (e.g. 0xFFD02F)'),
                  ),
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    primary: ColorScheme.fromSwatch().primary, // background
                    onPrimary: Colors.white, // foreground
                  ),
                  onPressed: () {
                    onTextInput(_commandController.text);
                  },
                  child: Text('Send'),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
