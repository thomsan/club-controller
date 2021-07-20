import 'package:club_controller_ui/communication/client_communication.dart';
import 'package:flutter/material.dart';
import '../model/led_strip_client.dart';
import '../color_helper.dart';

class StrobeParameters extends StatelessWidget {
  late double delayMs;
  late Color color;
  final Function(double) onStrobeDelayChanged;
  final Function(Color) onStrobeColorChanged;

  StrobeParameters(
      {Key? key,
      required this.delayMs,
      required this.color,
      required this.onStrobeDelayChanged,
      required this.onStrobeColorChanged})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5.0),
      child: Column(
        children: [
          Text("Delay (ms)"),
          Slider(
            value: delayMs,
            onChanged: onStrobeDelayChanged,
            label: delayMs.toString(),
            min: 10,
            max: 1000,
            divisions: 10,
          ),
        ],
      ),
    );
  }
}

class StrobeControl extends StatefulWidget {
  final Color color;
  final Function(Color) onColorChanged;
  final Widget title;
  final StrobeParameters strobeParameters;

  StrobeControl(
      {Key? key,
      required this.color,
      required this.onColorChanged,
      required this.title,
      required this.strobeParameters})
      : super(key: key);

  @override
  _StrobeControlState createState() => _StrobeControlState();
}

class _StrobeControlState extends State<StrobeControl> {
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
                  child: GestureDetector(
                    onTap: () {
                      showColorPicker(
                          context, widget.color, widget.onColorChanged);
                    },
                    /*onLongPress: () {
                      widget.colors.add(widget.color);
                      widget.onColorAdded(widget.colors);
                    },*/
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
                  flex: 2,
                  child: ElevatedButton(
                    child: Text("Strobe"),
                    onPressed: () => {
                      // TODO: Where to store if "Strobe all" is on and how to decide what to do for each client, when "Strobe all" is turned off?
                    },
                  ),
                ),
                widget.strobeParameters == null
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
            widget.strobeParameters == null
                ? Center()
                : AnimatedContainer(
                    duration: Duration(milliseconds: 200),
                    child: _showDetails
                        ? Column(
                            children: [
                              Text(
                                "Strobe parameters",
                                style: Theme.of(context).textTheme.headline5,
                              ),
                              widget.strobeParameters,
                            ],
                          )
                        : Center(),
                  ),
          ],
        ));
  }
}
