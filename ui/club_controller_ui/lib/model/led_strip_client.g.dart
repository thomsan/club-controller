// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'led_strip_client.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

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
    filter: Map<String, double>.from(json['filter'] as Map),
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
      'filter': instance.filter,
    };
