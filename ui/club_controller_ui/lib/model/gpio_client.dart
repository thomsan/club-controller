import 'package:json_annotation/json_annotation.dart';
import 'client.dart';
part 'gpio_client.g.dart';

enum GPIOMode { DISABLED, INPUT, OUTPUT }

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
