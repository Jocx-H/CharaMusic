#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import shutil
from typing import List
from service.music_creator import *
from service.music_creator import __prepareMid__, __createFinalMid__, __createTempMid__

BASE_PATH = dirname(dirname(abspath(__file__)))
TEMP_PATH = os.path.join(BASE_PATH, r'assets/temp')
VOCABULARY_PATH = os.path.join(BASE_PATH, r'assets/vocabulary')
WEIGHTS_PATH = os.path.join(BASE_PATH, r'assets/model')
BISHUN_PATH = os.path.join(BASE_PATH, r'assets/bishun/bishun_table.csv')
POEM_PATH = os.path.join(BASE_PATH, r'assets/poem/poem.json')
COLOR_PATH = os.path.join(BASE_PATH, r'assets/colors/color.json')
INPUT_PATH_SEG = '/music/prepare_mid/'
OUTPUT_PATH_SEG = '/music/temp_mid/'
TEMPMID_PATH_SEG = OUTPUT_PATH_SEG
FINAL_PATH_SEG = '/music/res_mid/'
FINAL_MP3_PATH_SEG = '/music/res_wav/'
SEG_LEN = 128
RNN_SIZE = 256
MAX_BARS = 10
TEMPERATURE = 0.8
MIDI_NUM = 3

NUM2NOTE = {'1': 'C', '2': 'D', '3': 'E', '4': 'G', '5': 'A'}

# 情绪类别
SAD = 'sa'
HAPPY = 'ha'
PASSIVE = 'pa'
# 情绪对应的BPM范围
BPM_SAD = [i for i in range(60, 110)]
BPM_HAPPY = [i for i in range(110, 160)]
BPM_PASSIVE = [i for i in range(50, 70)]
BPM_PASSIVE.extend([i for i in range(140, 170)])
# 情绪对应的八度范围
BADU_SAD = [i for i in range(3, 6)]
BADU_HAPPY = [i for i in range(4, 6)]
BADU_PASSIVE = [i for i in range(5, 6)]
# 情绪对应的时值范围以及被选到的概率
DURATION_SAD = [0.125, 0.25, 0.375, 0.5, 0.625]
RATE_SAD = [0.1, 0.3, 0.3, 0.2, 0.1]
DURATION_HAPPY = [0.125, 0.25, 0.375]
RATE_HAPPY = [0.4, 0.3, 0.3]
DURATION_PASSIVE = [0.125, 0.25, 0.375, 0.5]
RATE_PASSIVE = [0.1, 0.3, 0.3, 0.3]

CHAR_MAJOR = 1
CHAR_MINOR = 2
MAJOR_START_NOTES = ['C', 'E', 'G']
RATE_MAJOR_START_NOTES = [0.5, 0.3, 0.2]
MINOR_START_NOTES = ['A', 'C', 'E']
RATE_MINOR_START_NOTES = [0.5, 0.3, 0.2]
END_NOTES = ['C', 'E', 'G']

START_NOTE_NUM = [3, 4]
INTERVAL_LIST = [-3, -2, -1, 1, 2, 3, 4, 5, 6]

VARIATION_LIST = [1, 2, 3, 4]
RATE_VARIATION = [0.2, 0.2, 0.2, 0.4]


def __getLabel__(section_emo: list) -> list:
    r"""根据情绪分数值选择情绪标签"""
    section_emo_label = []
    for i in section_emo:
        i = float(i)
        if 0.1 <= i < 0.5:
            section_emo_label.append('sa')
        elif 0.5 <= i < 0.9:
            section_emo_label.append('ha')
        else:
            section_emo_label.append('pa')
    return section_emo_label


def __getColorLabel__(emo_value: float) -> str:
    r"""根据情绪得分获得颜色标签"""
    emo_value = float(emo_value)
    if 0.1 <= emo_value < 0.45:
        return 'sad'
    elif 0.45 <= emo_value < 0.55:
        return 'normal'
    elif 0.55 <= emo_value < 0.9:
        return 'happy'
    return 'passion'


