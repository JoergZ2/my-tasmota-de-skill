## Introduction
This Mycroft.ai skill is used to control IoT devices that are operated with the Tasmota firmware. Only MQTT (unencrypted, QoS 0) is considered as the communication protocol. The default syntax %prefix%/%topic%/ as well as %topic%/%prefix%/ (= setoption19/homeassistant mode) is available. The skill is currently especially designed for use in German and is case sensitive for topics. The following module must be installed: paho-mqtt.

## Configuration/setup
### MQTT Settings
* Enter IP of the MQTT broker
* Enter the port number of the MQTT broker (1883 is preset)

### Tasmota FullTopicSyntax
* Choice between the %prefix%/%topic%/ (default) or %topic%/%prefix%/ (Homeassstant or setoption19 type)

### Capitalization
* If the topics start with a capital letter, select this checkbox. ALL topics (= devices) with a leading uppercase letter are then generated. This also means that no other capital letter, e.g. TH10/TH16 or POW, may NOT occur.

More hints: Wiki (in german)

## Deutsche Version
Dieser Skill dient der Steuerung von IoT-Geräten, die mit der Firmware Tasmota betrieben werden. Als Kommunikationsprotokoll ist ausschließlich MQTT (unverschlüsselt, QoS 0) berücksichtigt. Zur Auswahl steht die default Syntax %prefix%/%topic%/ sowie %topic%/%prefix%/ (= setoption19/homeassistant Modus). Der Skill ist derzeit besonders auf die Nutzung in Deutsch ausgelegt und berücksichtigt die Groß- und Kleinschreibung von topics. Folgendes  Modul muss installiert werden: paho-mqtt.

## Configuration/Setup
### MQTT-Settings
* IP des MQTT-Brokers eingeben
* Portnummer des MQTT-Brokers eingeben (1883 ist vorbelegt)

### Tasmota FullTopicSyntax
* Auswahl zwischen dem Typ %prefix%/%topic%/ (vorbelegt) oder %topic%/%prefix%/ (Homeassstant bzw. setoption19 Typ)

### Capitalization
Falls die Topics mit einem Großbuchstaben anfangen, dann diese Checkbox wählen. Es werden dann ALLE Topics (= devices, = Geräte) mit einem führenden Großbuchstaben erzeugt. Das bedeutet gleichzeitig, dass kein weiterer Großbuchstabe z. B. wie TH10/TH16 oder POW NICHT vorkommen darf.

Dies bezieht sich allerdings auch auf die Schreibweise der auszuwertenden Sensordaten (Datei SensorKeywords.voc) 

Weitere Hinweise im Wiki

