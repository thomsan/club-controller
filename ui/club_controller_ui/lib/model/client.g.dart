// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'client.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Client _$ClientFromJson(Map<String, dynamic> json) {
  return Client(
    uid: json['uid'] as int,
    type_id: json['type_id'] as int,
    name: json['name'] as String,
    is_connected: json['is_connected'] as bool,
  );
}

Map<String, dynamic> _$ClientToJson(Client instance) => <String, dynamic>{
      'uid': instance.uid,
      'type_id': instance.type_id,
      'name': instance.name,
      'is_connected': instance.is_connected,
    };

LedStripClient _$LedStripClientFromJson(Map<String, dynamic> json) {
  return LedStripClient(
    uid: json['uid'],
    name: json['name'],
    type_id: json['type_id'],
    is_connected: json['is_connected'],
    color: Map<String, int>.from(json['color'] as Map),
    color_templates: (json['color_templates'] as List<dynamic>)
        .map((e) => Map<String, int>.from(e as Map))
        .toList(),
    effect_id: json['effect_id'] as int,
    fps: json['fps'] as int,
    frequency: Map<String, int>.from(json['frequency'] as Map),
    num_pixels: json['num_pixels'] as int,
    sigma: json['sigma'] as num,
  );
}

Map<String, dynamic> _$LedStripClientToJson(LedStripClient instance) =>
    <String, dynamic>{
      'uid': instance.uid,
      'type_id': instance.type_id,
      'name': instance.name,
      'is_connected': instance.is_connected,
      'color': instance.color,
      'color_templates': instance.color_templates,
      'effect_id': instance.effect_id,
      'fps': instance.fps,
      'frequency': instance.frequency,
      'num_pixels': instance.num_pixels,
      'sigma': instance.sigma,
    };

GpioClient _$GpioClientFromJson(Map<String, dynamic> json) {
  return GpioClient(
    uid: json['uid'],
    name: json['name'],
    type_id: json['type_id'],
    is_connected: json['is_connected'],
    gpios: (json['gpios'] as List<dynamic>).map((e) => e as bool).toList(),
  );
}

Map<String, dynamic> _$GpioClientToJson(GpioClient instance) =>
    <String, dynamic>{
      'uid': instance.uid,
      'type_id': instance.type_id,
      'name': instance.name,
      'is_connected': instance.is_connected,
      'gpios': instance.gpios,
    };
