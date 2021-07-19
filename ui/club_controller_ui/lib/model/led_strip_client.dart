import 'package:json_annotation/json_annotation.dart';
import 'client.dart';
part 'led_strip_client.g.dart';

@JsonSerializable()
class LedStripClient extends Client {
  Map<String, int> color;
  List<Map<String, int>> color_templates;
  int effect_id;
  int fps;
  Map<String, int> frequency;
  int num_pixels;
  Map<String, double> filter;

  LedStripClient(
      {required uid,
      required name,
      required type_id,
      required is_connected,
      required this.color,
      required this.color_templates,
      required this.effect_id,
      required this.fps,
      required this.frequency,
      required this.num_pixels,
      required this.filter})
      : super(
            uid: uid, name: name, type_id: type_id, is_connected: is_connected);

  factory LedStripClient.fromJson(Map<String, dynamic> json) =>
      _$LedStripClientFromJson(json);
  Map<String, dynamic> toJson() => _$LedStripClientToJson(this);
}
