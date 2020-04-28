from mycroft import MycroftSkill, intent_file_handler


class MyTasmotaDe(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('de.tasmota.my.intent')
    def handle_de_tasmota_my(self, message):
        self.speak_dialog('de.tasmota.my')


def create_skill():
    return MyTasmotaDe()

