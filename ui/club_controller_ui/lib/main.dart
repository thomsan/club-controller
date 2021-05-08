import 'package:flutter/material.dart';
import 'start_page.dart';

void main() {
  final title = 'Club Controller';
  runApp(MaterialApp(
    title: title,
    home: new StartPage(),
    theme: ThemeData(
      brightness: Brightness.light,
      primarySwatch: Colors.cyan,
    ),
    darkTheme:
        ThemeData(brightness: Brightness.dark, primarySwatch: Colors.cyan),
    themeMode: ThemeMode.dark,
  ));
}
