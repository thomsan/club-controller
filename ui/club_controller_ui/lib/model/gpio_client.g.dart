// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'gpio_client.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

GpioClient _$GpioClientFromJson(Map<String, dynamic> json) {
  return GpioClient(
    uid: json['uid'],
    name: json['name'],
    type_id: json['type_id'],
    is_connected: json['is_connected'],
    gpio_modes:
        (json['gpio_modes'] as List<dynamic>).map((e) => e as int).toList(),
    gpio_values:
        (json['gpio_values'] as List<dynamic>).map((e) => e as bool).toList(),
  );
}

Map<String, dynamic> _$GpioClientToJson(GpioClient instance) =>
    <String, dynamic>{
      'uid': instance.uid,
      'type_id': instance.type_id,
      'name': instance.name,
      'is_connected': instance.is_connected,
      'gpio_modes': instance.gpio_modes,
      'gpio_values': instance.gpio_values,
    };
