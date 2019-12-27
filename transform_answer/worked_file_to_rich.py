
import getConf
import pandas as pd
import convert_to_rich_element as converter
from datetime import datetime
import json

ner_user = set()
ner_stop = set()


def read_file():
    file_path = getConf.getElement("input", "file_dir") + getConf.getElement("input", "file_name")
    qa_data = pd.read_excel(file_path)
    qa_data = qa_data.drop(["No", "worker", "date", "memo"], axis=1)
    qa_data = qa_data.fillna("")
    qa_data_obj = qa_data.select_dtypes(['object'])
    qa_data[qa_data_obj.columns] = qa_data_obj.apply(lambda x : x.str.strip())
    return qa_data


def sep_block(qa_data):
    block_list = list()
    index = 0
    while index < len(qa_data):
        block = {
            "category": qa_data.loc[index]["category"] + "#" + qa_data.loc[index]["team"],
            "question": qa_data.loc[index]["question"],
            "entity": qa_data.loc[index]["entity"],
            "stop": qa_data.loc[index]["stop"],
            "answer": {
                "non_card": {},
                "card": [],
                "scenario": {}
            }
        }
        card_check = False
        if qa_data.loc[index]["question"] != "":
            if qa_data.loc[index]["scenario"] == "scenario":
                block["answer"]["scenario"] = {
                    "scenario_name": qa_data.loc[index]["scenario_name"],
                    "scenario_action": qa_data.loc[index]["scenario_action"]
                }
            if qa_data.loc[index]["card"] == "":
                block["answer"]["non_card"] = {
                    "title": [qa_data.loc[index]["title"]] if qa_data.loc[index]["title"] != "" else [],
                    "sub_title": [qa_data.loc[index]["sub_title"]] if qa_data.loc[index]["sub_title"] != "" else [],
                    "image": [qa_data.loc[index]["image"]] if qa_data.loc[index]["image"] != "" else [],
                    "button_postback": [qa_data.loc[index]["button_postback"]] if qa_data.loc[index]["button_postback"] != "" else [],
                    "button_url": [qa_data.loc[index]["button_url"]] if qa_data.loc[index]["button_url"] != "" else [],
                    "text": [qa_data.loc[index]["text"]] if qa_data.loc[index]["text"] != "" else [],
                    "frame": [qa_data.loc[index]["frame"]] if qa_data.loc[index]["frame"] != "" else [],
                    "audio": [qa_data.loc[index]["audio"]] if qa_data.loc[index]["audio"] != "" else []
                }
            if qa_data.loc[index]["card"].strip() == "card":
                card_check = True
                block["answer"]["card"].append({
                    "title": [qa_data.loc[index]["title"]] if qa_data.loc[index]["title"] != "" else [],
                    "sub_title": [qa_data.loc[index]["sub_title"]] if qa_data.loc[index]["sub_title"] != "" else [],
                    "image": [qa_data.loc[index]["image"]] if qa_data.loc[index]["image"] != "" else [],
                    "button_postback": [qa_data.loc[index]["button_postback"]] if qa_data.loc[index]["button_postback"] != "" else [],
                    "button_url": [qa_data.loc[index]["button_url"]] if qa_data.loc[index]["button_url"] != "" else [],
                    "text": [qa_data.loc[index]["text"]] if qa_data.loc[index]["text"] != "" else [],
                    "frame": [qa_data.loc[index]["frame"]] if qa_data.loc[index]["frame"] != "" else [],
                    "audio": [qa_data.loc[index]["audio"]] if qa_data.loc[index]["audio"] != "" else []
                })
        plus_index = 1
        while index + plus_index < len(qa_data) and qa_data.loc[index + plus_index]["question"] == "":
            now_index = index + plus_index
            if qa_data.loc[now_index]["card"].strip() == "card":
                card_check = True
            if not card_check:
                if qa_data.loc[now_index]["title"] != "":
                    block["answer"]["non_card"]["title"].append(qa_data.loc[now_index]["title"])
                if qa_data.loc[now_index]["sub_title"] != "":
                    block["answer"]["non_card"]["sub_title"].append(qa_data.loc[now_index]["sub_title"])
                if qa_data.loc[now_index]["image"] != "":
                    block["answer"]["non_card"]["image"].append(qa_data.loc[now_index]["image"])
                if qa_data.loc[now_index]["button_postback"] != "":
                    block["answer"]["non_card"]["button_postback"].append(qa_data.loc[now_index]["button_postback"])
                if qa_data.loc[now_index]["button_url"] != "":
                    block["answer"]["non_card"]["button_url"].append(qa_data.loc[now_index]["button_url"])
                if qa_data.loc[now_index]["text"] != "":
                    block["answer"]["non_card"]["text"].append(qa_data.loc[now_index]["text"])
                if qa_data.loc[now_index]["frame"] != "":
                    block["answer"]["non_card"]["frame"].append(qa_data.loc[now_index]["audio"])
                if qa_data.loc[now_index]["audio"] != "":
                    block["answer"]["non_card"]["audio"].append(qa_data.loc[now_index]["audio"])
            elif card_check and qa_data.loc[now_index]["card"] == "":
                if qa_data.loc[now_index]["title"] != "":
                    block["answer"]["card"][-1]["title"].append(qa_data.loc[now_index]["title"])
                if qa_data.loc[now_index]["sub_title"] != "":
                    block["answer"]["card"][-1]["sub_title"].append(qa_data.loc[now_index]["sub_title"])
                if qa_data.loc[now_index]["image"] != "":
                    block["answer"]["card"][-1]["image"].append(qa_data.loc[now_index]["image"])
                if qa_data.loc[now_index]["button_postback"] != "":
                    block["answer"]["card"][-1]["button_postback"].append(qa_data.loc[now_index]["button_postback"])
                if qa_data.loc[now_index]["button_url"] != "":
                    block["answer"]["card"][-1]["button_url"].append(qa_data.loc[now_index]["button_url"])
                if qa_data.loc[now_index]["text"] != "":
                    block["answer"]["card"][-1]["text"].append(qa_data.loc[now_index]["text"])
                if qa_data.loc[now_index]["frame"] != "":
                    block["answer"]["card"][-1]["frame"].append(qa_data.loc[now_index]["audio"])
                if qa_data.loc[now_index]["audio"] != "":
                    block["answer"]["card"][-1]["audio"].append(qa_data.loc[now_index]["audio"])
            elif card_check and qa_data.loc[now_index]["card"] != "":
                block["answer"]["card"].append({
                    "title": [qa_data.loc[now_index]["title"]] if qa_data.loc[now_index]["title"] != "" else [],
                    "sub_title": [qa_data.loc[now_index]["sub_title"]] if qa_data.loc[now_index]["sub_title"] != "" else [],
                    "image": [qa_data.loc[now_index]["image"]] if qa_data.loc[now_index]["image"] != "" else [],
                    "button_postback": [qa_data.loc[now_index]["button_postback"]] if qa_data.loc[now_index]["button_postback"] != "" else [],
                    "button_url": [qa_data.loc[now_index]["button_url"]] if qa_data.loc[now_index]["button_url"] != "" else [],
                    "text": [qa_data.loc[now_index]["text"]] if qa_data.loc[now_index]["text"] != "" else [],
                    "frame": [qa_data.loc[now_index]["frame"]] if qa_data.loc[now_index]["frame"] != "" else [],
                    "audio": [qa_data.loc[now_index]["audio"]] if qa_data.loc[now_index]["audio"] != "" else []
                })
            plus_index += 1
        index += plus_index
        block_list.append(block)
    return block_list


