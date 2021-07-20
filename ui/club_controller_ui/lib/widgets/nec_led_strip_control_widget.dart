import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:club_controller_ui/model/nec_led_strip_client.dart';
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

class NecLedStripControl extends StatefulWidget {
  final TextEditingController _commandController = TextEditingController();
  final Map<String, dynamic> color;
  final List<Map<String, dynamic>> colors;
  final Text title;
  final showInMainUI;
  final NecLedStripClient client;
  Function(Map<String, dynamic>) onColorChanged;
  Function(String) onTextInput;
  Function() onAvatarTap;

  NecLedStripControl(
      {Key? key,
      required this.color,
      required this.colors,
      required this.title,
      required this.showInMainUI,
      required this.client,
      required this.onAvatarTap,
      required this.onColorChanged,
      required this.onTextInput})
      : super(key: key);

  @override
  _NecLedStripControlState createState() => _NecLedStripControlState();
}

class _NecLedStripControlState extends State<NecLedStripControl> {
  bool _showDetails = false;

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
              onTap: widget.onAvatarTap,
              child: CircleAvatar(
                backgroundColor: fromJsonColor(widget.color),
              ),
            ),
          ),
          Expanded(
            flex: 2,
            child: widget.title,
          ),
          Expanded(
            flex: 3,
            child: NecColorTemplates(
              colors: widget.colors,
              onPressed: widget.onColorChanged,
            ),
          ),
          IconButton(
            onPressed: () => {
              setState(() {
                this._showDetails = !this._showDetails;
              })
            },
            icon: this._showDetails
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
          Expanded(
            flex: 3,
            child: Column(
              children: [
                Form(
                  child: TextFormField(
                    controller: widget._commandController,
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
                    widget.onTextInput(widget._commandController.text);
                  },
                  child: Text('Send'),
                ),
              ],
            ),
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
                                    WebsocketActionId.MAIN_UI_COMPONENT_UPDATED,
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
      ),
    );
  }
}
