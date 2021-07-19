// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'nec_led_strip_client.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

NecLedStripClient _$NecLedStripClientFromJson(Map<String, dynamic> json) {
  return NecLedStripClient(
    uid: json['uid'],
    name: json['name'],
    type_id: json['type_id'],
    is_connected: json['is_connected'],
    color: json['color'] as Map<String, dynamic>,
    color_templates: (json['color_templates'] as List<dynamic>)
        .map((e) => e as Map<String, dynamic>)
        .toList(),
    effect_id: json['effect_id'] as int,
    frequency: Map<String, int>.from(json['frequency'] as Map),
  );
}

Map<String, dynamic> _$NecLedStripClientToJson(NecLedStripClient instance) =>
    <String, dynamic>{
      'uid': instance.uid,
      'type_id': instance.type_id,
      'name': instance.name,
      'is_connected': instance.is_connected,
      'color': instance.color,
      'color_templates': instance.color_templates,
      'effect_id': instance.effect_id,
      'frequency': instance.frequency,
    };
