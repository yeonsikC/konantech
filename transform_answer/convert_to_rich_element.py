
import getConf


def convert_title(title):
    title_dict = {
        "type": "title",
        "text": title
    }
    return title_dict


def convert_sub_title(sub_title):
    sub_title_dict = {
        "type": "subtitle",
        "text": sub_title
    }
    return sub_title_dict


def convert_text(text):
    replace_list = ["<p>", "</p>"]
    for tag in replace_list:
        text.replace(tag, "")
    text_dict = {
        "type": "text",
        "text": text
    }
    return text_dict


def convert_buttons(button_list, button_type):
    splitter = getConf.getElement("trans", "button_splitter")
    button_dict = {
        "type": "buttons",
        "layout": "vertical",
        "elements": []
    }
    for element in button_list:
        element_dict = dict()
        split_list = element.split(splitter)
        if button_type == "postback":
            element_dict["type"] = "postback"
            if element != "":
                if len(split_list) == 2:
                    element_dict["text"] = split_list[0]
                    element_dict["value"] = split_list[1]
                else:
                    element_dict["text"] = element
                    element_dict["value"] = ""
        elif button_type == "url":
            element_dict["type"] = "web_url"
            if element != "":
                if len(split_list) == 2:
                    element_dict["text"] = split_list[0]
                    element_dict["url"] = split_list[1]
                else:
                    element_dict["text"] = element
                    element_dict["url"] = ""
        button_dict["elements"].append(element_dict)
    return button_dict


def convert_image(image_file_name):
    image_path = getConf.getElement("trans", "image_url")
    domain = getConf.getElement("trans", "domain")
    image_dict = {
        "type": "image",
        "width": "",
        "height": "",
        "filename": domain + "_" + image_file_name,
        "value": image_path + domain + "_" + image_file_name
    }
    return image_dict


def convert_audio(audio_url):
    audio_dict = {
        "type": "audio",
        "text": audio_url
    }
    return audio_dict


def convert_frame(frame_url):
    frame_dict = {
        "type": "iframe",
        "text": frame_url
    }
    return frame_dict


def convert_video(video_url):
    video_dict = {
        "type": "video",
        "text": video_url
    }
    return video_dict


def convert_expansion(file_name):
    file_path = getConf.getElement("trans", "expansion_url")
    expansion_dict = {
        "type": "expansion",
        "filename": file_name,
        "text": file_path + file_name
    }
    return expansion_dict