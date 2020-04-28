# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/toggle-on.svg" card_color="#FFA500" width="50" height="50" style="vertical-align:bottom"/> My Tasmota De
The skill communicates with tasmota firmware on esp-8266 devices by mqtt especially in german.

## About
This skill is used to control iot devices that are operated with the tasmota firmware. only mqtt (unencrypted, qos 0) is considered as the communication protocol. the default syntax %prefix%/%topic%/ as well as %topic%/%prefix%/ (= setoption19/homeassistant mode) is available. the skill is currently especially designed for use in german and is case sensitive for topics. the following python module must be installed: paho-mqtt.

## Examples
* "Schalte die pumpe an!"
* "Wie sind die sensordaten vom außenthermometer?"
* "Welche zeitpläne sind am fernseher eingerichtet?"

## Credits
JoergZ2

## Category
**IoT**

## Tags
#Tasmota
#Mqtt
#Esp-8266

