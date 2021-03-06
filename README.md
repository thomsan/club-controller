# Club control
[![BCH compliance](https://bettercodehub.com/edge/badge/thomsan/club-controller?branch=master)](https://bettercodehub.com/)

Raspberry Pi based controller to controller club components connected to ESP8266 controllers.

# Motivation
TODO

# Build Status
TODO

# Screenshots
TODO

# Features
TODO

# Clients
* NEC Led Strip
[Arduino client library - IRremoteESP8266](https://github.com/crankyoldgit/IRremoteESP8266)
[IR NEC codes](http://woodsgood.ca/projects/2015/02/13/rgb-led-strip-controllers-ir-codes/)[Alternative IR NEC codes](https://gist.github.com/Derpidoo/e3042055e0f5c3708f9b98b75fe4d59e)
[NEC Infrared Transmission Protocol](https://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol)

# Installation
TODO
1. For flashinbg client firmwares with Arudion IDE, copy wifi_settings_template.h to wifi_settings.h next to the *.ino file and update with your wifi credentials.

# How to use?
From the project root folder:
```
make run
```

# Tech/frameworks used
TODO
* [Club controller communication.txt](club_controller_communication.txt) can be viewed/modified with [sequencediagram.org](https://sequencediagram.org/)

# Contribute
TODO

# Credits
* Initial code base from [Scott Lawson's audio-reactive-led-strip](https://github.com/scottlawsonbc/audio-reactive-led-strip)
* Dockerized flutter web server based on [Jared Nelsen's example](https://github.com/jared-nelsen/flutter_web_docker_example)

# License
This project was developed by Thomas Ascioglu and is released under the MIT License.

MIT © Thomas Ascioglu
