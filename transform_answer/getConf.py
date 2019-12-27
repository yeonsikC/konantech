import configparser

config = configparser.ConfigParser()
config.read(r"C:\Users\구혜연\PycharmProjects\chatbot\transform_answer\conf\transform_answer.conf")

def getElement(section, name):

    element = config.get(section, name)

    return element
