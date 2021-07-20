import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:flutter/material.dart';
import '../model/led_strip_client.dart';
import '../color_helper.dart';

class LedStripParameters extends StatelessWidget {
  final LedStripClient client;
  final Function onClientValueChanged;
  late RangeValues frequencyRange;

  LedStripParameters(
      {Key? key, required this.client, required this.onClientValueChanged})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    this.frequencyRange = RangeValues(client.frequency["min"]!.toDouble(),
        client.frequency["max"]!.toDouble());

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5.0),
      child: Column(
        children: [
          Text("Frequency range"),
          RangeSlider(
            values: frequencyRange,
            labels:
                RangeLabels('${frequencyRange.start}', '${frequencyRange.end}'),
            onChanged: (newRange) {
              client.frequency["min"] = newRange.start.toInt();
              client.frequency["max"] = newRange.end.toInt();
              if (client.frequency["min"]! == client.frequency["max"]!) {
                client.frequency["max"] = client.frequency["max"]! + 1;
              }
              onClientValueChanged();
            },
            min: 0,
            max: 12000,
            divisions: 100,
          ),
          Text("Edge blurring"),
          Slider(
              value: client.filter["edge_blurring"]!,
              min: 0.01,
              max: 10,
              label: '${client.filter["edge_blurring"]!}',
              onChanged: (newEdgeBlurring) {
                client.filter["edge_blurring"] = newEdgeBlurring;
                onClientValueChanged();
              }),
          Text("Rise"),
          Slider(
              value: client.filter["rise"]!,
              min: 0.001,
              max: 0.999,
              label: '${client.filter["rise"]!}',
              onChanged: (newEdgeBlurring) {
                client.filter["rise"] = newEdgeBlurring;
                onClientValueChanged();
              }),
          Text("Decay"),
          Slider(
              value: client.filter["decay"]!,
              min: 0.001,
              max: 0.999,
              label: '${client.filter["decay"]!}',
              onChanged: (newEdgeBlurring) {
                client.filter["decay"] = newEdgeBlurring;
                onClientValueChanged();
              })
        ],
      ),
    );
  }
}

class LedStripControl extends StatefulWidget {
  final Color color;
  final List<Color> colors;
  final Text title;
  final showInMainUI;
  final LedStripParameters? ledStripParameters;
  final List<dynamic> ledStripPresets;
  Function(Color) onColorChanged;
  Function(List<Color>) onColorAdded;
  Function(List<Color>) onColorRemoved;

  LedStripControl(
      {Key? key,
      required this.color,
      required this.colors,
      required this.title,
      required this.showInMainUI,
      this.ledStripParameters,
      required this.ledStripPresets,
      required this.onColorChanged,
      required this.onColorAdded,
      required this.onColorRemoved})
      : super(key: key);

  @override
  _LedStripControlState createState() => _LedStripControlState();
}

class _LedStripControlState extends State<LedStripControl> {
  TextEditingController _textFieldController = TextEditingController();
  bool _showDetails = false;
  String _textInput = "";

  Future<void> _displayPresetTitleInputDialog(BuildContext context) async {
    return showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: Text('Preset Title'),
            content: TextField(
              onChanged: (value) {
                setState(() {
                  _textInput = value;
                });
              },
              controller: _textFieldController,
              decoration: InputDecoration(hintText: "E.g. Bass"),
            ),
            actions: <Widget>[
              TextButton(
                child: Text('CANCEL'),
                onPressed: () {
                  setState(() {
                    Navigator.pop(context);
                  });
                },
              ),
              TextButton(
                child: Text('OK'),
                onPressed: () {
                  setState(() {
                    clientCommunication.send(
                        WebsocketActionId.SAVE_AS_LED_STRIP_PRESET, {
                      "client_uid": widget.ledStripParameters!.client.uid,
                      "title": _textInput
                    });
                    Navigator.pop(context);
                  });
                },
              ),
            ],
          );
        });
  }

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
                  child: GestureDetector(
                    onTap: () {
                      showColorPicker(
                          context, widget.color, widget.onColorChanged);
                    },
                    onLongPress: () {
                      widget.colors.add(widget.color);
                      widget.onColorAdded(widget.colors);
                    },
                    child: CircleAvatar(
                      backgroundColor: widget.color,
                    ),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: widget.title,
                ),
                Expanded(
                  flex: 4,
                  child: ColorTemplates(
                    colors: widget.colors,
                    onPressed: widget.onColorChanged,
                    onLongPressed: (color) {
                      widget.colors.remove(color);
                      widget.onColorRemoved(widget.colors);
                    },
                  ),
                ),
                widget.ledStripParameters == null
                    ? Center()
                    : IconButton(
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
            widget.ledStripParameters != null
                ? AnimatedContainer(
                    duration: Duration(milliseconds: 200),
                    child: _showDetails
                        ? Column(
                            children: [
                              Text(
                                "Led strip parameters",
                                style: Theme.of(context).textTheme.headline5,
                              ),
                              widget.ledStripParameters!,
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceEvenly,
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
                                                  "uid": widget
                                                      .ledStripParameters!
                                                      .client
                                                      .uid,
                                                  "show_in_main_ui":
                                                      newShowInMainUI
                                                })
                                          }),
                                ],
                              ),
                              Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceEvenly,
                                children: [
                                  ElevatedButton(
                                    child: Text("Save as preset"),
                                    onPressed: () =>
                                        _displayPresetTitleInputDialog(context),
                                  ),
                                  widget.ledStripPresets.isEmpty
                                      ? Center()
                                      : DropdownButton<Map<String, dynamic>>(
                                          value: null,
                                          hint: Text("Choose a preset"),
                                          onChanged: (Map<String, dynamic>?
                                              chosenPreset) {
                                            clientCommunication.send(
                                                WebsocketActionId.APPLY_PRESET,
                                                {
                                                  "uid": widget
                                                      .ledStripParameters!
                                                      .client
                                                      .uid,
                                                  "preset_uid":
                                                      chosenPreset!["uid"]
                                                });
                                          },
                                          items: widget.ledStripPresets
                                              .map<
                                                  DropdownMenuItem<
                                                      Map<String,
                                                          dynamic>>>((preset) =>
                                                  DropdownMenuItem<
                                                          Map<String, dynamic>>(
                                                      value: preset,
                                                      child: Text(
                                                        preset["title"],
                                                      )))
                                              .toList()),
                                ],
                              ),
                            ],
                          )
                        : Center(),
                  )
                : Center(),
          ],
        ));
  }
}
