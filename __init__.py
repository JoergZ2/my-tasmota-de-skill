import time
import json
from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
import paho.mqtt.client as mqtt
from mycroft.util import play_audio_file, resolve_resource_file
__author__ = 'aussieW (jamiehoward430) modified by JoergZ2'
#test
LOGGER = getLogger(__name__)
class MyTasmotaDe(MycroftSkill):

    def __init__(self):
        super(MyTasmotaDe, self).__init__(name="MyTasmotaDe")
        self.default_location = ""
        self.protocol = "mqtt"
        self.mqttssl = ""
        self.mqttca = ""
        self.mqtthost = ""
        self.mqttport = ""
        #self.mqttauth = self.config[""]
        #self.mqttuser = self.config[""]
        #self.mqttpass = self.config[""]

#        if (self.protocol == "mqtt"):
#            self.mqttc = mqtt.Client("MycroftAI")
#            if (self.mqttauth == "yes"):
#                self.mqttc.username_pw_set(self.mqttuser,self.mqttpass)
#            if (self.mqttssl == "yes"):
#                self.mqttc.tls_set(self.mqttca)
#            LOGGER.info("AJW - connect to: " + self.mqtthost)
#            LOGGER.info("AJW - connect to: " + str(self.mqttport))
#            self.mqttc.connect(self.mqtthost,self.mqttport,10)
#            self.mqttc.on_message = self.on_message
#            self.mqttc.subscribe(dataRequestTopic)
#            self.mqttc.loop_start()


    def initialize(self):
        '''
        Reads the preferences from settings.json which is written by
        the skill interface on home.mycroft.ai
        '''
        self.load_data_files(dirname(__file__))
        self. __build_automation_command()
        self. __build_control_command()
        self. __build_dataRequest_command()
        self.mqtthost = self.settings.get('mqttbroker')
        self.mqttport = self.settings.get('mqttport')
        self.fulltopicsyntax = self.settings.get('fulltopicsyntax')
        self.capitalization = self.settings.get('capitalization')
        if self.capitalization == True:
            self.capitalization = "yes"
        '''
        Under certain conditions the standard topic structure of tasmota is
        changed. the default is %prefix%/%topic%/. But you can change it to
        %topic%/%prefix%/ with the command setoption19 1.
        The advantage of the latter syntax is that you can easily identify
        your devices. This skill can control both topic structures if
        the appropriate selection has been made in the skill setup.
        '''
        if self.fulltopicsyntax == "default":
            self.actionConfirmationTopic = "stat/+/#"
            self.prefix = "cmnd/"
        if self.fulltopicsyntax == "homeassistant":
            self.actionConfirmationTopic = "+/stat/#"
            self.prefix = "/cmnd"

    def translate_to_german_number_syntax(self, val1 = None, val2 = None, val3 = None, val4 = None, val5 = None, watt = None):
        '''
        Script wide function: 
        For german speaking users dots in numbers are changed to commas.
        The function is used in the on_message section.
        '''
        self.val1 = str(val1); self.val1 = self.val1.replace('.',',')
        self.val2 = str(val2); self.val2 = self.val2.replace('.',',')
        self.val3 = str(val3); self.val3 = self.val3.replace('.',',')
        self.val4 = str(val4); self.val4 = self.val4.replace('.',',')
        self.val5 = str(val5); self.val5 = self.val5.replace('.',',')
        self.watt = str(watt); self.watt = self.watt.replace('.',',')
        return [self.val1, self.val2, self.val3,self.val4,val5, self.watt]



    def __build_automation_command(self):
        '''
        The __build functions are defining which keywords from the intent files
        are required or optionally. It uses the *.voc files from language directories.
        By determining which keywords are required and which are optional,
        the behavior of the skill can be well controlled.
        The main task of this function is switching or turning devices ON and OFF.
        '''
        # example: "Schalte die Pumpe an!" | "Turn on the pump!" 
        intent = IntentBuilder("automation_Intent")\
	.require("CommandKeyword")\
	.require("ModuleKeyword")\
	.require("ActionKeyword")\
	.optionally("LocationKeyword")\
	.build()
        self.register_intent(intent, self.handle_automation_command)

    def __build_control_command(self):
        '''
        The future main task of this function is to manage devices or services
        for example to make the lights brighter or to change the color or to manage
        a mediacenter (louder, softer).
        '''
        #not used yet
        intent = IntentBuilder("control_Intent")\
        .require("ModuleKeyword")\
        .require("AttributeKeyword")\
        .require("ValueKeyword")\
        .optionally("LocationKeyword")\
        .build()
        self.register_intent(intent, self.handle_control_command)

    def __build_dataRequest_command(self):
        '''
        The main task og this function is to return sensor values from sensors
        connected to Tasmota flashed devices (temperatur, humidity, pressure, current ...)
        '''
	# example: "Wie ist die Temperatur am Außenfühler?" | ""what's the temperature on the deck"
        intent = IntentBuilder("dataRequest_Intent")\
        .require("RequestKeyword")\
        .require("SensorKeyword")\
        .require("ModuleKeyword")\
        .optionally("LocationKeyword")\
        .build()
        self.register_intent(intent, self.handle_dataRequest_command)

    def handle_automation_command(self, message):
        '''
        The handle_ ... functions include the commands which are when an
        appropriate combination of required and optional keywords have been
        specified.
        Currently the power setting is hard coded. Adaptations are imaginable
        '''
        #Beispiel "Schalte den|die|das <MQTT-Name des Gerätes> an"
        command = "/POWER"
        #LOGGER.info('AJW: mqtt automation command')
        cmd_name = message.data.get("CommandKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ', '_')
        if mdl_name == "werkstatt_radio":
            mdl_name = "werkstattradio"
        act_name = message.data.get("ActionKeyword")
        loc_name = message.data.get("LocationKeyword")
        if loc_name:
           loc_name = loc_name.replace(' ', '_')
        else:
           loc_name = self.default_location
        if act_name:
            cmd_name = '/POWER'
            act_name = act_name.replace('an','ON').replace('aus','OFF')

        if (self.protocol == "mqtt"):
            self.mqttc = mqtt.Client("MycroftAI")
            #if (self.mqttauth == "yes"):
            #    mqttc.username_pw_set(self.mqttuser,self.mqttpass)
            #if (self.mqttssl == "yes"):
            #    mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - Module automation_command connect to: " + str(self.mqttport))
            play_audio_file(resolve_resource_file("/home/pi/mycroft-core/mycroft/res/snd/verstanden.mp3"))
            #self.speak_dialog('verstanden')
            time.sleep(1.0)
            self.mqttc.connect(self.mqtthost, self.mqttport, keepalive=10)
            self.mqttc.on_message = self.on_message
            self.mqttc.loop_start()
            self.mqttc.subscribe(self.actionConfirmationTopic)
            #LOGGER.info("AJW - connected - about to execute" + "- " + mdl_name + cmd_name)
            if self.fulltopicsyntax == "default":
                if self.capitalization == "yes":
                    mdl_name = mdl_name.capitalize()
                self.mqttc.publish(self.prefix + mdl_name + command, act_name)
            if self.fulltopicsyntax == "homeassistant":
                if self.capitalization == "yes":
                    mdl_name = mdl_name.capitalize()
                self.mqttc.publish(mdl_name + self.prefix + command, act_name)
            LOGGER.info("AJW - Published: " + mdl_name + cmd_name, act_name)
	    #allow time for the action to be performed and a confirmation to be returned
            time.sleep(1)
            self.mqttc.disconnect()

        else:
            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

    def handle_control_command(self, message):
        '''
        These commands are to change settings. It will not be about switching
        on and off, but about values for brightness, volume, station selection,
        sound etc.
        Not used yet.
        '''
        att_name = message.data.get("AttributeKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ', '_')
        val_name = message.data.get("ValueKeyword")
        loc_name = message.data.get("LocationKeyword")
        service_name = message.data.get("ServiceKeyword")

        if loc_name:
            loc_name = loc_name.replace(' ', '_')
        else:
            loc_name = self.default_location

        LOGGER.info('AJW: att: ' + att_name + '; mdl: ' + mdl_name + '; val: ' + val_name + '; loc: ' + loc_name)

#        if act_name:
#            cmd_name += '_' + act_name

        if (self.protocol == "mqtt"):
            mqttc = mqtt.Client("MycroftAI")
            if (self.mqttssl == "yes"):
                mqttc.tls_set(self.mqttca)
            LOGGER.info("AJW - connect to: " + self.mqtthost)
            LOGGER.info("AJW - connect to: " + str(self.mqttport))
            mqttc.connect(self.mqtthost,self.mqttport,keepalive=10)
#            LOGGER.info("AJW - connected - about to execute" + "-" + cmd_name)
            if self.capitalization == "yes":
                mdl_name = mdl_name.capitalize()
            mqttc.publish(mdl_name + "/" + "cmnd/POWER", act_name)
#           mqttc.publish("/mediaCenter/" + loc_name + "/" + mdl_name, act_name)
            #LOGGER.info("Funk control command AJW - Published: " + loc_name + "/" + mdl_name + ", " + act_name)
            mqttc.disconnect()
            self.speak_dialog("cmd.sent")
#            LOGGER.info(mdl_name + "-" + cmd_name)

        else:
            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})

            LOGGER.error("Error: {0}".format(e))

    def handle_dataRequest_command(self, message):
        '''
        This function is used to call up the measured values of the sensors.
        The function works together with the on_message function. Tasmota knows
        13 different status queries so far:
        status (without any digit): a summary of important parameters,
        status0: playback of all status reports 1-11,
        status1 to status11: selected single reports e.g. about network settings,
        sensors or firmware version. Look at the Tasmota documentation for detail.
        Further down (search for "if sen_name == "), the corresponding keywords are 
        used to filter which status information is retrieved.
        The following on_message function also filters which values should be
        announced.
        '''
        req_name = message.data.get("RequestKeyword")
        sen_name = message.data.get("SensorKeyword")
        loc_name = message.data.get("LocationKeyword")
        mdl_name = message.data.get("ModuleKeyword")
        mdl_name = mdl_name.replace(' ','_')
        if mdl_name == "werkstatt_radio":
            mdl_name = "werkstattradio"
        if mdl_name == "messpunkt_1" or mdl_name == "stromzähler_1":
            mdl_name = "Messpunkt_1"
        if mdl_name == "stromzähler 2":
            mdl_name = "stromzähler_2"
        if mdl_name == "außenthermometer" or mdl_name == "aussenthermometer" or mdl_name == "schuppen" or mdl_name == "durchgang":
            mdl_name = "TH10"
        if self.capitalization == "yes":
            mdl_name = mdl_name.capitalize()
            if mdl_name == "Th10":
                mdl_name = "TH10"
            sen_name = sen_name.capitalize()
        prefix = "cmnd/"
        topic = mdl_name + "/"
        if self.fulltopicsyntax == "default":
            dataRequestTopic = prefix + topic
        if self.fulltopicsyntax == "homeassistant":
            dataRequestTopic = topic + prefix
        if (self.protocol == "mqtt"):
            self.mqttc = mqtt.Client("MycroftAI")
            #if (self.mqttauth == "yes"):
                #self.mqttc.username_pw_set(self.mqttuser,self.mqttpass)
            #if (self.mqttssl == "yes"):
                #self.mqttc.tls_set(self.mqttca)
            LOGGER.info("Funk Request AJW - connect to: " + str(self.mqtthost))
            #LOGGER.info("AJW - connect to: " + str(self.mqttport))
            play_audio_file(resolve_resource_file("/home/pi/mycroft-core/mycroft/res/snd/verstanden.mp3"))
            #self.speak_dialog('verstanden')
            time.sleep(1)
            self.mqttc.connect(self.mqtthost,self.mqttport)
            self.mqttc.on_message = self.on_message
            self.mqttc.loop_start()
            if sen_name == "Schaltzustand" or sen_name == "Zustand":
                command = "STATUS"
                dataRequestTopic = dataRequestTopic + command
                payload = 11
            if sen_name == "Sensordaten" or sen_name == "Messdaten":
                command = "STATUS"
                dataRequestTopic = dataRequestTopic + command
                payload = 10
            if sen_name == "Zeitplan" or sen_name == "Zeitpläne":
                command = "timers"
                payload = ""
                dataRequestTopic = dataRequestTopic + command

            #self.mqttc.subscribe(str(dataRequestTopic)+"/#")
            if self.fulltopicsyntax == "default":
                #self.mqttc.subscribe(result + mdl_name + '/#')
                self.mqttc.subscribe(self.actionConfirmationTopic)
            if self.fulltopicsyntax == "homeassistant":
                #self.mqttc.subscribe(mdl_name + result + '/#')
                self.mqttc.subscribe(self.actionConfirmationTopic)
            self.mqttc.publish(dataRequestTopic, payload)
            LOGGER.info("AJW - Published: "+ dataRequestTopic + " " + str(payload))
            #self.payload = json.loads(msg.payload.decode())
            time.sleep(1)
            self.mqttc.disconnect()
        else:
            self.speak_dialog("not.found", {"command": cmd_name, "action": act_name, "module": dev_name})
            LOGGER.error("Error: {0}".format(e))

        
    def stop(self):
        pass

    def on_message(self, mqttClient, userdata, msg):
        '''
        This function evaluates the JSON formatted output of the devices.
        If power has changed the device sends an JSON statement like {"POWER":"OFF"}.
        Each of the 11 Tasmota status messages has a unique keyword e.g.
        "StatusSNS" (for sensor values). With the following if ... elif structure, 
        the results are intercepted and appropriate response texts are output.
        Because this skill is specially programmed for the German language,
        the answers are in German. Alternatively, you can write the possible
        answers in dialog files and mix them with the variables with the
        measured values.
        '''
        LOGGER.info('AJW: Topicmytasmotade = ' + msg.topic)
        splitTopic = msg.topic.split('/')
        if self.fulltopicsyntax == "default":
            device_name = splitTopic[1]
        if self.fulltopicsyntax == "homeassistant":
            device_name = splitTopic[0]
        #LOGGER.info('SplitTopic ist: ' + splitTopic[0])
        values = str(msg.payload.decode())
        values_dict = json.loads(values)
        #LOGGER.info(values_dict)

        '''if "Timers" in values_dict or "Timers1" in values_dict or \
        "Timers2" in values_dict or  "Timers3" in values_dict or \
        "Timers4" in values_dict:
            try:
                with open("/var/log/mycroft/timer.log", "a") as tl:
                    tl.write(str(values_dict) + "\n")
                answer = self.timer_request_answer()
                self.speak(answer)
            except Exception as e:
                LOGGER.info('Error:  {0}'.format(e))
                pass'''
        if "Timers" in values_dict:
            if values_dict['Timers'] == "ON":
                self.speak_dialog('timers')
                del values_dict['Timers']
                counter = 1
                for key in values_dict:
                    #print(result_dict[key])
                    if values_dict[key]['Enable'] == 0:
                        continue
                    if values_dict[key]['Enable'] == 1:
                        #self.speak("Timer 1")
                        counter_word = str(counter)
                        moment = values_dict[key]['Time']
                        moment = moment.replace(":"," Uhr ")
                        action = values_dict[key]['Action']
                        if action == 1:
                            action = "einschalten"
                        else:
                            action = "aussschalten"
                        days = values_dict[key]['Days']
                        if days == "1111111":
                            days = "täglich"
                        elif days == "1000001":
                            days = "am wochenende"
                        elif days == "0111110":
                            days = "montags bis freitags"
                        else:
                            days = "an verschiedenen Tagen"
                        answer = "Timer " + counter_word + ", Uhrzeit: " + moment + ". Aktion: " + action + ", Tage: " + days + "."
                    self.speak(answer)
                    #time.sleep(2)
                    counter += 1
            if values_dict['Timers'] == "OFF":
                self.speak_dialog('notimers')

        if "StatusSNS" in values_dict and "ENERGY" in values_dict['StatusSNS']:
            '''
            StatusSNS includes both weather sensors and electrical measured values.
            Therefore a more complex query via two parameters is required.
            '''
            value_ttl = values_dict['StatusSNS']['ENERGY']['Total']
            value_ytdy = values_dict['StatusSNS']['ENERGY']['Yesterday']
            value_tdy = values_dict['StatusSNS']['ENERGY']['Today']
            value_vtg = values_dict['StatusSNS']['ENERGY']['Voltage']
            value_crt = values_dict['StatusSNS']['ENERGY']['Current']
            value_fct = values_dict['StatusSNS']['ENERGY']['Factor']
            watt = value_vtg * value_crt * value_fct; watt = round(watt,2)
            trlt = self.translate_to_german_number_syntax(\
            values_dict['StatusSNS']['ENERGY']['Voltage'],\
            values_dict['StatusSNS']['ENERGY']['Current'], \
            watt, \
            values_dict['StatusSNS']['ENERGY']['Today'], \
            values_dict['StatusSNS']['ENERGY']['Yesterday'], \
            values_dict['StatusSNS']['ENERGY']['Total'])
            trlt[4] = str(trlt[4])
            trlt[4] = trlt[4].replace('.',',')
            answer = "Die Spannung ist " + str(trlt[0]) + " Volt, " + \
                     "der aktuelle Strom " + str(trlt[1]) + " Ampere. " + \
                     "Der Verbrauch liegt jetzt bei " + str(trlt[2]) + " Watt. " +\
                     "Heute wurden " + str(trlt[3]) + \
                     " Kilowattstunden verbraucht, gestern  " + str(trlt[4]) + \
                     " und insgesamt " + str(trlt[5]) + " Kilowattstunden."
        elif "StatusSNS" in values_dict:
            '''If there a different meteorological sensors you have to build
             an if statement for each of them.'''
            if "SI7021" in values_dict['StatusSNS']:
                value_temp = values_dict['StatusSNS']['SI7021']['Temperature']
                value_hum = values_dict['StatusSNS']['SI7021']['Humidity']
                value_temp = str(value_temp).replace('.',',')
                value_hum = str(value_hum).replace('.',',')
                answer = "Die Temperatur ist " + value_temp + " Grad und die Luftfeuchtigkeit ist " + value_hum + " Prozent."
            if "DHT11" in values_dict['StatusSNS']:
                value_temp = values_dict['StatusSNS']['DHT11']['Temperature']
                value_hum = values_dict['StatusSNS']['DHT11']['Humidity']
                value_temp = str(value_temp).replace('.',',')
                value_hum = str(value_hum).replace('.',',')
                answer = "Die Temperatur ist " + value_temp + " Grad und die Luftfeuchtigkeit ist " + value_hum + " Prozent."
        elif "StatusSTS" in values_dict:
            value_power = values_dict['StatusSTS']['POWER']
            value_power = value_power.replace('ON','an').replace('OFF','aus')
            answer = "Der Schaltzustand ist " + value_power + "."
            #self.speak_dialog('aus')
            #LOGGER.info("Antwort: " + answer)
        elif "POWER" in values_dict:
            #LOGGER.info("Power empfangen")
            value_power = values_dict['POWER']
            value_power = value_power.replace('ON','an').replace('OFF','aus')
            answer = device_name + " ist " + value_power + "geschaltet."
            #self.speak_dialogue('an')

        else:
            LOGGER.info('AJW: Received a message' + values_dict)
            return
       # if msg.topic == actionConfirmationTopic:
        if msg.topic != '':
            if msg.payload != '':
                LOGGER.info('AJW: Requested action was successful')
                #LOGGER.info("Sprechtext: " + answer)
                self.speak(answer)
                #self.speak_dialog('action.successful')
            else:
                LOGGER.info('AJW: Requested action was unsuccessful')
                self.speak_dialog('action.unsuccessful')
            return

def create_skill():
#    myskill = MyTasmotaDe()
#    return myskill
    return MyTasmotaDe()

