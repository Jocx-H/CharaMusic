import json
import random
import time
import os
import traceback
from os.path import dirname, abspath

BASE_PATH = dirname(dirname(abspath(__file__)))
BASE_PATH = BASE_PATH.replace('\\', '/')
TEMP_PATH = os.path.join(BASE_PATH, r'assets/temp')
PICTURES_PATH = os.path.join(BASE_PATH, r'assets/pictures/pics')
PICTURES_INFO_PATH = os.path.join(BASE_PATH, r'assets/pictures/picture_infos')


def getToken():
    r"""为用户创建新的Temp文件夹，但在此之前先删除其他文件夹"""
    now = str(time.time_ns())
    file_path = os.path.join(TEMP_PATH, now)
    if not os.path.exists(file_path):
        try:
            os.mkdir(file_path)
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
            raise e
    pic_path = PICTURES_PATH
    files = os.listdir(pic_path)
    file_size = len(files)
    picture_id = random.randint(0, file_size - 1)
    return {'token': now, 'picture_id': picture_id, 'pic_name': files[picture_id]}


def getPic(pic_id: int):
    r"""返回获取的图片路径"""
    try:
        pic_path = PICTURES_PATH
        pic_name = os.listdir(pic_path)[pic_id]
        pic_path = os.path.join(PICTURES_PATH, pic_name)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    return pic_path


def getPictureInfo(pic_id: int) -> dict:
    r"""获取图片对应的信息"""
    try:
        pic_path = PICTURES_PATH
        picture = os.listdir(pic_path)[pic_id].split("：")[0]
        info_json = os.path.join(PICTURES_INFO_PATH, 'info.json')
        with open(info_json, 'r', encoding='utf-8') as R:
            infos = json.load(R)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    return infos[picture]