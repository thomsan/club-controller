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

@JsonSerializable()
class GpioClient extends Client {
  List<int> gpio_modes;
  List<bool> gpio_values;

  GpioClient(
      {required uid,
      required name,
      required type_id,
      required is_connected,
      required this.gpio_modes,
      required this.gpio_values})
      : super(
            uid: uid, name: name, type_id: type_id, is_connected: is_connected);

  factory GpioClient.fromJson(Map<String, dynamic> json) =>
      _$GpioClientFromJson(json);
  Map<String, dynamic> toJson() => _$GpioClientToJson(this);
}
