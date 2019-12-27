import pandas as pd
import getConf
import messageAPI
import json
from datetime import datetime
import sys
import requests

def read_xlsx(file_name):

    data_path = getConf.getElement("input", "intent_file_dir") + file_name
    data = pd.read_excel(data_path)

    return data


def get_volume():

    volume_url = (getConf.getElement("api", "volume_url") + getConf.getElement("api", "volume_api") +
                  "?domain_id=" + getConf.getElement("api", "domain"))
    response = requests.get(volume_url)
    result = json.loads(response.content)

    data = pd.DataFrame(columns=["pkey", "intent", "entities", "category", "answer", "scenario", "keywords", "semantics", "question"])
    for element in result["result"]:
        data.loc[len(data)] = [element["pkey"], element["intent"], element["entities"], element["category"],
                               element["answer"], element["scenario"], element["keywords"], element["semantics"], element["question"]]

    return data


def cleaning_answer(answer):

    cleaned_answer = dict()
    if answer["answer"]:
        cleaned_answer["response"] = "O"
        cleaned_answer["score"] = answer["score"]
        cleaned_answer["entities"] = answer["answer"]["entities"]
        cleaned_answer["intent"] = answer["answer"]["intent"]
        cleaned_answer["scenario"] = answer["answer"]["scenario"]
        cleaned_answer["semantics"] = answer["answer"]["semantics"]
    else:
        cleaned_answer["response"] = "X"
        cleaned_answer["score"] = 0
        cleaned_answer["entities"] = ""
        cleaned_answer["intent"] = ""
        cleaned_answer["scenario"] = ""
        cleaned_answer["semantics"] = ""

    if answer["payloads"]:
        cleaned_answer["answer"] = json.dumps(answer["payloads"][0]["contents"], ensure_ascii=False)
    else:
        cleaned_answer["answer"] = ""

    return cleaned_answer


def isNaN(pkey):

    if pkey == pkey:
        return False
    return True


def intent_test(data):

    result_df = pd.DataFrame(columns=["pkey", "intent", "entities", "category", "answer", "scenario", "keywords", "semantics", "question",
                                      "result_intent", "result_entities", "result_answer",
                                      "result_scenario", "result_semantics", "score", "response", "correct"])

    question_index = 0
    count_respons_O = 0
    count_correct_O = 0
    original_entities_set = set()
    for i in range(len(data)):
        answer = messageAPI.analyze(data.loc[i]["question"])
        cleaned_answer = cleaning_answer(answer)

        if not isNaN(data.loc[i]["pkey"]):
            question_index = i
            result_df.loc[i, "pkey"] = data.loc[i]["pkey"]
            result_df.loc[i, "intent"] = data.loc[i]["intent"]
            result_df.loc[i, "entities"] = data.loc[i]["entities"]
            result_df.loc[i, "category"] = data.loc[i]["category"]
            result_df.loc[i, "answer"] = data.loc[i]["answer"]
            result_df.loc[i, "scenario"] = data.loc[i]["scenario"]
            result_df.loc[i, "keywords"] = data.loc[i]["keywords"]
            result_df.loc[i, "semantics"] = data.loc[i]["semantics"]
        result_df.loc[i, "question"] = data.loc[i]["question"]
        result_df.loc[i, "result_intent"] = cleaned_answer["intent"]
        result_df.loc[i, "result_entities"] = cleaned_answer["entities"]
        result_df.loc[i, "result_answer"] = cleaned_answer["answer"]
        result_df.loc[i, "result_scenario"] = cleaned_answer["scenario"]
        result_df.loc[i, "result_semantics"] = cleaned_answer["semantics"]
        result_df.loc[i, "score"] = cleaned_answer["score"]
        result_df.loc[i, "response"] = cleaned_answer["response"]
        if cleaned_answer["response"] == "O":
            count_respons_O += 1
        original_entities_set = set(str(data.loc[question_index]["entities"]).strip().split(" "))
        analyzed_entities_set = set(str(cleaned_answer["entities"]).strip().split(" "))
        if original_entities_set - analyzed_entities_set == set():
            result_df.loc[i, "correct"] = "O"
            count_correct_O += 1
        elif cleaned_answer["score"] > 55:
            result_df.loc[i, "correct"] = "O"
            count_correct_O += 1
        else:
            result_df.loc[i, "correct"] = "X"

    last_index = len(result_df)
    result_df.loc[last_index, "score"] = result_df["score"].mean()
    result_df.loc[last_index, "response"] = round(count_respons_O / (last_index) * 100, 2)
    result_df.loc[last_index, "correct"] = round(count_correct_O / (last_index) * 100, 2)
    result_df = result_df.fillna("")

    return result_df, count_respons_O, count_correct_O


def write_xlsx(result_df):

    now = datetime.now()
    fileName = (str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2) + "_" +
                str(now.hour).zfill(2) + str(now.minute).zfill(2) + str(now.second).zfill(2) + "_" +
                getConf.getElement("api", "domain") + "_intent_test.xlsx")

    result_df.to_excel(getConf.getElement("output", "output_file_dir") + fileName, index=False)

    return fileName


if __name__ == "__main__":
    option = sys.argv[1]
    check_file = False
    if option in ["-f", "--f", "-file", "--file"]:
        data = read_xlsx(getConf.getElement("input", "file_name"))
        check_file = True
    elif option in ["-v", "--v", "-volume", "---volume", "-V"]:
        data = get_volume()
    else:
        print("<option>")
        print("-f : test with specify file")
        print("-v : test with volume data")
    print()
    print("=================================================")
    print("URL : " + getConf.getElement("api", "url"))
    print("user : " + getConf.getElement("api", "user") + " / " + "domain : " + getConf.getElement("api", "domain"))
    if check_file:
        print("test_file : " + getConf.getElement("input", "file_name"))
    result_df, count_respons_O, count_correct_O = intent_test(data)
    print("count : " + str(len(result_df) - 1) + " / " + "response : " + str(count_respons_O) + " / " + "correct : " + str(count_correct_O))
    result_fileName = write_xlsx(result_df)
    print("=================================================")
    print(getConf.getElement("output", "output_file_dir") + result_fileName)
    print()
