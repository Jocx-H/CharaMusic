#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import hashlib
import os
import random
import re
import time
import traceback
from json import dumps
from os.path import abspath, dirname

import requests
from aip import AipNlp
from fastapi import UploadFile
from snownlp import SnowNLP

BASE_PATH = dirname(dirname(abspath(__file__)))
BASE_PATH = BASE_PATH.replace('\\', '/')
TEMP_PATH = os.path.join(BASE_PATH, r'assets/temp')
POEM_PATH = os.path.join(BASE_PATH, r'assets/poem/poem.json')

section_count = 4  # 音乐的小节

BAIDU_SECRET_KEY = {
    'id': '',  
    'key': '',  
    'secret': ''
}  # 百度密钥
client = AipNlp(BAIDU_SECRET_KEY['id'],
                BAIDU_SECRET_KEY['key'],
                BAIDU_SECRET_KEY['secret'])

xf_hw_url = ''  # 讯飞手写识别连接
xf_url = ''  # 讯飞文本识别连接
XF_SECRET_KEY = {
    'id': '',
    'key': ''
}  # 讯飞密钥（请填写自己的）
img_reco_confidence = 0.7


def __getHeader__():
    cur_time = str(int(time.time()))
    param = dumps({'language': 'cn|en'})
    param_base64 = base64.b64encode(param.encode('utf-8'))

    m2 = hashlib.md5()
    str1 = XF_SECRET_KEY['key'] + cur_time + str(param_base64, 'utf-8')
    m2.update(str1.encode('utf-8'))
    check_sum = m2.hexdigest()
    # 组装http请求头
    header = {
        'X-CurTime': cur_time,
        'X-Param': param_base64,
        'X-Appid': XF_SECRET_KEY['id'],
        'X-CheckSum': check_sum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


def __getBody__(file_path: str):
    with open(file_path, 'rb') as f:
        img_file = f.read()
    data = {'image': str(base64.b64encode(img_file), 'utf-8')}
    return data


async def __detectHandwritingImg__(img_path: str) -> dict:
    r"""对手写图片进行识别"""
    try:
        r = requests.post(xf_hw_url, headers=__getHeader__(), data=__getBody__(img_path))
        r = r.json()
        if r['data'] == '':
            return {'sus': False, 'text': ''}
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    text = ''  # 识别出来的文本结果
    for line in r['data']['block'][0]['line']:
        if line['confidence'] > img_reco_confidence:
            text += (line['word'][0]['content'])
    return {'sus': True, 'text': text}


def __getLabel__(emo: float) -> str:
    if 0.1 <= emo < 0.5:
        return 'sa'
    elif 0.5 <= emo < 0.9:
        return 'ha'
    return 'pa'


async def recognizeHandWritingImg(identify: str, img: UploadFile) -> bool:
    r"""上传并识别印刷体图片，返回识别后的信息"""
    try:
        content = await img.read()  # 先把数据流存成图片再检测
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        return False
    suffix = '.' + img.filename.split('.')[-1]
    assert suffix == '.jpg' or suffix == '.JPG' or \
           suffix == '.bmp' or suffix == '.BMP' or \
           suffix == '.png' or suffix == '.PNG', "只支持JPG，PNG, BMP"
    assert type(content) is bytes, "文件流应该是Bytes类型吧？" + str(content)
    # 先存到临时的文件待检测
    img_path = os.path.join(TEMP_PATH, identify + r'/handwritingimg_temp' + suffix)
    with open(img_path, 'wb') as f:
        f.write(content)
    res = await __detectHandwritingImg__(img_path)
    # 能成功识别出是文本后才存储
    if res['sus']:
        txt_path = os.path.join(TEMP_PATH, identify + r'/handwritingchar_temp.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(res['text'])
    return res['sus']


async def textAnalysis(text: str) -> dict:
    r"""
    对文本进行情感分析
    :vocabulary text: 待分析文本
    :return: 情感分析后的各种参数

    Example:
    {
        sentence_emotion: 整句话的情感分析,
        key_token: 关键词列表,
        emos: 关键词情感得分列表
    }
    """
    text = re.sub('[a-zA-Z]+', '', text)
    sentences = re.split(r'\W+', text)
    section_key = []
    section_emo = []
    for sen in sentences:
        if len(sen) == 0:
            continue
        # 每个小节选取一个关键词并情感分析
        nlp = SnowNLP(sen)
        key_tokens = nlp.keywords(limit=1)
        key_token = ''
        if len(key_tokens) == 0:
            tokens = list(nlp.tags)
            for seq in tokens:
                if seq[1] == 'a' or seq[1] == 'n' or seq[1] == 'v':
                    key_token = seq[0]
                    break
            else:
                key_token = random.sample(nlp.words, 1)[0]
        else:
            key_token = key_tokens[0]
        assert key_token != '', '关键词为空，选取错误'
        time.sleep(0.1)
        nlp_t = SnowNLP(sen)
        snow_emo = nlp_t.sentiments
        section_key.append(key_token)
        section_emo.append(snow_emo)  # 情感分析补正
    time.sleep(0.5)
    sentence_snow = SnowNLP(text)
    emo = sentence_snow.sentiments
    sentence_emo_label = __getLabel__(emo)
    return {'sentence_emo_label': sentence_emo_label,
            'key_tokens': section_key, 'section_emo_values': section_emo}


async def getHandwritingImgText(identify: str) -> dict:
    r"""
    获得手写图片分析出来后的文本
    """
    text_file = os.path.join(TEMP_PATH, identify + r'/handwritingchar_temp.txt')
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    return {'text': text}