def convert_each_answer(answer_elements_dict):
    element_list = list()
    max_index = max(len(answer_elements_dict["title"]),
                    len(answer_elements_dict["sub_title"]),
                    len(answer_elements_dict["image"]),
                    len(answer_elements_dict["text"]),
                    len(answer_elements_dict["frame"]),
                    len(answer_elements_dict["audio"]))
    for i in range(max_index):
        if i < len(answer_elements_dict["title"]):
            element_list.append(converter.convert_title(answer_elements_dict["title"][i]))
        if i < len(answer_elements_dict["sub_title"]):
            element_list.append(converter.convert_sub_title(answer_elements_dict["sub_title"][i]))
        if i < len(answer_elements_dict["text"]):
            element_list.append(converter.convert_text(answer_elements_dict["text"][i]))
        if i < len(answer_elements_dict["image"]):
            element_list.append(converter.convert_image(answer_elements_dict["image"][i]))
        if i < len(answer_elements_dict["frame"]):
            element_list.append(converter.convert_frame(answer_elements_dict["frame"][i]))
        if i < len(answer_elements_dict["audio"]):
            element_list.append(converter.convert_audio(answer_elements_dict["audio"][i]))
    if answer_elements_dict["button_postback"]:
        element_list.append(converter.convert_buttons(answer_elements_dict["button_postback"], "postback"))
    if answer_elements_dict["button_url"]:
        element_list.append(converter.convert_buttons(answer_elements_dict["button_url"], "url"))
    return element_list


