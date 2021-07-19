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
