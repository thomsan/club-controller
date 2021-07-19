import 'package:json_annotation/json_annotation.dart';
import 'client.dart';

part 'nec_led_strip_client.g.dart';

@JsonSerializable()
class NecLedStripClient extends Client {
  Map<String, dynamic> color;
  List<Map<String, dynamic>> color_templates;
  int effect_id;
  Map<String, int> frequency;

  NecLedStripClient(
      {required uid,
      required name,
      required type_id,
      required is_connected,
      required this.color,
      required this.color_templates,
      required this.effect_id,
      required this.frequency})
      : super(
            uid: uid, name: name, type_id: type_id, is_connected: is_connected);

  factory NecLedStripClient.fromJson(Map<String, dynamic> json) =>
      _$NecLedStripClientFromJson(json);
  Map<String, dynamic> toJson() => _$NecLedStripClientToJson(this);
}
