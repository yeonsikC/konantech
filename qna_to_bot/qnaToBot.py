import pandas as pd
import os
from collections import Counter
import morph
import configparser
import sys
sys.path.insert(0, "/home/konan-isdt/konanbot-util/source/transform_answer")
import worked_file_to_rich


def choice(data):
    '''
    데이터 중 category, team, question, entity, stop 변수만 선택하고, 좌우공백 제거.
    :param data: dataframe
    :return:  dataframe
    '''
    data_use_col = data[["category", "team", "question", "entity", "stop"]]
    data_use = data_use_col.dropna(axis=0, subset=('question',))
    data_use["category"] = data_use["category"].astype("str")
    data_use["category"] = data_use["category"].apply(lambda x: x.strip())
    data_use["team"] = data_use["team"].astype("str")
    data_use["team"] = data_use["team"].apply(lambda x: x.strip())
    data_use["question"] = data_use["question"].astype("str")
    data_use["question"] = data_use["question"].apply(lambda x: x.strip())
    data_use["entity"] = data_use["entity"].astype("str")
    data_use["entity"] = data_use["entity"].apply(lambda x: x.strip())
    data_use["stop"] = data_use["stop"].astype("str")
    data_use["stop"] = data_use["stop"].apply(lambda x: x.strip())
    return data_use


def category_team(data):
    '''
    cat = category#team
    c.f.) "#".join(category, team)
    :param data: dataframe
    :return: datafrmae
    '''
    # 1. 단어 사이에 _가 아닌 띄어쓰기를 했을 경우를 대비하여 띄어쓰기를 "_"로 변경
    data["category"] = data["category"].apply(lambda x: x.replace(" ", "_"))
    data["team"] = data["team"].apply(lambda x: x.replace(" ", "_"))
    # 2. cat이란 변수에 "category#team" 형태를 만듦
    cat = data[["category", "team"]].apply(lambda x: '#'.join(x), axis=1)
    return cat

def entity(data):
    '''
    entity를 단어별로 나열한 후, 중복 제거.
    여기서, 중복제거를 위해 영문을 모두 소문자로 변경.
    :param data: dataframe
    :return: 중복 없는 entity.txt4
    '''
    entities = data['entity'].apply(lambda x : x.split(' '))
    entity=[]
    for words in entities:
        for word in words:
            entity.append(word)
    entity = list(set(map(lambda x:x.lower(), entity)))[1:]
    entity = pd.DataFrame({"entity":entity[1:]})
    entity.to_csv(outputPath+"entity.txt", header=None, index=None)


def stopword(data):
    '''
    stopword를 결측치 처리 후, 단어별로 나열하고, 중복 제거.
    띄어쓰기가 아닌 ','로 된 경우, " "로 다 변환하였음.
    여기서, 중복제거를 위해 영문을 모두 소문자로 변경.
    :param data: dataframe
    :return: 중복 없는 stopword.txt
    '''
    stop = data["stop"]
    stop_use = stop.dropna()
    stop_use = stop_use.astype("str")
    stop_use = stop_use.apply(lambda x: x.replace(",", " "))
    stopwords = list(stop_use.apply(lambda x: x.split(" ")))
    stopword = []
    for words in stopwords:
        for word in words:
            stopword.append(word)
    stopword = list(set(map(lambda x: x.lower(), stopword)))
    lines = ''
    for word in stopword:
        lines += ' ' + word
    morph_words = morph.get_morphs(lines)
    morph_word = morph_words['morph_tag_tokens']
    final_stopword = []
    for word in morph_word.split(' '):
        a, b = word.split('/')
        if b[0] == 'N':
            if a!='nan':
                final_stopword.append(a)
    stopword_set = pd.DataFrame(final_stopword)
    stopword_set.to_csv(outputPath+"ner-stop.txt", header=None, index=None)


def set_word(entity):
    '''
    entity 복합명사를 구분하고 난 다음 중복 단어를 제거하는 함수
    :param data: dataframe
    :return: 중복 없는 dataframe.txt
    '''
    entitySet = pd.DataFrame(list(set(list(entity[0])))[1:])
    entitySet.to_csv(outputPath+"ner-user.txt",header=None, index=None)

