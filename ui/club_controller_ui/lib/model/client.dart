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
