import requests
import json
import getConf

def analyze(question):

    data = {
        "domain": getConf.getElement("api", "domain"),
        "user": getConf.getElement("api", "user"),
        "text": question
    }
    chat_url = getConf.getElement("api", "url") + getConf.getElement("api", "api")
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    response = requests.post(chat_url, data=json.dumps(data), headers=headers)
    result = json.loads(response.content)

    return result