def replace_question(data,syn):
    '''
    Qustion들의 동의어들을 모두 대표어로 바꾸어 줌.
    :param data: dataframe
    :param syn: dataframe
    :return: dataframe
    '''
    syn_dict = {}
    for line in syn[0]:
        words = line.split(',')
        for word in words[1:]:
            syn_dict[word] = words[0]
    newQuestions = []
    for question in data['question']:
        newQuestions.append(replace_all(question, syn_dict))
    data['question'] = newQuestions
    pd.DataFrame(data['question']).to_csv(outputPath+"question.csv", encoding="utf-16", index=None)
    data = data.reset_index()
    return data


def replace_all(text, dic):
    '''
    question에서 syn의 'key값(동의어)'을 'value값(대표어)'으로 모두 바꿈.
    :param text: str
    :param dic: dict
    :return: str
    '''
    for i, j in dic.items():
        text = text.replace(i.upper(), j)
        text = text.replace(i, j)
    return text


def final_data_set(data,question):
    '''
    최종적으로 코난봇에 넣을 데이터셋을 만드는 함수
    category#team question answer
    :param data: dataframe
    :param syn: syn - dataframe
    :return: dataframe, to_csv
    '''
    category_teams = list(category_team(data))
    answer_df = worked_file_to_rich.worked_file_to_rich()
    answer = answer_df['answer']
    finalDataSet = pd.DataFrame({"category" : category_teams,
                                 "question" : question['question'],
                                "answer" : answer})
    finalDataSet.to_csv(outputPath+"final_data_set.csv", encoding="utf-8", index=False, sep=",")
    return finalDataSet


def check_image(image_df):
    path_dir = "/home/konan-isdt/konanbot-data/attachments/images/"
    domain = input("도메인을 입력하세요. ex) SMU\n 입력 : ").strip().upper()
    my_image = os.listdir(path_dir)
    my_image.sort()
    my_images = []
    for i in range(len(my_image)):
        my_image[i] = my_image[i].upper()
        if my_image[i][:len(domain)]==domain:
            my_images.append(my_image[i])
    excel_image = image_df["image_df"]
    excel_image = excel_image.reset_index(drop=True)
    for i in range(len(excel_image)):
        excel_image[i] = domain+'_'+ excel_image[i]
        excel_image[i] = excel_image[i].upper()
    my_image_dic = Counter(my_images)
    excel_image_dic = Counter(excel_image)
    print("==================================================")
    print()
    print("디렉터리 내 이미지 개수 : {}".format(len(my_images)))
    print("엑셀 내 이미지 개수 : {}".format(len(excel_image)))
    print()
    if len(my_image_dic - excel_image_dic) == 0:
        print("나의 폴더에 있는 모든 이미지 파일이 엑셀에도 있습니다.")
    else:
        print("나의 폴더에는 있지만 엑셀에는 없는 이미지 : {}".format(my_image_dic - excel_image_dic))
    if len(excel_image_dic - my_image_dic) == 0:
        print("엑셀에 있는 모든 이미지 파일이 나의 폴더에도 있습니다.")
    else:
        print("엑셀에는 있지만 나의 폴더에는 없는 이미지 : {}".format(excel_image_dic - my_image_dic))
    print()
    print("==================================================")