def get_rich_json(block_list):
    global ner_user, ner_stop
    for block in block_list:
        if block["entity"] != "":
            ner_user = ner_user | set(block["entity"].split(" "))
        if block["stop"] != "":
            ner_stop = ner_stop | set(block["stop"].split(" "))
        transformed_answer = [{
            "elements": []
        }]
        if block["answer"]["non_card"]:
            transformed_answer[0]["elements"] = convert_each_answer(block["answer"]["non_card"])
        if block["answer"]["card"]:
            transformed_answer[0]["elements"].append({
                "contents": [],
                "type": "carousel"
            })
            temp_list = list()
            for each_card in block["answer"]["card"]:
                temp_dict = {
                    "elements": convert_each_answer(each_card)
                }
                temp_list.append(temp_dict)
            transformed_answer[0]["elements"][-1]["contents"] = temp_list
        if block["answer"]["scenario"]:
            transformed_answer = "scenario" + block["answer"]["scenario"]["scenario_name"] + "." + block["answer"]["scenario"]["scenario_action"]
        block["answer"] = transformed_answer
    return block_list


def write_intent_xlsx_and_ner(block_list):
    global ner_user, ner_stop
    now = datetime.now()
    present_date = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)
    present_time = str(now.hour).zfill(2) + str(now.minute).zfill(2) + str(now.second).zfill(2)
    result_df = pd.DataFrame(columns=["pkey", "intent", "entities", "category", "answer",
                                      "scenario", "keywords", "sementics", "question", "auth", "template", "date",
                                      "roles", "reg_user", "reg_date", "mod_user", "mod_date"])
    pkey = 1
    domain = getConf.getElement("trans", "domain")
    user = getConf.getElement("trans", "user")
    for block in block_list:
        temp_dict = {
            "pkey": domain + str(pkey).zfill(6),
            "intent": block["entity"].replace(" ", "/"),
            "entities": block["entity"],
            "category": block["category"],
            "answer": json.dumps(block["answer"], ensure_ascii=False),
            "scenario": "",
            "keywords": "",
            "semantics": "",
            "question": block["question"],
            "auth": "",
            "template": "generic" if "scenario" not in block["answer"] else "",
            "date": "",
            "roles": "",
            "reg_user": user,
            "reg_date": present_date + present_time,
            "mod_user": "",
            "mod_date": ""
        }
        result_df.loc[len(result_df)] = temp_dict
        pkey += 1
    output_base_name = getConf.getElement("output", "file_dir") + present_date + "_" + present_time + "_" + domain + "_"
    intent_file_name = output_base_name + "intent.xlsx"
    result_df.to_excel(intent_file_name, index=False)
    ner_file_name = output_base_name + "ner-user.txt"
    ner_file = open(ner_file_name, "w")
    for ner in list(ner_user):
        ner_file.write(ner + "\n")
    ner_file.close()
    ner_stop_name = output_base_name + "ner-stop.txt"
    ner_stop_file = open(ner_stop_name, "w")
    for stop in list(ner_stop):
        ner_stop_file.write(stop + "\n")
    ner_stop_file.close()
    return result_df, intent_file_name, ner_file_name, ner_stop_name


def worked_file_to_rich():
    print()
    print("===================================================")
    print()
    qa_data = read_file()
    block_list = get_rich_json(sep_block(qa_data))
    result_df, intent_file_name, ner_file_name, ner_stop_name = write_intent_xlsx_and_ner(block_list)
    print("결과 파일 생성 완료")
    print("intent : " + intent_file_name)
    print("ner-user : " + ner_file_name)
    print("ner_stop : " + ner_stop_name)
    print()
    print("===================================================")
    print()
    return result_df
