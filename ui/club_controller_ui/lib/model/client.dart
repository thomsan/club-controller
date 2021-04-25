import 'package:json_annotation/json_annotation.dart';

part 'client.g.dart';

@JsonSerializable()
class Client {
  int uid;
  int type_id;
  String name;
  bool is_connected;

  Client(
      {required this.uid,
      required this.type_id,
      required this.name,
      required this.is_connected});

  factory Client.fromJson(Map<String, dynamic> json) => _$ClientFromJson(json);
  Map<String, dynamic> toJson() => _$ClientToJson(this);
}

@JsonSerializable()
class LedStripClient extends Client {
  Map<String, int> color;
  List<Map<String, int>> color_templates;
  int effect_id;
  int fps;
  Map<String, int> frequency;
  int num_pixels;
  num sigma;

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
      required this.sigma})
      : super(
            uid: uid, name: name, type_id: type_id, is_connected: is_connected);

  factory LedStripClient.fromJson(Map<String, dynamic> json) =>
      _$LedStripClientFromJson(json);
  Map<String, dynamic> toJson() => _$LedStripClientToJson(this);
}

@JsonSerializable()
class GpioClient extends Client {
  List<bool> gpios;

  GpioClient(
      {required uid,
      required name,
      required type_id,
      required is_connected,
      required this.gpios})
      : super(
            uid: uid, name: name, type_id: type_id, is_connected: is_connected);

  factory GpioClient.fromJson(Map<String, dynamic> json) =>
      _$GpioClientFromJson(json);
  Map<String, dynamic> toJson() => _$GpioClientToJson(this);
}