def chatbot():
    pd.options.mode.chained_assignment = None  # 이유없는 경고문 제거
    global inputPath
    global outputPath
    inputPath = '/home/konan-isdt/konanbot-util/source/qna_to_bot/input/'
    outputPath = '/home/konan-isdt/konanbot-util/source/qna_to_bot/output/'
    menu = '''
    =============================================================================

    ※ 원하는 메뉴의 숫자를 입력 하세요.
    
    1. 데이터 전처리 작업.
        * 좌우공백제거, 필요변수 선택 
    2. entity 파일 생성.
        * entity.txt 생성 : 중복 없는 entity
    3. ner-stop 파일 생성
        * ner-stop.txt 생성 : 중복 없고 명사만 있는 ner-stop
        ※ 1 ~ 3번 메뉴를 모두 선택하셨으면,
           생성된 entity.txt파일 내에서 복합명사를 구분하고 4번을 진행하세요.
    4. 복합명사 처리한 entity 중복 제거.
        * 본인이 직접 복합명사 제거 후, 다시 중복 단어를 제거하여 ner-user.txt 생성.
        ※ 4번 메뉴를 하셨으면,
           생성된 ner-user.txt 파일을 통해 동의어사전(syn-user.txt)을 구축하세요.
    5. question에 있는 동의어들을 모두 대표어로 변환. (작업 후 검토필)
        * 본인이 직접 대표어와 동의어 처리 한 syn-user.txt 필요.
        ※ 생성된 question.csv 파일 내에서 대표어로 바뀐 동의어들에 대한 검토를 진행하세요.
    6.  이미지 파일 유무 확인.
        * 가지고 있는 파일들과 엑셀에 기입한 파일비교.
    7. category,question,answer 데이터 셋 구축.
        * 이전 작업들을 모두 진행한 후, 마지막에 진행.
    99. QnA 엑셀 파일 다시 불러오기
        * QnA.xlsx
    0. 종료.
    
    =============================================================================
    입력 : '''
    chk = 0
    select = 1
    while chk == 0:
        try:
            path_file = input("엑셀 파일명을 입력하세요. ex) SMU_QnA.xlsx\n입력 : ").strip().replace('\n', '')
            data = pd.read_excel(inputPath+path_file)
            image_df = pd.DataFrame({'image_df': data['image']})
            image_df = image_df.dropna(axis=0)
        except Exception as e:
            if path_file == '0':
                select = 0
                chk = 1
            print()
            print("※ 종료하려면 '0'을 입력하세요.")
            print("Error code : {}".format(e))
        else:
            chk=1
            c = configparser.ConfigParser()
            c.read("/home/konan-isdt/konanbot-util/source/transform_answer/conf/transform_answer.conf")
            file_name = path_file
            c.set('input', 'file_name', file_name)
            with open("/home/konan-isdt/konanbot-util/source/transform_answer/conf/transform_answer.conf", 'w') as configfile:
                c.write(configfile)
    while select != 0:
        select = int(input(menu))
        if select == 1:
            data = choice(data)
        elif select == 2:
            entity(data)
        elif select == 3:
            stopword(data)
        elif select == 4:
            entity2 = pd.read_csv(outputPath+'entity.txt', header=None)
            set_word(entity2)
        elif select == 5:
            syn = pd.read_csv(outputPath+"syn-user.txt", header=None, sep=" ")
            data = replace_question(data,syn)
        elif select == 6:
            check_image(image_df)
        elif select == 7:
            question = pd.read_csv(outputPath+"question.csv", encoding="utf-16")
            finalDataSet = final_data_set(data, question)
            print("================================")
            print()
            print("final_data_set.csv 생성 완료")
            print("의도 수 : {}".format(len(finalDataSet)))
            print()
            print("================================")
            print()
        elif select == 99:
            try:
                path_file = input("엑셀 파일명을 입력하세요. ex) SMU_QnA.xlsx\n입력 : ").strip().replace('\n', '')
                data = pd.read_excel(inputPath + path_file)
                image_df = pd.DataFrame({'image_df': data['image']})
                image_df = image_df.dropna(axis=0)
                c = configparser.ConfigParser()
                c.read("/home/konan-isdt/konanbot-util/source/transform_answer/conf/transform_answer.conf")
                file_name = path_file
                c.set('input', 'file_name', file_name)
                with open("/home/konan-isdt/konanbot-util/source/transform_answer/conf/transform_answer.conf", 'w') as configfile:
                    c.write(configfile)
            except Exception as e:
                print("Error code : {}".format(e))
        else:
            select = 0

    print("작업을 종료하겠습니다.")

chatbot()