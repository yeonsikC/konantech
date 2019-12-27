import requests
import json

def get_morphs(line):
    results = dict()

    params = {
        'mod': 'kma',
        'text': line,
        'format': 'json',
        'charset': 'utf8',
        'language': 'korean',
        'option': ''
    }

    kana_url = "http://10.10.18.186:7578/ksm/kana/analyze"
    response = requests.get(kana_url, params=params)

    result = json.loads(response.content)

    tokens = ""
    morph_tag_tokens = ""
    sharp_tag_tokens = ""

    for sent in result["sents"]:
        for word in sent["words"]:
            for lemma in word["nbest"][0]["lemmas"]:
                if len(tokens) > 0:
                    tokens += " "
                tokens += lemma["string"]

                if len(morph_tag_tokens) > 0:
                    morph_tag_tokens += " "

                morph_tag_token = lemma["string"] + "/" + lemma["tag2"]
                morph_tag_tokens += morph_tag_token

                if len(sharp_tag_tokens) > 0:
                    sharp_tag_tokens += " "

                sharp_tag_token = lemma["string"] + "#S"
                sharp_tag_tokens += sharp_tag_token

    results["tokens"] = tokens
    results["morph_tag_tokens"] = morph_tag_tokens
    results["sharp_tag_tokens"] = sharp_tag_tokens

    return results

def get_pattern(line):
    results = dict()

    params = {
        'text': line,
        'format': 'json',
        'charset': 'utf8',
        'language': 'korean',
        'option': 'a'
    }

    sfx_url = "http://10.10.18.186:7578/ksm/sfx/candidate"
    response = requests.get(sfx_url, params=params)

    result = json.loads(response.content, strict=False)

    for node in result["result"]:
        pattern = node["pattern"]
        results["pattern"] = pattern

    return results

def print_result(lines):
    print()
    print("============== 형태소 분석 ==============")
    print()
    for line in lines:
        if len(line) > 0:
            morph_results = get_morphs(line)
            pattern_results = get_pattern(line)
            print("원문:\t" + line)
            print("lemma:\t" + morph_results["tokens"])
            print("형태소:\t" + morph_results["morph_tag_tokens"])
            print("#S:\t" + morph_results["sharp_tag_tokens"])
            print("자동:\t" + pattern_results["pattern"])
            print()