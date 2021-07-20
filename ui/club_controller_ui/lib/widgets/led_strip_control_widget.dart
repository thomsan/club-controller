import 'dart:math';

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
  final LedStripParameters? ledStripParameters;
  Function(Color) onColorChanged;
  Function(List<Color>) onColorAdded;
  Function(List<Color>) onColorRemoved;

  LedStripControl(
      {Key? key,
      required this.color,
      required this.colors,
      required this.title,
      this.ledStripParameters,
      required this.onColorChanged,
      required this.onColorAdded,
      required this.onColorRemoved})
      : super(key: key);

  @override
  _LedStripControlState createState() => _LedStripControlState();
}

class _LedStripControlState extends State<LedStripControl> {
  bool expanded = false;

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
                Expanded(
                  flex: 1,
                  child: IconButton(
                    onPressed: () => {
                      setState(() {
                        this.expanded = !this.expanded;
                      })
                    },
                    icon: expanded
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
                ),
              ],
            ),
            Builder(
              builder: (context) {
                return widget.ledStripParameters != null && this.expanded
                    ? widget.ledStripParameters!
                    : Center();
              },
            ),
          ],
        ));
  }
}
