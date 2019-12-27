import json
import pandas as pd
import configparser


def answer_to_json(data):
    json_data = []
    for sentence in data['answer']:
        json_sentence = json.loads(sentence)
        json_data.append(json_sentence)
    return json_data


def count_type(json_data):
    types = []
    title = []
    for json_data_list in json_data:
        type = []
        try:
            title.append(json_data_list[0]['elements'][0]['text'])
        except KeyError:
            title.append('답변 드릴게요')
        for sentence in json_data_list:
            elements = sentence['elements']
            for element in elements:
                if element['type'] == 'buttons':
                    for depth_sentence in element['elements']:
                        type.append(depth_sentence['type'])
                else:
                    type.append(element['type'])
        types.append(type)
    return types, title


def set_voice(types, title):
    voice = []
    for i in range(len(types)):
        if types.count('carousel'):
            voice.append('옆으로 넘겨 읽어주세요')
        elif types[i].count('postback') > 1:
            voice.append('원하시는 버튼을 눌러주세요')
        elif types[i].count('web_url'):
            voice.append('버튼을 눌러 해당사이트로 이동해주세요')
        elif types[i].count('iframe'):
            voice.append('영상을 눌러 재생해주세요')
        else:
            if title[i] == '답변 드리겠습니다':
                voice.append(title[i])
            else:
                voice.append(title[i] + '입니다')
    return voice


def add_tts(json_data, voice):
    final_data = []
    for i in range(len(json_data)):
        elements = json_data[i][0]['elements']
        elements.append({'key': 'tts', 'value': voice[i], 'type': 'any'})
        final_data.append(json_data[i])
    return final_data


def main():
    c = configparser.ConfigParser()
    c.read('conf/add_tts.conf')
    input_dir = c.get('input', 'file_dir')
    output_dir = c.get('output', 'file_dir')
    file_name = c.get('input', 'file_name')

    data = pd.read_excel(input_dir + file_name)
    data_tts = pd.DataFrame({'answer': data['answer']})

    json_data = answer_to_json(data_tts)
    types, title = count_type(json_data)
    voice = set_voice(types, title)
    final_data = add_tts(json_data, voice)
    data['answer'] = final_data
    data['answer'] = data['answer'].apply(lambda x : json.dumps(x))
    data['mod_date'] = data['mod_date'].astype('str')
    data['reg_date'] = data['reg_date'].astype('str')
    data['answer'] = data['answer'].astype('str')
    data.to_excel(output_dir + file_name, index=None)


if __name__ == '__main__':
    main()
