import configparser

config = configparser.ConfigParser()
config.read(r"C:\Users\구혜연\PycharmProjects\chatbot\bulk_test\conf\intent_test.conf")

def getElement(section, name):

    element = config.get(section, name)

    return element