def __getPomes__(count: int, section_emo: List[float]) -> dict:
    r"""根据情绪分数值选择诗句"""
    poem_path = POEM_PATH
    poems = [[], [], []]
    try:
        with open(poem_path, 'r', encoding='utf-8') as R:
            poem_dict = json.load(R)
            for i in range(len(section_emo)):
                sentences = poem_dict[str(int(section_emo[i] * 10))]
                count = min(len(sentences), count)
                if i != len(section_emo) - 1:
                    poem_temp = random.sample(sentences, count)
                    for p in poem_temp:
                        poems[0].append(p['name'])
                        poems[1].append(p['author'])
                        poems[2].append(p['sentence'])
                else:
                    poem_temp = random.sample(sentences, count)
                    for p in poem_temp:
                        poems[0].append(p['name'])
                        poems[1].append(p['author'])
                        poems[2].append(p['sentence'])
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    return {'names': poems[0], 'authors': poems[1], 'sentences': poems[2]}


def __getColors__(count: int, color_value: List[float]) -> dict:
    r"""根据mid文件的长度和颜色标签获取对应的rgb"""
    color_path = COLOR_PATH
    res = [[], [], []]
    try:
        with open(color_path, 'r') as R:
            colors_dict = json.load(R)
            for i in range(len(color_value)):
                color_label = __getColorLabel__(color_value[i])
                emo_colors = colors_dict[color_label]
                # 在情绪标签的字典中随机选取一个色系
                color_type = random.choice(list(emo_colors.keys()))
                if i == len(color_value) - 1:
                    color_temp = random.sample(emo_colors[color_type], min(count + 1, 7))
                    for c in color_temp:
                        res[0].append(c['name'])
                        res[1].append(c['rgb'])
                        res[2].append(c['light'])
                else:
                    color_temp = random.sample(emo_colors[color_type], min(count, 7))
                    for c in color_temp:
                        res[0].append(c['name'])
                        res[1].append(c['rgb'])
                        res[2].append(c['light'])
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    return {'color_names': res[0], 'color_rgbs': res[1], 'color_lights': res[2]}


async def createMid(identify: str, sentence_emotion: str, words: List[str], section_emos: List[float], dynasty: int) -> bool:
    r"""用于生成音乐
    :return: 生成成功返回True，失败返回False
    """
    emos = __getLabel__(section_emos)
    key_words = []
    for i in range(len(words)):
        key_words.append((words[i], emos[i]))
    music_path = os.path.join(TEMP_PATH, identify + r'/music')
    if os.path.exists(music_path):
        shutil.rmtree(music_path)
    os.mkdir(music_path)
    music_sub_path = ['prepare_mid', 'res_mid', 'res_wav', 'temp_mid']
    for i in music_sub_path:
        path = os.path.join(music_path, i)
        if not os.path.exists(path):
            os.mkdir(path)
    try:
        if not await __prepareMid__(identify, key_words):
            raise Exception('生成初始音乐失败')
        if not await __createTempMid__(identify):
            raise Exception('LSTM生成音乐失败')
        if not await __createFinalMid__(identify, sentence_emotion, dynasty):
            raise Exception('修饰音乐失败')
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        return False
    return True


def getMidFile(identify: str) -> str:
    r"""获得mid文件的下载路径"""
    mid_path = os.path.join(TEMP_PATH, identify + FINAL_PATH_SEG + 'result.mid')
    if not os.path.exists(mid_path):
        raise Exception('mid_path is not exists.')
    return mid_path


def getMp3File(identify: str) -> str:
    r"""获得mp3文件的下载路径"""
    mp3_path = os.path.join(TEMP_PATH, identify + FINAL_MP3_PATH_SEG + 'result.mp3')
    if not os.path.exists(mp3_path):
        raise Exception('mp3_path is not exists.')
    return mp3_path


async def getBg(identify: str, section_emos: List[float]) -> dict:
    r"""获得各种标签，一定要在最终mid生成后使用"""
    try:  # 获得图片和古诗的数量
        mid = os.path.join(TEMP_PATH, identify + FINAL_PATH_SEG + 'result.mid')
        bpm, song, start_time = read(mid).merge()
        song_time = song.eval_time(bpm)
        song_time = float(song_time[0: len(song_time) - 1])
        count = int(song_time / (len(section_emos) * 3))
    except Exception('失败，最终mid文件还没有生成') as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    try:  # 装载图片和古诗
        colors = __getColors__(count, section_emos)
        poems = __getPomes__(count, section_emos)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    return {'length': len(colors['color_names']), 'colors': colors, 'poems': poems}
