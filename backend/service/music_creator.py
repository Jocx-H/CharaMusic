#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import traceback
import os
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from keras.layers import Dense
from keras.layers import Input
from keras.layers import LSTM
from keras.models import Sequential
from keras.utils.np_utils import to_categorical
from music21 import chord as chord21
from music21 import converter as converter21
from music21 import interval as interval21
from music21 import key as key21
from music21 import note as note21
from music21 import pitch as pitch21
from music21 import stream as stream21
from musicpy.sampler import S, C, N, chord, note, sampler, piece, volume
from musicpy.sampler import read, write, concat, set_effect, degree_to_note
from musicpy.sampler import fade, fade_out

BASE_PATH = dirname(dirname(abspath(__file__)))
TEMP_PATH = os.path.join(BASE_PATH, r'assets/temp')
VOCABULARY_PATH = os.path.join(BASE_PATH, r'assets/vocabulary')
WEIGHTS_PATH = os.path.join(BASE_PATH, r'assets/model')
BISHUN_PATH = os.path.join(BASE_PATH, r'assets/bishun/bishun_table.csv')
MUSICSF2_PATH = os.path.join(BASE_PATH, r'assets/china_sf2')
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
BPM_SAD = [i for i in range(85, 125)]
BPM_HAPPY = [i for i in range(125, 170)]
BPM_PASSIVE = [i for i in range(130, 170)]
# BPM_PASSIVE.extend([i for i in range(80, 100)])
# 情绪对应的八度范围
BADU_SAD = [3, 4, 5]
BADU_HAPPY = [4, 5]
BADU_PASSIVE = [4, 5]
# 情绪对应的时值范围以及被选到的概率
DURATION_SAD = [0.125, 0.25, 0.375, 0.5, 0.625]
RATE_SAD = [0.1, 0.3, 0.3, 0.2, 0.1]
DURATION_HAPPY = [0.125, 0.25, 0.375]
RATE_HAPPY = [0.4, 0.3, 0.3]
DURATION_PASSIVE = [0.125, 0.25, 0.375, 0.5]
RATE_PASSIVE = [0.2, 0.3, 0.3, 0.2]

CHAR_MAJOR = 1
CHAR_MINOR = 2
MAJOR_START_NOTES = ['C', 'E', 'G']
RATE_MAJOR_START_NOTES = [0.5, 0.3, 0.2]
MINOR_START_NOTES = ['A', 'C', 'E']
RATE_MINOR_START_NOTES = [0.5, 0.3, 0.2]
END_NOTES = ['C', 'E', 'G']
# 起始音音符数量
START_NOTE_NUM = [3, 4]
# 可选的音程
INTERVAL_LIST = [-3, -2, -1, 1, 2, 3, 4, 5, 6]
# 齐奏
UNISON_PLAY = 1
# 重奏
REPEAT_PLAY = 2
# 重复
REPEAT_MUSIC = 1
# 重复手法可以变化的位置|变头|变中|变尾
REPEAT_CHANGE_POS = [1, 2, 3]
# 模进
CHANGE_PITCH = 2
# 模进可以选择的音符
PITCH_POS = ['C', 'D', 'E', 'G', 'A']
# 简单的变奏手法
VARIATION_LIST = [1, 2, 3]
RATE_VARIATION = [0.2, 0.4, 0.4]
# 乐器及其弹奏手法
# 古筝
GUZHENG = 1
GUZHENG_LUN = 1  # 起始音轮指
GUZHENG_SUS = 2  # 正常弹
GUZHENG_SAO = 3  # 扫弦
GUZHENG_HUA = 4  # 上滑音
# 笛子
DIZI = 2
DIZI_ART = 1    # 起始音
DIZI_F = 2      # 正常吹
# 古琴
GUQIN = 3
GUQIN_LOOPS = 1
GUQIN_PROCHG = 2    # 正常弹1
GUQIN_MO = 3        # 正常弹2
GUQIN_GOU = 4       # 正常弹3
GUQIN_HUA = 5       # 上滑音
GUQIN_FAN = 6       # 泛音
# 琵琶
PIPA = 4
PIPA_LOOPS = 1      # 起始音
PIPA_PROCHG = 2     # 正常弹
PIPA_SAO = 3        # 扫弦
PIPA_DLUN = 4       # 短轮指
PIPA_FAN = 5        # 泛音
# 二胡
ERHU = 5
ERHU_KEY = 1  # 正常弹
ERHU_HUA = 2  # 上滑音
# 扬琴
YANGQIN = 6
YANGQIN_LUN = 1  # 轮指
YANGQIN_SUS = 2  # 正常吹
YANGQIN_SAO = 3  # 长音扫弦
# 埙
XUN = 7
XUN_PRO = 1  # 正常吹
XUN_LONG = 2  # 长音
# 笙
SHENG = 8
SHENG_SUS = 1  # 正常吹
# 箫
XIAO = 9
XIAO_LOOPS = 1  # 起始音
XIAO_SUS = 2  # 正常吹
# 唢呐
SUONA = 10
SUONA_LOOPS = 1  # 起始音
SUONA_DSUS = 2  # 正常吹
SUONA_HUA = 3  # 上滑音

INSTRUMENTS_DICT = {GUZHENG:
                        [(GUZHENG_LUN, 'GuZheng_blswspy.sf2'), (GUZHENG_SUS, 'GuZheng_sus.sf2'),
                         (GUZHENG_SAO, 'GuZheng_VibShaker1.sf2'), (GUZHENG_HUA, 'GuZheng_Ud2dk.sf2')],
                    DIZI:
                        [(DIZI_ART, 'DiZi_ArtfillKeyA1.sf2'), (DIZI_F, 'DiZi_FHighLeg.sf2')],
                    GUQIN:
                        [(GUQIN_LOOPS, 'GuQin_SJ-Loops.sf2'), (GUQIN_PROCHG, 'GuQin_ProChg.sf2'),
                         (GUQIN_MO, 'GuQin_Mo.sf2'), (GUQIN_GOU, 'GuQin_GouVelLeg.sf2'),
                         (GUQIN_HUA, 'GuQin_GouVelUp.sf2'), (GUQIN_FAN, 'GuQin_Harmonics.sf2')],
                    PIPA:
                        [(PIPA_LOOPS, 'PiPa_SJ-Loops.sf2'), (PIPA_PROCHG, 'PiPa_ProChg.sf2'),
                         (PIPA_SAO, 'PiPa_SusRoll.sf2'), (PIPA_DLUN, 'PiPa_GZ1P.sf2'),
                         (PIPA_FAN, 'PiPa_VibLeg.sf2')],
                    ERHU:
                        [(ERHU_KEY, 'ErHu_KeySwitchB.sf2'), (ERHU_HUA, 'ErHu_GraceUpKs1.sf2')],
                    YANGQIN:
                        [(YANGQIN_SUS, 'YangQin_Sus.sf2'), (YANGQIN_LUN, 'YangQin_Loop.sf2'),
                         (YANGQIN_SAO, 'YangQin_SusPro.sf2')],
                    XUN:
                        [(XUN_PRO, 'Xun_ProGram.sf2'), (XUN_LONG, 'Xun_VibCryFX.sf2')],
                    SHENG:
                        [(SHENG_SUS, 'Sheng_LegMw.sf2')],
                    XIAO:
                        [(XIAO_LOOPS, 'Xiao_Loop.sf2'), (XIAO_SUS, 'Xiao_SusVibLeg.sf2')],
                    SUONA:
                        [(SUONA_LOOPS, 'SuoNa_Loop.sf2'), (SUONA_DSUS, 'SuoNa_DSusLeg.sf2'),
                         (SUONA_HUA, 'SuoNa_VibVelUpLeg.sf2')]
                    }

# 朝代
QIN = 1
HAN = 2
JIN = 3
TANG1 = 4
TANG2 = 5
SONG = 6
MING = 7
# 朝代与乐器组合
DYNASTY_INSTRUMENTS = {QIN: [(GUZHENG, ERHU), (GUZHENG, XIAO), (GUZHENG, XUN)],
                       HAN: [(DIZI, YANGQIN, ERHU), (DIZI, ERHU, PIPA), (DIZI, ERHU, GUZHENG), (DIZI, XIAO)],
                       JIN: [(GUQIN, GUZHENG, DIZI), (GUQIN, XUN), (GUQIN, XIAO)],
                       TANG1: [(PIPA, DIZI), (PIPA, GUZHENG, XIAO)],
                       TANG2: [(XIAO, ERHU, PIPA), (XIAO, GUZHENG, PIPA)],
                       SONG: [(ERHU, PIPA), (ERHU, GUZHENG)],
                       MING: [(YANGQIN, PIPA), (YANGQIN, ERHU), (SUONA, DIZI)]}
# 乐器组合被选中的概率
DYNASTY_INSTRUMENTS_RATE = {QIN: [0.1, 0.5, 0.4],
                            HAN: [0.2, 0.3, 0.3, 0.2],
                            JIN: [0.2, 0.4, 0.4],
                            TANG1: [0.3, 0.7],
                            TANG2: [0.4, 0.6],
                            SONG: [0.5, 0.5],
                            MING: [0.5, 0.4, 0.1]}
# 乐器适合的音高|主要是正常弹
INSTRUMENTS_PITCH = {GUZHENG: 'C5', DIZI: 'C5', GUQIN: 'C4', PIPA: 'C4',
                     ERHU: 'A4', YANGQIN: 'C5', XUN: 'C4', SHENG: 'A4', XIAO: 'E3', SUONA: 'G4'}

INSTRUMENTS_RANGE = {ERHU: [59, 83], XUN: [55, 76], XIAO: [45, 79]}

def __fBishunDecoder__(text):
    r"""解码笔顺，得到初始音符序列"""
    df = pd.read_csv(BISHUN_PATH)
    df = df.set_index('汉字').T.to_dict()
    shuns = []
    for word in text:
        shuns2 = []
        shun = df[word]['笔顺']
        for i in shun:
            shuns2.append(int(i))
        shuns.extend(shuns2)
    for i in range(0, len(shuns) - 1):
        if abs(shuns[i] - shuns[i + 1]) >= 3:
            a, b = 0, 0
            if shuns[i] < shuns[i + 1]:
                a = shuns[i]
                b = shuns[i + 1]
            else:
                a = shuns[i + 1]
                b = shuns[i]
            candidate = [s for s in range(a + 1, b)]
            shuns.insert(i + 1, np.random.choice(candidate))
    notes = ''
    for i in shuns:
        notes += NUM2NOTE[str(i)]
    return notes


def __fGenerateBadu__(word):
    r"""根据关键词的情绪选择一个合适的八度域"""
    badu = 4
    if word[1] == SAD:
        badu = np.random.choice(BADU_SAD)
    elif word[1] == HAPPY:
        badu = np.random.choice(BADU_HAPPY)
    elif word[1] == PASSIVE:
        badu = np.random.choice(BADU_PASSIVE)
    return badu


def __fGenerateDuration__(note_num, emotion):
    r"""根据音符数量和情绪生成对应的时值"""
    duration = None  # array类型
    if emotion == SAD:
        duration = np.random.choice(
            DURATION_SAD, size=note_num, replace=True, p=RATE_SAD)
    elif emotion == HAPPY:
        duration = np.random.choice(
            DURATION_HAPPY, size=note_num, replace=True, p=RATE_HAPPY)
    elif emotion == PASSIVE:
        duration = np.random.choice(
            DURATION_PASSIVE, size=note_num, replace=True, p=RATE_PASSIVE)
    return duration.tolist()


def __fGenerateBpm__(emotion):
    r"""根据情绪生成对应的bpm"""
    if emotion == SAD:
        word_bpm = np.random.choice(BPM_SAD)
    elif emotion == HAPPY:
        word_bpm = np.random.choice(BPM_HAPPY)
    else:
        word_bpm = np.random.choice(BPM_PASSIVE)
    return word_bpm


def __fModifySectionsHelp__(song_con_chord):
    r"""辅助修饰小节，合并一个小节内连续多个相同音符的为单个音符"""
    if_merge = 0
    if len(song_con_chord) <= 3:
        if_merge = np.random.choice([0, 1], p=[0.4, 0.6])
    else:
        if_merge = 1
    single_chord = chord([song_con_chord[0]])
    note_interval = 1
    if if_merge:
        sum_intervals = sum(song_con_chord.interval)
        if sum_intervals < 1.5:
            note_interval = sum_intervals
        else:
            note_interval = 1.5
        single_chord = single_chord.set(duration=note_interval, interval=note_interval)
        return single_chord, note_interval
    else:
        return song_con_chord, song_con_chord.interval


def __fGenStartingForm__(music_phrase_list, music_scale=CHAR_MAJOR):
    r"""生成起始式的op"""
    sf_scale = None
    if music_scale == CHAR_MAJOR:
        sf_scale = S('C major')
    if music_scale == CHAR_MINOR:
        sf_scale = S('C minor')
    start_song = music_phrase_list[0]
    start_badu = start_song[0].num
    sf_start_note = None
    sf_second_note = None
    sf_third_note = None
    sf_fourth_note = None
    sf_chord = chord([])
    sf_duration = []
    # 随机选择起始式的音符数量
    sf_start_note_num = np.random.choice(START_NOTE_NUM)
    # 随机选择第一个音符
    sf_start_note = note(np.random.choice(MAJOR_START_NOTES, p=RATE_MAJOR_START_NOTES), start_badu)
    sf_chord.append(sf_start_note)
    # 获得第一个音符为根音的三和弦
    sf_standrad_chord = C(sf_start_note.name, start_badu)
    # 开始处理后续音符
    if sf_start_note_num == 3:
        # 为第一个音符设置时值
        sf_duration.append(0.625)
        # 选第二个音符，必须在C大调内
        sf_second_note = sf_start_note.with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
        while sf_second_note.name not in sf_scale:
            sf_second_note = sf_start_note.with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
        sf_chord.append(sf_second_note)
        # 为第二个音符设置时值
        sf_duration.append(np.random.choice([0.375, 0.5]))
        # 选第三个音符，不能和第二个音符相同
        sf_third_note = np.random.choice(sf_standrad_chord - sf_start_note)
        while sf_third_note.name == sf_second_note.name:
            sf_third_note = np.random.choice(sf_standrad_chord - sf_start_note)
        sf_chord.append(sf_third_note)
        # 为第三个音符设置时值
        sf_duration.append(np.random.choice([0.5, 0.75]))
        sf_chord = sf_chord.set(sf_duration, sf_duration)
    elif sf_start_note_num == 4:
        # 选第一个音符的时值
        sf_duration.append(np.random.choice([0.5, 0.75]))
        # 选第二个音符，必须在C大调内
        sf_second_note = sf_start_note.with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
        while sf_second_note not in sf_scale:
            sf_second_note = sf_start_note.with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
        sf_chord.append(sf_second_note)
        # 为第二个音符设置时值
        sf_duration.append(np.random.choice([0.375, 0.5]))
        # 选第三个音符，不能和第二个音符相同
        sf_third_note = np.random.choice(sf_standrad_chord - sf_start_note)
        while sf_third_note not in sf_scale or sf_third_note.name == sf_second_note.name:
            sf_third_note = np.random.choice(sf_standrad_chord - sf_start_note)
        sf_chord.append(sf_third_note)
        # 选第三个音符的时值
        sf_duration.append(np.random.choice([0.375, 0.5]))
        # 选第四个音符
        start_bar = start_song.firstnbars(1)
        sf_fourth_note = sf_third_note.with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
        temp_num = 0
        while sf_fourth_note not in sf_scale or abs(
                start_bar[0].degree - sf_fourth_note.degree) > 6 or sf_fourth_note == sf_third_note:
            sf_fourth_note = sf_third_note.with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
            temp_num += 1
            if temp_num >= 20:
                while sf_fourth_note not in sf_scale:
                    sf_fourth_note = start_bar[0].with_interval(int(np.random.choice(INTERVAL_LIST)))[1]
                break
        sf_chord.append(sf_fourth_note)
        # 选第四个音符的时值
        sf_duration.append(np.random.choice([0.5, 0.75]))
        sf_chord = sf_chord.set(sf_duration, sf_duration)
    music_phrase_list.insert(0, sf_chord)
    return music_phrase_list


def __fChoiceScale__(sentence_emotion):
    r"""根据整个句子的情绪选择音阶"""
    music_scale = None
    if sentence_emotion == SAD:
        music_scale = np.random.choice([CHAR_MINOR, CHAR_MAJOR], p=[0.4, 0.6])
    elif sentence_emotion == HAPPY:
        music_scale = CHAR_MAJOR
    elif sentence_emotion == PASSIVE:
        music_scale = np.random.choice([CHAR_MINOR, CHAR_MAJOR], p=[0.1, 0.9])
    return music_scale


def __fGenEndingFormHelp__(end_note):
    r"""辅助生成终止式，判断end_note和E、G谁接近"""
    end_note_degree = end_note.degree
    res_E = N('E' + str(end_note.num))
    res_G = N('G' + str(end_note.num))
    if abs(res_E.degree - end_note_degree) < abs(res_G.degree - end_note_degree):
        if end_note != res_E:
            return res_E
        else:
            return res_G
    else:
        if end_note != res_G:
            return res_G
        else:
            return res_E


def __fGenEndingForm__(music_phrase_list):
    """生成终止式"""
    ef_end_bar = chord([])
    ef_end_duration = []
    end_note = music_phrase_list[-1][-1]
    end_interval = music_phrase_list[-1].interval
    end_interval_new = end_interval
    if sum(end_interval) / len(end_interval) <= 0.375:
        end_interval_new = [i + 0.25 for i in end_interval]
        if end_interval_new[-1] < 0.75:
            end_interval_new[-1] = 0.75
    music_phrase_list[-1] = music_phrase_list[-1].set(duration=end_interval_new, interval=end_interval_new)
    # 生成终止式倒数第二个音符
    ef_second_note = __fGenEndingFormHelp__(end_note)
    ef_end_bar.append(ef_second_note)
    ef_end_duration.append(1.0)
    # 生成终止式最后的音符
    ef_end_note = N('C' + str(end_note.num))
    ef_end_bar += ef_end_note
    ef_end_duration.append(1.75)
    ef_end_bar = ef_end_bar.set(ef_end_duration, ef_end_duration)
    music_phrase_list.append(ef_end_bar)
    return music_phrase_list


def __fAdjustPitch__(music_phrase_list):
    r"""调整各音乐片段的音高"""
    for i in range(2, len(music_phrase_list) - 1):
        prev_phrase = music_phrase_list[i - 1]
        curr_phrase = music_phrase_list[i]
        prev_end_bar = prev_phrase.split_bars()[-1]
        curr_start_bar = curr_phrase.split_bars()[0]
        prev_end_bar_pitch = [j.degree for j in prev_end_bar]
        curr_start_bar_pitch = [j.degree for j in curr_start_bar]
        prev_avg_pitch = round(sum(prev_end_bar_pitch) / len(prev_end_bar_pitch))
        curr_avg_pitch = round(sum(curr_start_bar_pitch) / len(curr_start_bar_pitch))
        pitch_diff = int(prev_avg_pitch - curr_avg_pitch)

        if pitch_diff > 0 and pitch_diff / 12 >= 1:
            music_phrase_list[i] = music_phrase_list[i].up((pitch_diff // 12) * 12)
        elif pitch_diff < 0 and abs(pitch_diff) / 12 >= 1:
            music_phrase_list[i] = music_phrase_list[i].down((abs(pitch_diff) // 12) * 12)
        else:
            continue
    return music_phrase_list


def __fAdjustNoteHelp__(song_note, my_music_scale):
    r"""找到距离本音符音程最近的调式内的音"""
    my_music_scale.start = N('C' + str(song_note.num))  # 设置八度为song_note的
    standard_notes = my_music_scale.getScale().notes  # 获取音阶内的音符列表
    song_note_degree = song_note.degree
    replace_note = standard_notes[0]
    for sn in standard_notes:
        if abs(sn.degree - song_note_degree) < abs(replace_note.degree - song_note_degree):
            replace_note = sn
    return replace_note


def __fAdjustScaleNote__(song, my_music_scale=S('C major pentatonic')):
    """调整不在音阶内的音符"""
    # 调整不在音阶内的音符
    old_duration = song.get_duration()
    old_interval = song.interval
    for i in range(len(song)):
        if song[i] not in my_music_scale:
            replace_note = __fAdjustNoteHelp__(song[i], my_music_scale)
            song[i] = replace_note
    song = song.set(old_duration, old_interval)  # 重设为原song的时值和间隔
    return song


def __fJudgeRangeNote__(song, instrument):
    """判断是否在乐器音域内"""
    i_range = INSTRUMENTS_RANGE[instrument]
    for i in range(len(song)):
        if i_range[0] <= song[i].degree <= i_range[1]:
            continue
        else:
            return False
    return True


def __fAdjustLongDuration__(song):
    """
    调整一个song中过长的音符时值，随机概率合并连续多个相同音符为一个长音符
    """
    # 进行过长时值的处理
    song_new = chord([])
    song_new_interval = []
    song_interval = song.interval
    song_len = len(song) - 2
    i = 0
    while song_len - i >= 0:
        song_con_chord = chord([])
        song_con_interval = []
        while song[i] == song[i + 1]:
            song_con_chord.append(song[i])
            song_con_interval.append(song_interval[i])
            i += 1
        # 若不为0，则i所指的是最后一个重复音符
        if len(song_con_chord) != 0:
            song_con_chord.append(song[i])
            song_con_interval.append(song_interval[i])
        # 若此时仍不为0，则处理所有重复音符
        if len(song_con_chord) != 0:
            song_con_chord = song_con_chord.set(duration=song_con_interval, interval=song_con_interval)
            # 选择是否合并重复音符
            if_merge = 0
            if len(song_con_chord) <= 3:
                if_merge = np.random.choice([0, 1], p=[0.3, 0.7])
            else:
                if_merge = 1
            single_note = song_con_chord[0]
            single_note_interval = 1
            if if_merge:
                sum_intervals = sum(song_con_chord.interval)
                if sum_intervals < 1.5:
                    single_note_interval = sum_intervals
                else:
                    single_note_interval = 1.5
                song_new.append(single_note)
                song_new_interval.append(single_note_interval)
            # 若不合并，将每个音符和间隔添加进来
            else:
                for note_index in range(len(song_con_chord)):
                    song_new.append(song_con_chord[note_index])
                    song_new_interval.append(song_con_interval[note_index])
        # 非重复音符，直接添加
        else:
            if song_interval[i] > 1.5:
                song_interval[i] = 1.5
            song_new.append(song[i])
            song_new_interval.append(song_interval[i])
        i += 1
    song_new.append(song[-2])
    song_new.append(song[-1])
    song_new_interval.append(song_interval[-2])
    song_new_interval.append(song_interval[-1])
    song_new = song_new.set(duration=song_new_interval, interval=song_new_interval)
    return song_new


def __fAdjustDurationAndInterval__(music_phrase_list):
    """将时值和间隔调整为相同"""
    for p in range(len(music_phrase_list)):
        music_phrase_list[p].interval = music_phrase_list[p].get_duration()
    return music_phrase_list


def __fSectionNumJudge__(song_bars_len):
    """根据小节数量判断承与转的数量"""
    cheng_num = round((song_bars_len / 3) / 4)
    zhuan_num = round((2 * song_bars_len / 3) / 4)
    if (cheng_num + zhuan_num) * 4 > song_bars_len:
        zhuan_num -= 1
    return cheng_num, zhuan_num


def __fAddRepeat__(song_chord, change_pos):
    """音乐发展手法：重复+统一的少量变化"""
    song_chord_bars = song_chord.split_bars()
    song_chord_new = song_chord.copy()
    # 变头
    if change_pos == 1:
        note_index = int(np.random.choice([i for i in range(len(concat(song_chord_bars[:1])))]))
    # 变中
    elif change_pos == 2:
        note_index = int(np.random.choice([i for i in range(len(concat(song_chord_bars[1:2])))]))
    # 变尾
    else:
        note_index = int(np.random.choice([i for i in range(len(concat(song_chord_bars[2:])))]))
    note_up_down = int(np.random.choice([2, 3, 4, 5, 6]))
    up_or_down = np.random.choice([1, 2])
    if up_or_down == 1:
        song_chord_new = song_chord.up(note_up_down, note_index)
    elif up_or_down == 2:
        song_chord_new = song_chord.down(note_up_down, note_index)
    return song_chord_new


def __fAddChangePitch__(song_chord, pitch_pos):
    """音乐发展手法：模进"""
    note_badu = str(song_chord[0].num)
    song_chord_new = song_chord.reset_pitch(pitch_pos + note_badu)
    return song_chord_new


def __fAddReverse__(song_chord):
    """音乐发展手法：倒影"""
    return song_chord.reverse()


def __fMusicDevelop__(song, sentence_emotion=HAPPY):
    """
    使用音乐发展手法修饰音乐
    起、承、转、合
    """
    song_res = chord([])
    song = song.only_notes()
    song_bars = song.split_bars()
    song_bars_len = len(song_bars) - 7  # 除去起始式+起始4小节与终止式的2小节
    cheng_num, zhuan_num = __fSectionNumJudge__(song_bars_len)
    # 起|前5小节
    song_res += (concat(song_bars[:5]))
    # 承
    cheng_change_pos = np.random.choice(REPEAT_CHANGE_POS)
    cheng_pitch_pos = np.random.choice(PITCH_POS)
    for i in range(cheng_num):
        cheng_next_chord = concat(song_bars[5 + i * 4:5 + (i + 1) * 4])
        song_res += cheng_next_chord
        if np.random.choice([1, 2], p=[0.7, 0.3]) == REPEAT_MUSIC:
            cheng_next_chord_new = __fAddRepeat__(cheng_next_chord, cheng_change_pos)
        else:
            cheng_next_chord_new = __fAddChangePitch__(cheng_next_chord, cheng_pitch_pos)
            song_res = song_res.rest(0.25)
        song_res += cheng_next_chord_new
    # 转
    song_res_zhuan_temp = chord([])
    zhuan_change_pos = cheng_change_pos
    zhuan_pitch_pos = cheng_pitch_pos
    if zhuan_num - 1 >= 1:
        for i in range(cheng_num, cheng_num + zhuan_num - 1):
            zhuan_next_chord = concat(song_bars[5 + i * 4:5 + (i + 1) * 4])
            song_res_zhuan_temp += (zhuan_next_chord)
            zhuan_develop_choice = np.random.choice([1, 2, 3], p=[0.6, 0.2, 0.2])
            if zhuan_develop_choice == REPEAT_MUSIC:
                zhuan_next_chord_new = __fAddRepeat__(zhuan_next_chord, zhuan_change_pos)
            elif zhuan_develop_choice == CHANGE_PITCH:
                zhuan_next_chord_new = __fAddChangePitch__(zhuan_next_chord, zhuan_pitch_pos)
                song_res_zhuan_temp = song_res_zhuan_temp.rest(0.25)
            else:
                zhuan_next_chord_new = __fAddReverse__(zhuan_next_chord)
            song_res_zhuan_temp += (zhuan_next_chord_new)
    song_res_zhuan_temp += (concat(song_bars[5 + (cheng_num + zhuan_num - 1) * 4:-2]))
    # 调整节奏，进行扩展或紧缩
    song_res_temp_interval = song_res_zhuan_temp.interval
    if sentence_emotion == SAD and sum(song_res_temp_interval) / len(song_res_temp_interval) <= 0.375:
        song_res_temp_interval = [i + 0.25 for i in song_res_temp_interval]
    elif sentence_emotion == HAPPY and sum(song_res_temp_interval) / len(song_res_temp_interval) >= 0.375:
        for i in range(len(song_res_temp_interval)):
            if song_res_temp_interval[i] >= 0.25:
                song_res_temp_interval[i] -= 0.125
    elif sentence_emotion == PASSIVE and sum(song_res_temp_interval) / len(song_res_temp_interval) >= 0.375:
        for i in range(len(song_res_temp_interval)):
            if song_res_temp_interval[i] >= 0.25:
                song_res_temp_interval[i] -= 0.125
    song_res_zhuan_temp = song_res_zhuan_temp.set(duration=song_res_temp_interval, interval=song_res_temp_interval)
    song_res += song_res_zhuan_temp
    # 合
    # 有概率的重复起始句
    if np.random.random() <= 0.7:
        song_start_chord = concat(song_bars[1:5])
        song_start_chord_interval = song_start_chord.interval
        if sum(song_start_chord_interval) / len(song_start_chord_interval) <= 0.375:
            song_start_chord_interval_new = [i + 0.25 for i in song_start_chord_interval]
            song_start_chord = song_start_chord.set(duration=song_start_chord_interval_new,
                                                    interval=song_start_chord_interval_new)
        song_res += song_start_chord
    # 添加终止式
    song_res += concat(song_bars[-2:])
    return song_res


def __fAddTechnique1__(song):
    """添加弹奏手法：长音"""
    song_long = chord([])
    song_longi = []
    song_interval = song.interval
    for i in range(len(song_interval)):
        if 0.6 <= song_interval[i] <= 1.5:
            song_longi.append(i)
    if len(song_longi) - 5 <= 0:
        song_longi.append(1)
        song_long = song.pick(song_longi)
        song_long = set_effect(song_long, fade_out(500))
    else:
        chord_size = int((len(song_longi) - 4) * 0.5)
        song_longi = np.random.choice(song_longi[2:-2], replace=False, size=chord_size)
        if len(song_longi) != 0:
            song_longi = np.sort(song_longi)  # 不可或缺!
            song_long = song.pick(song_longi)
            song_long = set_effect(song_long, fade_out(500))
        else:
            np.append(song_longi, 1)
            song_long = song.pick(song_longi)
            song_long = set_effect(song_long, fade_out(500))
    return song_long, song_longi


def __fAddTechnique2__(song, song_longi=[]):
    """添加弹奏手法：上滑音"""
    song_hua = chord([])
    song_huai = []
    song_duration = song.get_duration()
    for i in range(len(song_duration) - 1):
        if 0.6 <= song_duration[i] <= 0.8 \
                and song[i + 1].degree - song[i].degree >= 2 \
                and i not in song_longi:
            if np.random.rand() <= 0.9:
                song_huai.append(i)
    if len(song_huai) != 0:
        song_hua = song.pick(song_huai)
        song_hua = set_effect(song_hua, fade(50, 500))
    else:
        song_huai.append(len(song) - 2)
        song_hua = song.pick(song_huai)
        song_hua = set_effect(song_hua, fade(50, 500))
    return song_hua, song_huai


def __fAddTechnique3__(song, song_longi=[]):
    """添加弹奏手法：短轮指"""
    song_dlun = chord([])
    song_dluni = []
    song_duration = song.get_duration()
    for i in range(len(song_duration) - 1):
        if 0.2 <= song_duration[i] <= 0.5 \
                and i not in song_longi:
            if np.random.rand() <= 0.3:
                song_dluni.append(i)
    if len(song_dluni) != 0:
        song_dlun = song.pick(song_dluni)
        song_dlun = set_effect(song_dlun, fade(50, 500))
    else:
        song_dluni.append(len(song) - 3)
        song_dlun = song.pick(song_dluni)
        song_dlun = set_effect(song_dlun, fade(50, 500))
    return song_dlun, song_dluni


def __fSplitSong__(song_bars):
    """
    将song中间部分按照6小节为单位分开，辅助重奏
    """
    song_6bars_list = []
    song_bars_len = len(song_bars) - 7  # 除去起始式+起始4小节与终止式的2小节
    change_num = round(song_bars_len / 6)
    if change_num <= 1:
        song_6bars_list.append(concat(song_bars[5:-2]))
        song_6bars_list.append(concat(song_bars[5:-2]))
    elif 1 < change_num <= 2:
        song_6bars_list.append(concat(song_bars[5:5 + 6]))
        song_6bars_list.append(concat(song_bars[5 + 6:-2]))
    elif change_num >= 3:
        for i in range(change_num - 2):
            song_6bars_list.append(concat(song_bars[5 + i * 6:5 + (i + 1) * 6]))
        song_6bars_list.append(concat(song_bars[5 + (change_num - 2) * 6:-2]))
    return song_6bars_list


def __fAddQIN_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(GUZHENG, ERHU)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []

    song1 = song
    song2 = song
    if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
        song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        song1 = __fAdjustScaleNote__(song1)
    else:
        song1 = __fAdjustScaleNote__(song1)
    is_in_range = False
    if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
        song2 = song2.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, ERHU)
    else:
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, ERHU)
    if not is_in_range:
        if play_way == REPEAT_PLAY:
            song1 = __fMusicDevelop__(song1)
        music_track.append(song1)
        channel_list.append(2)
        # 添加古筝弹奏手法
        song_long, song_longi = __fAddTechnique1__(song1)  # 古筝长音
        song_hua, song_huai = __fAddTechnique2__(song1, song_longi)  # 古筝滑音
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(4)
        start_time4 = song1[:song_longi[0]].bars()
        start_time5 = song1[:song_huai[0]].bars()
        start_list.append(0)
        start_list.append(start_time4)
        start_list.append(start_time5)
        # 构造乐曲类型
        song_add_QIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
        return song_add_QIN0

    if play_way == UNISON_PLAY:
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUZHENG_LUN:
            note_pitch = np.random.choice([i for i in range(60, 105)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 2000))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(5)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(5)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(60, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        if if_add_lun == GUZHENG_LUN:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 添加古筝弹奏手法
        song_long, song_longi = __fAddTechnique1__(song1)  # 古筝长音
        song_hua, song_huai = __fAddTechnique2__(song1, song_longi)  # 古筝滑音
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(4)
        start_time4 = song1[:song_longi[0]].bars() + start_time1
        start_time5 = song1[:song_huai[0]].bars() + start_time1
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_QIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_QIN0
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUZHENG_LUN:
            note_pitch = np.random.choice([i for i in range(60, 105)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([GUZHENG, ERHU, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUZHENG:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(3)  # 泛音音色
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == GUZHENG_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            # 添加演奏手法
            song_long, song_longi = __fAddTechnique1__(song1)  # 古筝长音
            song_hua, song_huai = __fAddTechnique2__(song1, song_longi)  # 古筝滑音
            music_track.append(song_long)
            music_track.append(song_hua)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_QIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_QIN0
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([GUZHENG, ERHU, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUZHENG:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(3)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 1:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([GUZHENG, ERHU, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice2 == GUZHENG:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(3)
            elif instrument_choice2 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(5)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(5)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == GUZHENG_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            # 添加演奏手法
            song_long, song_longi = __fAddTechnique1__(song1)  # 古筝长音
            song_hua, song_huai = __fAddTechnique2__(song1, song_longi)  # 古筝滑音
            music_track.append(song_long)
            music_track.append(song_hua)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_QIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_QIN0


def __fAddQIN_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(GUZHENG, XIAO)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []

    song1 = song
    song2 = song
    if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
        song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        song1 = __fAdjustScaleNote__(song1)
    else:
        song1 = __fAdjustScaleNote__(song1)
    is_in_range = False
    if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
        song2 = song2.reset_pitch(INSTRUMENTS_PITCH[XIAO])
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XIAO)
    else:
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XIAO)
    if not is_in_range:
        if play_way == REPEAT_PLAY:
            song1 = __fMusicDevelop__(song1)
        music_track.append(song1)
        channel_list.append(2)
        # 添加古筝弹奏手法
        song_long, song_longi = __fAddTechnique1__(song1)  # 古筝长音
        song_hua, song_huai = __fAddTechnique2__(song1, song_longi)  # 古筝滑音
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(4)
        start_time4 = song1[:song_longi[0]].bars()
        start_time5 = song1[:song_huai[0]].bars()
        start_list.append(0)
        start_list.append(start_time4)
        start_list.append(start_time5)
        # 构造乐曲类型
        song_add_QIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
        return song_add_QIN1

    if play_way == UNISON_PLAY:
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUZHENG_LUN:
            note_pitch = np.random.choice([i for i in range(60, 105)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 2000))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(6)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(6)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(60, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        if if_add_lun == GUZHENG_LUN:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 添加古筝弹奏手法
        song_long, song_longi = __fAddTechnique1__(song1)
        song_hua, song_huai = __fAddTechnique2__(song1, song_longi)
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(4)
        start_time4 = song1[:song_longi[0]].bars() + start_time1
        start_time5 = song1[:song_huai[0]].bars() + start_time1
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_QIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_QIN1
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUZHENG_LUN:
            note_pitch = np.random.choice([i for i in range(60, 105)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([GUZHENG, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUZHENG:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(3)  # 泛音音色
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(6)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(6)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == GUZHENG_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            # 添加古筝弹奏手法
            song_long, song_longi = __fAddTechnique1__(song1)
            song_hua, song_huai = __fAddTechnique2__(song1, song_longi)
            music_track.append(song_long)
            music_track.append(song_hua)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_QIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_QIN1
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([GUZHENG, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUZHENG:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(3)
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(6)
            elif instrument_choice1 == 1:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(6)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([GUZHENG, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice2 == GUZHENG:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(3)
            elif instrument_choice2 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(6)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(6)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == GUZHENG_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            # 添加古筝弹奏手法
            song_long, song_longi = __fAddTechnique1__(song1)
            song_hua, song_huai = __fAddTechnique2__(song1, song_longi)
            music_track.append(song_long)
            music_track.append(song_hua)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_QIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_QIN1


def __fAddQIN_2__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(GUZHENG, XUN)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []

    song1 = song
    song2 = song
    if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
        song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        song1 = __fAdjustScaleNote__(song1)
    else:
        song1 = __fAdjustScaleNote__(song1)
    is_in_range = False
    if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
        song2 = song2.reset_pitch(INSTRUMENTS_PITCH[XUN])
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XUN)
    else:
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XUN)
    if not is_in_range:
        if play_way == REPEAT_PLAY:
            song1 = __fMusicDevelop__(song1)
        music_track.append(song1)
        channel_list.append(2)
        # 添加古筝弹奏手法
        song_long, song_longi = __fAddTechnique1__(song1)  # 古筝长音
        song_hua, song_huai = __fAddTechnique2__(song1, song_longi)  # 古筝滑音
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(4)
        start_time4 = song1[:song_longi[0]].bars()
        start_time5 = song1[:song_huai[0]].bars()
        start_list.append(0)
        start_list.append(start_time4)
        start_list.append(start_time5)
        # 构造乐曲类型
        song_add_QIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
        return song_add_QIN2

    if play_way == UNISON_PLAY:
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUZHENG_LUN:
            note_pitch = np.random.choice([i for i in range(60, 105)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 2000))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(5)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(5)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(80, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        start_time2 = 0
        if if_add_lun == GUZHENG_LUN:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 添加古筝弹奏手法
        song_longZ, song_longZi = __fAddTechnique1__(song1)  # 古筝长音
        song_longX, song_longXi = __fAddTechnique1__(song2)  # 埙长音
        song_hua, song_huai = __fAddTechnique2__(song1, song_longZi)  # 古筝滑音
        music_track.append(song_longZ)
        music_track.append(song_longX)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(6)
        channel_list.append(4)
        start_time4 = song1[:song_longZi[0]].bars() + start_time1
        start_time5 = song2[:song_longXi[0]].bars() + start_time2
        start_time6 = song1[:song_huai[0]].bars() + start_time1
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_QIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_QIN2
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUZHENG_LUN:
            note_pitch = np.random.choice([i for i in range(60, 105)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([GUZHENG, XUN, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUZHENG:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(3)  # 泛音音色
            elif instrument_choice1 == XUN:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == GUZHENG_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_longZ, song_longZi = __fAddTechnique1__(song1)  # 古筝长音
            song_hua, song_huai = __fAddTechnique2__(song1, song_longZi)  # 古筝滑音
            music_track.append(song_longZ)
            music_track.append(song_hua)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longZi[0]].bars() + start_time1
            start_time5 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_QIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_QIN2
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([GUZHENG, XUN, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUZHENG:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(3)
            elif instrument_choice1 == XUN:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 1:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([GUZHENG, XUN, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice2 == GUZHENG:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(3)
            elif instrument_choice2 == XUN:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(5)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(5)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == GUZHENG_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_longZ, song_longZi = __fAddTechnique1__(song1)  # 古筝长音
            song_hua, song_huai = __fAddTechnique2__(song1, song_longZi)  # 古筝滑音
            music_track.append(song_longZ)
            music_track.append(song_hua)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longZi[0]].bars() + start_time1
            start_time5 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_QIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_QIN2


def __fAddHAN_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(DIZI, YANGQIN, ERHU)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song3 = song3.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(6)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(6)
        # 设置音量
        song_2_vol = volume(60, mode='value')
        song_3_vol = volume(127, mode='value')
        song_4_vol = volume(80, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time2 = 0
        if if_add_lun == DIZI_ART:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        # 添加扬琴弹奏手法
        song_longY, song_longiY = __fAddTechnique1__(song2)  # 扬琴长音
        song_huaE, song_huaiE = __fAddTechnique2__(song3)  # 二胡滑音
        music_track.append(song_longY)
        music_track.append(song_huaE)
        channel_list.append(5)
        channel_list.append(7)
        start_time4 = song2[:song_longiY[0]].bars() + start_time2
        start_time5 = song3[:song_huaiE[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_HAN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_HAN1
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([DIZI, YANGQIN, ERHU], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == DIZI:
                song11 = song_6bars_list[0].reset_pitch('G4')
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(2)
            elif instrument_choice1 == YANGQIN:
                if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(3)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(6)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_add_HAN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN0
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([DIZI, YANGQIN, ERHU], p=[0.1, 0.5, 0.4])
            if instrument_choice1 == DIZI:
                # 原音+泛音
                song11 = song_6bars_list[0].reset_pitch('G4')
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(2)
            elif instrument_choice1 == YANGQIN:
                if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(3)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(6)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([DIZI, YANGQIN, ERHU], p=[0.1, 0.5, 0.4])
            if instrument_choice2 == DIZI:
                song12 = song_6bars_list[1].reset_pitch('G4')
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(2)
            elif instrument_choice2 == YANGQIN:
                if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(3)
            elif instrument_choice2 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(6)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_add_HAN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN0


def __fAddHAN_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(DIZI, ERHU, PIPA)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song3 = song3.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 2000))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(6)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(6)
        # 设置音量
        song_2_vol = volume(80, mode='value')
        song_3_vol = volume(80, mode='value')
        song_4_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time2 = 0
        if if_add_lun == DIZI_ART:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        # 添加琵琶弹奏手法
        song_long, song_longi = __fAddTechnique1__(song3)  # 琵琶长音
        song_hua, song_huai = __fAddTechnique2__(song2)  # 二胡滑音
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(7)
        channel_list.append(4)
        start_time4 = song3[:song_longi[0]].bars() + start_time2
        start_time5 = song2[:song_huai[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_HAN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_HAN1
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([DIZI, PIPA, ERHU], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == DIZI:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(9)  # 采用琵琶的泛音
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(6)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(3)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_add_HAN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN1
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([DIZI, PIPA, ERHU], p=[0.1, 0.5, 0.4])
            if instrument_choice1 == DIZI:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(9)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(6)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(3)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([DIZI, PIPA, ERHU], p=[0.1, 0.5, 0.4])
            if instrument_choice2 == DIZI:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(9)
            elif instrument_choice2 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(6)
            elif instrument_choice2 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(3)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_add_HAN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN1


def __fAddHAN_2__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(DIZI, ERHU, GUZHENG)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
            song3 = song3.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 2000))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(6)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(6)
        # 设置音量
        song_2_vol = volume(80, mode='value')
        song_3_vol = volume(80, mode='value')
        song_4_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time2 = 0
        if if_add_lun == DIZI_ART:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        # 添加琵琶弹奏手法
        song_long, song_longi = __fAddTechnique1__(song3)  # 古筝长音
        song_huaZ, song_huaZi = __fAddTechnique2__(song3, song_longi)  # 古筝滑音
        song_huaE, song_husEi = __fAddTechnique2__(song2)  # 二胡滑音
        music_track.append(song_long)
        music_track.append(song_huaZ)
        music_track.append(song_huaE)
        channel_list.append(7)
        channel_list.append(8)
        channel_list.append(4)
        start_time4 = song3[:song_longi[0]].bars() + start_time2
        start_time5 = song3[:song_huaZi[0]].bars() + start_time2
        start_time6 = song2[:song_husEi[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_HAN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_HAN2
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([DIZI, GUZHENG, ERHU], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == DIZI:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)  # 采用古筝的泛音
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(6)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(3)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_add_HAN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN2
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([DIZI, GUZHENG, ERHU], p=[0.1, 0.5, 0.4])
            if instrument_choice1 == DIZI:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(6)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(3)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([DIZI, GUZHENG, ERHU], p=[0.1, 0.5, 0.4])
            if instrument_choice2 == DIZI:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(6)
            elif instrument_choice2 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(6)
            elif instrument_choice2 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(3)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_add_HAN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN2


def __fAddHAN_3__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(DIZI, XIAO)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[XIAO])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 2000))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(4)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(4)
        # 设置音量
        song_2_vol = volume(80, mode='value')
        song_3_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        if if_add_lun == DIZI_ART:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 构造乐曲类型
        song_add_HAN3 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_HAN3
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == DIZI_ART:
            note_pitch = np.random.choice([i for i in range(40, 89)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([DIZI, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == DIZI:
                song11 = song_6bars_list[0].reset_pitch('G4')
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(2)
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_add_HAN3 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN3
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([DIZI, XIAO, 11], p=[0.1, 0.5, 0.4])
            if instrument_choice1 == DIZI:
                # 原音+泛音
                song11 = song_6bars_list[0].reset_pitch('G4')
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(2)
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([DIZI, XIAO, 11], p=[0.1, 0.5, 0.4])
            if instrument_choice2 == DIZI:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(2)
            elif instrument_choice2 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(4)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(4)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[DIZI])
            song1.notes = [set_effect(i, fade(20, 20)) for i in song1.notes]
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == DIZI_ART:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_add_HAN3 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_HAN3


def __fAddJIN_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(GUQIN, GUZHENG, DIZI)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
            song1 = song.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
        if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
            song2 = song.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song3 = song.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUQIN_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 66)])
            song_lun = chord([degree_to_note(note_pitch)], duration=3, interval=3)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(3)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(8)
            channel_list.append(12)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(8)
            channel_list.append(12)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(127, mode='value')
        song_4_vol = volume(40, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        start_time2 = 0
        if if_add_lun == GUQIN_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()  # song23_start_num1是用song1算的，这里必须是song1
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        # 添加琵琶弹奏手法
        song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
        song_long, song_longi = __fAddTechnique1__(song2)  # 古筝长音
        song_huaZ, song_huaZi = __fAddTechnique2__(song2, song_longi)  # 古筝滑音
        music_track.append(song_huaQ)
        music_track.append(song_long)
        music_track.append(song_huaZ)
        channel_list.append(5)
        channel_list.append(9)
        channel_list.append(10)
        start_time4 = song1[:song_huaQi[0]].bars() + start_time1
        start_time5 = song2[:song_longi[0]].bars() + start_time2
        start_time6 = song2[:song_huaZi[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_JIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_JIN0
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUQIN_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 66)])
            song_lun = chord([degree_to_note(note_pitch)], duration=3, interval=3)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([GUQIN, GUZHENG, DIZI], p=[0.4, 0.4, 0.2])
            if instrument_choice1 == GUQIN:
                song11 = song_6bars_list[0]
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song11)
                channel_list.append(6)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(8)
            elif instrument_choice1 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song3 = song_6bars_list[0]
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(12)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
            music_track.append(song1)
            channel_list.append(3)
            start_time1 = 0
            if if_add_lun == GUQIN_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
            music_track.append(song_huaQ)
            channel_list.append(5)
            start_time4 = song1[:song_huaQi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_JIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_JIN0
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([GUQIN, GUZHENG, DIZI], p=[0.4, 0.4, 0.2])
            if instrument_choice1 == GUQIN:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(8)
            elif instrument_choice1 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song3 = song_6bars_list[0]
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(12)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([GUQIN, GUZHENG, DIZI], p=[0.4, 0.4, 0.2])
            if instrument_choice2 == GUQIN:
                song12 = song_6bars_list[1]
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(6)
            elif instrument_choice2 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song4 = song_6bars_list[1]
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(8)
            elif instrument_choice2 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song5 = song_6bars_list[1]
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(12)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
            music_track.append(song1)
            channel_list.append(3)
            start_time1 = 0
            if if_add_lun == GUQIN_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
            music_track.append(song_huaQ)
            channel_list.append(5)
            start_time4 = song1[:song_huaQi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_JIN0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_JIN0


def __fAddJIN_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(GUQIN, XUN)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []

    song1 = song
    song2 = song
    if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
        song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        song1 = __fAdjustScaleNote__(song1)
    else:
        song1 = __fAdjustScaleNote__(song1)
    is_in_range = False
    if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
        song2 = song2.reset_pitch(INSTRUMENTS_PITCH[XUN])
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XUN)
    else:
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XUN)
    if not is_in_range:
        if play_way == REPEAT_PLAY:
            song1 = __fMusicDevelop__(song1)
        music_track.append(song1)
        channel_list.append(2)
        # 添加古琴弹奏手法
        song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
        music_track.append(song_huaQ)
        channel_list.append(5)
        start_time4 = song1[:song_huaQi[0]].bars()
        start_list.append(0)
        start_list.append(start_time4)
        # 构造乐曲类型
        song_add_JIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
        return song_add_JIN1

    if play_way == UNISON_PLAY:
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUQIN_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 66)])
            song_lun = chord([degree_to_note(note_pitch)], duration=3, interval=3)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(3)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(7)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(7)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        start_time2 = 0
        if if_add_lun == GUQIN_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 添加古琴弹奏手法
        song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
        song_long, song_longi = __fAddTechnique1__(song2)  # 埙长音
        music_track.append(song_huaQ)
        music_track.append(song_long)
        channel_list.append(5)
        channel_list.append(8)
        start_time4 = song1[:song_huaQi[0]].bars() + start_time1
        start_time5 = song2[:song_longi[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_JIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_JIN1
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUQIN_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 66)])
            song_lun = chord([degree_to_note(note_pitch)], duration=3, interval=3)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([GUQIN, XUN, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUQIN:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)  # 泛音音色
            elif instrument_choice1 == XUN:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(7)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(7)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
            music_track.append(song1)
            channel_list.append(3)
            start_time1 = 0
            if if_add_lun == GUQIN_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
            music_track.append(song_huaQ)
            channel_list.append(5)
            start_time4 = song1[:song_huaQi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_JIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_JIN1
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([GUQIN, XUN, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUQIN:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)
            elif instrument_choice1 == XUN:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(7)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(7)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([GUQIN, XUN, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice2 == GUQIN:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(6)
            elif instrument_choice2 == XUN:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(7)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XUN][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XUN])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(7)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
            music_track.append(song1)
            channel_list.append(3)
            start_time1 = 0
            if if_add_lun == GUQIN_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
            music_track.append(song_huaQ)
            channel_list.append(5)
            start_time4 = song1[:song_huaQi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_JIN1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_JIN1


def __fAddJIN_2__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(GUQIN, XIAO)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []

    song1 = song
    song2 = song
    if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
        song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        song1 = __fAdjustScaleNote__(song1)
    else:
        song1 = __fAdjustScaleNote__(song1)
    is_in_range = False
    if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
        song2 = song2.reset_pitch(INSTRUMENTS_PITCH[XIAO])
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XIAO)
    else:
        song2 = __fAdjustScaleNote__(song2)
        is_in_range = __fJudgeRangeNote__(song2, XIAO)
    if not is_in_range:
        if play_way == REPEAT_PLAY:
            song1 = __fMusicDevelop__(song1)
        music_track.append(song1)
        channel_list.append(2)
        # 添加古琴弹奏手法
        song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
        music_track.append(song_huaQ)
        channel_list.append(5)
        start_time4 = song1[:song_huaQi[0]].bars()
        start_list.append(0)
        start_list.append(start_time4)
        # 构造乐曲类型
        song_add_JIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
        return song_add_JIN2

    if play_way == UNISON_PLAY:
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUQIN_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 66)])
            song_lun = chord([degree_to_note(note_pitch)], duration=3, interval=3)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(3)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(8)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(8)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(100, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        if if_add_lun == GUQIN_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
        music_track.append(song_huaQ)
        channel_list.append(5)
        start_time4 = song1[:song_huaQi[0]].bars() + start_time1
        start_list.append(start_time4)
        volume_list.append(song_2_vol)
        song_add_JIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_JIN2
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == GUQIN_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 66)])
            song_lun = chord([degree_to_note(note_pitch)], duration=3, interval=3)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([GUQIN, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUQIN:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)  # 泛音音色
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(8)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(8)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
            music_track.append(song1)
            channel_list.append(3)
            start_time1 = 0
            if if_add_lun == GUQIN_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
            music_track.append(song_huaQ)
            channel_list.append(5)
            start_time4 = song1[:song_huaQi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_JIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_JIN2
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([GUQIN, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice1 == GUQIN:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(8)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(8)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([GUQIN, XIAO, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice2 == GUQIN:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(6)
            elif instrument_choice2 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(8)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(8)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[GUQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[GUQIN])
            music_track.append(song1)
            channel_list.append(3)
            start_time1 = 0
            if if_add_lun == GUQIN_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_huaQ, song_huaQi = __fAddTechnique2__(song1)  # 古琴滑音
            music_track.append(song_huaQ)
            channel_list.append(5)
            start_time4 = song1[:song_huaQi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_JIN2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_JIN2


def __fAddTANG1_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(PIPA, DIZI)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == PIPA_LOOPS:
            note_pitch = np.random.choice([i for i in range(36, 70)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(7)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(7)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(50, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        if if_add_lun == PIPA_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 添加琵琶弹奏手法
        song_long, song_longi = __fAddTechnique1__(song1)  # 琵琶长音
        song_dlun, song_dluni = __fAddTechnique3__(song1, song_longi)  # 琵琶短轮指
        music_track.append(song_long)
        music_track.append(song_dlun)
        channel_list.append(3)
        channel_list.append(4)
        start_time4 = song1[:song_longi[0]].bars() + start_time1
        start_time5 = song1[:song_dluni[0]].bars() + start_time1
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_TANG10 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_TANG10
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == PIPA_LOOPS:
            note_pitch = np.random.choice([i for i in range(36, 70)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([PIPA, DIZI, 11], p=[0.5, 0.2, 0.3])
            if instrument_choice1 == PIPA:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(5)
            elif instrument_choice1 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(7)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(7)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[PIPA])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == PIPA_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_long, song_longi = __fAddTechnique1__(song1)  # 琵琶长音
            song_dlun, song_dluni = __fAddTechnique3__(song1, song_longi)  # 琵琶短轮指
            music_track.append(song_long)
            music_track.append(song_dlun)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_dluni[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_TANG10 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG10
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([PIPA, DIZI, 11], p=[0.5, 0.2, 0.3])
            if instrument_choice1 == PIPA:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(5)
            elif instrument_choice1 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(7)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(7)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([PIPA, DIZI, 11], p=[0.3, 0.4, 0.3])
            if instrument_choice2 == PIPA:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(5)
            elif instrument_choice2 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(7)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(7)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[PIPA])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == PIPA_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_long, song_longi = __fAddTechnique1__(song1)  # 琵琶长音
            song_dlun, song_dluni = __fAddTechnique3__(song1, song_longi)  # 琵琶短轮指
            music_track.append(song_long)
            music_track.append(song_dlun)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_dluni[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_TANG10 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG10


def __fAddTANG1_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(PIPA, GUZHENG, XIAO)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
            song3 = song3.reset_pitch(INSTRUMENTS_PITCH[XIAO])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == PIPA_LOOPS:
            note_pitch = np.random.choice([i for i in range(36, 70)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(7)
            channel_list.append(11)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(7)
            channel_list.append(11)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(110, mode='value')
        song_4_vol = volume(100, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        start_time2 = 0
        if if_add_lun == PIPA_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        song_longP, song_longPi = __fAddTechnique1__(song1)  # 琵琶长音
        song_dlun, song_dluni = __fAddTechnique3__(song1, song_longPi)  # 琵琶短轮指
        song_longZ, song_longZi = __fAddTechnique1__(song2)  # 古筝长音
        song_hua, song_huai = __fAddTechnique2__(song2, song_longZi)  # 古筝滑音
        music_track.append(song_longP)
        music_track.append(song_dlun)
        music_track.append(song_longZ)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(4)
        channel_list.append(8)
        channel_list.append(9)
        start_time4 = song1[:song_longPi[0]].bars() + start_time1
        start_time5 = song1[:song_dluni[0]].bars() + start_time1
        start_time6 = song2[:song_longZi[0]].bars() + start_time2
        start_time7 = song2[:song_huai[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        start_list.append(start_time7)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_TANG11 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_TANG11
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == PIPA_LOOPS:
            note_pitch = np.random.choice([i for i in range(36, 70)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([PIPA, GUZHENG, XIAO], p=[0.1, 0.5, 0.4])
            if instrument_choice1 == PIPA:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(5)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(7)
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(11)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[PIPA])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == PIPA_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_long, song_longi = __fAddTechnique1__(song1)  # 琵琶长音
            song_dlun, song_dluni = __fAddTechnique3__(song1, song_longi)  # 琵琶短轮指
            music_track.append(song_long)
            music_track.append(song_dlun)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_dluni[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_TANG11 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG11
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([PIPA, GUZHENG, XIAO], p=[0.1, 0.5, 0.4])
            if instrument_choice1 == PIPA:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(5)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(7)
            elif instrument_choice1 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(11)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([PIPA, GUZHENG, XIAO], p=[0.1, 0.5, 0.4])
            if instrument_choice2 == PIPA:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(5)
            elif instrument_choice2 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(7)
            elif instrument_choice2 == XIAO:
                if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[XIAO])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(11)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[PIPA])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == PIPA_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_long, song_longi = __fAddTechnique1__(song1)  # 琵琶长音
            song_dlun, song_dluni = __fAddTechnique3__(song1, song_longi)  # 琵琶短轮指
            music_track.append(song_long)
            music_track.append(song_dlun)
            channel_list.append(3)
            channel_list.append(4)
            start_time4 = song1[:song_longi[0]].bars() + start_time1
            start_time5 = song1[:song_dluni[0]].bars() + start_time1
            start_list.append(start_time4)
            start_list.append(start_time5)
            song_add_TANG11 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG11


def __fAddTANG2_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(XIAO, ERHU, PIPA)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[XIAO])
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song3 = song3.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == XIAO_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 52)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(7)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(3)
            channel_list.append(7)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(100, mode='value')
        song_4_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time2 = 0
        if if_add_lun == XIAO_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        # 添加琵琶弹奏手法
        song_hua, song_huai = __fAddTechnique2__(song2)  # 二胡滑音
        song_long, song_longi = __fAddTechnique1__(song3)  # 琵琶长音
        song_dlun, song_dluni = __fAddTechnique3__(song3, song_longi)  # 琵琶短轮指
        music_track.append(song_hua)
        music_track.append(song_long)
        music_track.append(song_dlun)
        channel_list.append(5)
        channel_list.append(7)
        channel_list.append(8)
        start_time4 = song2[:song_huai[0]].bars() + start_time2
        start_time5 = song3[:song_longi[0]].bars() + start_time2
        start_time6 = song3[:song_dluni[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_TANG20 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_TANG20
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == XIAO_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 52)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([XIAO, ERHU, PIPA], p=[0.4, 0.2, 0.4])
            if instrument_choice1 == XIAO:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)  # 与琵琶合奏
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(3)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(6)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[XIAO])
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == XIAO_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_add_TANG20 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG20
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([XIAO, ERHU, PIPA], p=[0.4, 0.2, 0.4])
            if instrument_choice1 == XIAO:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(6)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(3)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(6)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([XIAO, ERHU, PIPA], p=[0.4, 0.2, 0.4])
            if instrument_choice2 == XIAO:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(6)
            elif instrument_choice2 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(3)
            elif instrument_choice2 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(6)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[XIAO])
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == XIAO_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_add_TANG20 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG20


def __fAddTANG2_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(XIAO, GUZHENG, PIPA)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        song3 = song
        if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[XIAO])
        if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song3 = song3.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == XIAO_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 52)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            song3 = song3[song23_start_num1:]
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(4)
            channel_list.append(9)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song3 = song3[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            song3 = set_effect(song3, fade_out(2000))
            music_track.append(song2)
            music_track.append(song3)
            channel_list.append(4)
            channel_list.append(9)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(100, mode='value')
        song_4_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time2 = 0
        if if_add_lun == XIAO_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol, song_4_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2, start_time2]
            volume_list = [song_2_vol, song_3_vol, song_4_vol]
        song_longZ, song_longZi = __fAddTechnique1__(song2)  # 古筝长音
        song_hua, song_huai = __fAddTechnique2__(song2, song_longZi)  # 古筝滑音
        song_longP, song_longPi = __fAddTechnique1__(song3)  # 琵琶长音
        song_dlun, song_dluni = __fAddTechnique3__(song3, song_longPi)  # 琵琶短轮指
        music_track.append(song_longZ)
        music_track.append(song_hua)
        music_track.append(song_longP)
        music_track.append(song_dlun)
        channel_list.append(5)
        channel_list.append(6)
        channel_list.append(9)
        channel_list.append(10)
        start_time4 = song2[:song_longZi[0]].bars() + start_time2
        start_time5 = song2[:song_huai[0]].bars() + start_time2
        start_time6 = song3[:song_longPi[0]].bars() + start_time2
        start_time7 = song3[:song_dluni[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        start_list.append(start_time7)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_TANG21 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_TANG21
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == XIAO_LOOPS:
            note_pitch = np.random.choice([i for i in range(45, 52)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([XIAO, GUZHENG, PIPA], p=[0.4, 0.3, 0.3])
            if instrument_choice1 == XIAO:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(4)  # 与古筝合奏
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(8)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[XIAO])
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == XIAO_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_add_TANG21 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG21
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([XIAO, GUZHENG, PIPA], p=[0.4, 0.3, 0.3])
            if instrument_choice1 == XIAO:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(4)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song3)
                channel_list.append(8)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([XIAO, GUZHENG, PIPA], p=[0.4, 0.3, 0.3])
            if instrument_choice2 == XIAO:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(4)
            elif instrument_choice2 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(4)
            elif instrument_choice2 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(8)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[XIAO][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[XIAO])
            music_track.append(song1)
            channel_list.append(2)
            if if_add_lun == XIAO_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_add_TANG21 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_TANG21


def __fAddSONG_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(ERHU, PIPA)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        music_track.append(song1)
        channel_list.append(1)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(4)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(4)
        # 设置音量
        song_2_vol = volume(110, mode='value')
        song_3_vol = volume(127, mode='value')
        start_time2 = song1[:song23_start_num1].bars()
        start_list = [0, start_time2]
        volume_list = [song_2_vol, song_3_vol]
        song_hua, song_huai = __fAddTechnique2__(song1)  # 二胡滑音
        song_long, song_longi = __fAddTechnique1__(song2)  # 琵琶长音
        song_dlun, song_dluni = __fAddTechnique3__(song2, song_longi)  # 琵琶短轮指
        music_track.append(song_hua)
        music_track.append(song_long)
        music_track.append(song_dlun)
        channel_list.append(2)
        channel_list.append(5)
        channel_list.append(6)
        start_time4 = song1[:song_huai[0]].bars()
        start_time5 = song2[:song_longi[0]].bars() + start_time2
        start_time6 = song2[:song_dluni[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_SONG0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_SONG0
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([ERHU, PIPA, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == ERHU:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(7)  # 与古筝合奏
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[ERHU])
            music_track.append(song1)
            channel_list.append(1)
            start_time2 = song1[:start_time1_index].bars()
            start_list = [start_time2, 0]
            song_hua, song_huai = __fAddTechnique2__(song1)  # 二胡滑音
            music_track.append(song_hua)
            channel_list.append(2)
            start_time4 = song1[:song_huai[0]].bars()
            start_list.append(start_time4)
            song_add_SONG0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_SONG0
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([ERHU, PIPA, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == ERHU:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(7)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([ERHU, PIPA, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice2 == ERHU:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(7)
            elif instrument_choice2 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(4)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(4)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[ERHU])
            music_track.append(song1)
            channel_list.append(1)
            start_time2 = song1[:start_time_index1].bars()
            start_time3 = song1[:start_time_index2].bars()
            start_list = [start_time2, start_time3, 0]
            song_hua, song_huai = __fAddTechnique2__(song1)  # 二胡滑音
            music_track.append(song_hua)
            channel_list.append(2)
            start_time4 = song1[:song_huai[0]].bars()
            start_list.append(start_time4)
            song_add_SONG0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_SONG0


def __fAddSONG_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(ERHU, GUZHENG)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
        music_track.append(song1)
        channel_list.append(1)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(4)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(4)
        # 设置音量
        song_2_vol = volume(110, mode='value')
        song_3_vol = volume(127, mode='value')
        start_time2 = song1[:song23_start_num1].bars()
        start_list = [0, start_time2]
        volume_list = [song_2_vol, song_3_vol]
        song_huaE, song_huaEi = __fAddTechnique2__(song1)  # 二胡滑音
        song_long, song_longi = __fAddTechnique1__(song2)  # 古筝长音
        song_huaZ, song_huaZi = __fAddTechnique2__(song2, song_longi)  # 古筝滑音
        music_track.append(song_huaE)
        music_track.append(song_long)
        music_track.append(song_huaZ)
        channel_list.append(2)
        channel_list.append(5)
        channel_list.append(6)
        start_time4 = song1[:song_huaEi[0]].bars()
        start_time5 = song2[:song_longi[0]].bars() + start_time2
        start_time6 = song2[:song_huaZi[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_SONG1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_SONG1
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([ERHU, GUZHENG, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == ERHU:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(5)  # 与古筝合奏
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[ERHU])
            music_track.append(song1)
            channel_list.append(1)
            start_time2 = song1[:start_time1_index].bars()
            start_list = [start_time2, 0]
            song_hua, song_huai = __fAddTechnique2__(song1)  # 二胡滑音
            music_track.append(song_hua)
            channel_list.append(2)
            start_time4 = song1[:song_huai[0]].bars()
            start_list.append(start_time4)
            song_add_SONG1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_SONG1
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([ERHU, GUZHENG, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == ERHU:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(5)
            elif instrument_choice1 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([ERHU, GUZHENG, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice2 == ERHU:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(5)
            elif instrument_choice2 == GUZHENG:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(4)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[GUZHENG][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[GUZHENG])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(4)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[ERHU])
            music_track.append(song1)
            channel_list.append(1)
            start_time2 = song1[:start_time_index1].bars()
            start_time3 = song1[:start_time_index2].bars()
            start_list = [start_time2, start_time3, 0]
            song_hua, song_huai = __fAddTechnique2__(song1)  # 二胡滑音
            music_track.append(song_hua)
            channel_list.append(2)
            start_time4 = song1[:song_huai[0]].bars()
            start_list.append(start_time4)
            song_add_SONG1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_SONG1


def __fAddMING_0__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(YANGQIN, PIPA)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
        if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[PIPA])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == YANGQIN_LUN:
            note_pitch = np.random.choice([i for i in range(41, 48)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(2)
        music_track.append(song1)
        channel_list.append(1)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(8)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(8)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        start_time2 = 0
        if if_add_lun == YANGQIN_LUN:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        # 添加琵琶弹奏手法
        song_longY, song_longYi = __fAddTechnique1__(song1)  # 扬琴长音
        song_longP, song_longPi = __fAddTechnique1__(song2)  # 琵琶长音
        song_dlun, song_dluni = __fAddTechnique3__(song2, song_longPi)  # 琵琶短轮指
        music_track.append(song_longY)
        music_track.append(song_longP)
        music_track.append(song_dlun)
        channel_list.append(3)
        channel_list.append(6)
        channel_list.append(7)
        start_time4 = song1[:song_longYi[0]].bars() + start_time1
        start_time5 = song2[:song_longPi[0]].bars() + start_time2
        start_time6 = song2[:song_dluni[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        start_list.append(start_time6)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_MING0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_MING0
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == YANGQIN_LUN:
            note_pitch = np.random.choice([i for i in range(41, 48)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(2)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([YANGQIN, PIPA, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == YANGQIN:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(8)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
            music_track.append(song1)
            channel_list.append(1)
            start_time1 = 0
            if if_add_lun == YANGQIN_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_longY, song_longYi = __fAddTechnique1__(song1)  # 扬琴长音
            music_track.append(song_longY)
            channel_list.append(3)
            start_time4 = song1[:song_longYi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_MING0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_MING0
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([YANGQIN, PIPA, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == YANGQIN:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(8)
            elif instrument_choice1 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([YANGQIN, PIPA, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice2 == YANGQIN:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(8)
            elif instrument_choice2 == PIPA:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(5)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[PIPA][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[PIPA])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(5)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
            music_track.append(song1)
            channel_list.append(1)
            start_time1 = 0
            if if_add_lun == YANGQIN_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_longY, song_longYi = __fAddTechnique1__(song1)  # 扬琴长音
            music_track.append(song_longY)
            channel_list.append(3)
            start_time4 = song1[:song_longYi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_MING0 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_MING0


def __fAddMING_1__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(YANGQIN, ERHU)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
        if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[ERHU])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == YANGQIN_LUN:
            note_pitch = np.random.choice([i for i in range(41, 48)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(2)
        music_track.append(song1)
        channel_list.append(1)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(4)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(4)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(127, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        start_time2 = 0
        if if_add_lun == YANGQIN_LUN:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        song_long, song_longi = __fAddTechnique1__(song1)  # 扬琴长音
        song_hua, song_huai = __fAddTechnique1__(song2)  # 二胡滑音
        music_track.append(song_long)
        music_track.append(song_hua)
        channel_list.append(3)
        channel_list.append(5)
        start_time4 = song1[:song_longi[0]].bars() + start_time1
        start_time5 = song2[:song_huai[0]].bars() + start_time2
        start_list.append(start_time4)
        start_list.append(start_time5)
        volume_list.append(song_2_vol)
        volume_list.append(song_2_vol)
        # 构造乐曲类型
        song_add_MING1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_MING1
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == YANGQIN_LUN:
            note_pitch = np.random.choice([i for i in range(41, 48)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(2)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([YANGQIN, ERHU, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == YANGQIN:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(1)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
            music_track.append(song1)
            channel_list.append(1)
            start_time1 = 0
            if if_add_lun == YANGQIN_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_longY, song_longYi = __fAddTechnique1__(song1)  # 扬琴长音
            music_track.append(song_longY)
            channel_list.append(3)
            start_time4 = song1[:song_longYi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_MING1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_MING1
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([YANGQIN, ERHU, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == YANGQIN:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(1)
            elif instrument_choice1 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(4)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(4)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([YANGQIN, ERHU, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice2 == YANGQIN:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(1)
            elif instrument_choice2 == ERHU:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(4)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[ERHU][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[ERHU])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song5)
                channel_list.append(4)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[YANGQIN][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[YANGQIN])
            music_track.append(song1)
            channel_list.append(1)
            start_time1 = 0
            if if_add_lun == YANGQIN_LUN:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_longY, song_longYi = __fAddTechnique1__(song1)  # 扬琴长音
            music_track.append(song_longY)
            channel_list.append(3)
            start_time4 = song1[:song_longYi[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_MING1 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_MING1


def __fAddMING_2__(song, song_main_badu, play_way, song_bpm):
    """乐器组合(SUONA, DIZI)"""
    music_track = []
    channel_list = []
    start_list = []
    volume_list = []
    if play_way == UNISON_PLAY:
        song1 = song
        song2 = song
        if song_main_badu != INSTRUMENTS_PITCH[SUONA][1]:
            song1 = song1.reset_pitch(INSTRUMENTS_PITCH[SUONA])
        if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
            song2 = song2.reset_pitch(INSTRUMENTS_PITCH[DIZI])
        # 轮指|随机是否加入轮指
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == SUONA_LOOPS:
            note_pitch = np.random.choice([i for i in range(55, 69)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        music_track.append(song1)
        channel_list.append(2)
        # 判断其他乐器加入的时间|用音符数量
        song23_start_num1 = len(concat(song1.split_bars()[:5]))
        # 其他乐器出去的时间
        song23_start_num2 = len(concat(song1.split_bars()[:-7]))
        # 判断结尾是否要主乐器独奏收尾
        if_single_end = np.random.choice([0, 1])
        if if_single_end == 0:
            song2 = song2[song23_start_num1:]
            music_track.append(song2)
            channel_list.append(5)
        else:
            song2 = song2[song23_start_num1:song23_start_num2]
            song2 = set_effect(song2, fade_out(2000))
            music_track.append(song2)
            channel_list.append(5)
        # 设置音量
        song_2_vol = volume(127, mode='value')
        song_3_vol = volume(100, mode='value')
        # 若是前面选择加入轮指，这里单独处理每个音轨开始的时间
        start_time1 = 0
        if if_add_lun == SUONA_LOOPS:
            start_time1 = song_lun.bars()
            # 确定其他音轨开始的时间
            start_time2 = start_time1 + song1[:song23_start_num1].bars()
            start_list = [0, start_time1, start_time2]
            song_1_vol = volume(127, mode='value')
            volume_list = [song_1_vol, song_2_vol, song_3_vol]
        else:
            start_time2 = song1[:song23_start_num1].bars()
            start_list = [0, start_time2]
            volume_list = [song_2_vol, song_3_vol]
        song_hua, song_huai = __fAddTechnique2__(song1)  # 唢呐滑音
        music_track.append(song_hua)
        channel_list.append(3)
        start_time4 = song1[:song_huai[0]].bars() + start_time1
        start_list.append(start_time4)
        # 构造乐曲类型
        song_add_MING2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list, volume=volume_list)
        return song_add_MING2
    elif play_way == REPEAT_PLAY:
        song1 = chord([])
        song11 = chord([])
        song2 = chord([])
        song3 = chord([])
        song12 = chord([])
        song4 = chord([])
        song5 = chord([])
        # 起始音
        if_add_lun = np.random.choice([0, 1], p=[0.8, 0.2])
        if if_add_lun == SUONA_LOOPS:
            note_pitch = np.random.choice([i for i in range(55, 69)])
            song_lun = chord([degree_to_note(note_pitch)], duration=4, interval=4)
            song_lun = set_effect(song_lun, fade(100, 500))
            # 添加到序列，待生成乐曲类型
            music_track.append(song_lun)
            channel_list.append(1)
        # 其他音
        song_bars = song.split_bars()
        song_start = concat(song_bars[:5])
        song_end = concat(song_bars[-2:])
        song_6bars_list = __fSplitSong__(song_bars)
        if len(song_6bars_list) <= 2:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time1_index = len(song1)
            # 承&转
            instrument_choice1 = np.random.choice([SUONA, DIZI, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == SUONA:
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song11)
                channel_list.append(2)
            elif instrument_choice1 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            song1 += song_6bars_list[1]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[SUONA][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[SUONA])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == SUONA_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[:start_time1_index].bars()
                start_list = [0, start_time2, start_time1]
            else:
                start_time2 = song1[:start_time1_index].bars()
                start_list = [start_time2, 0]
            song_hua, song_huai = __fAddTechnique2__(song1)  # 唢呐滑音
            music_track.append(song_hua)
            channel_list.append(3)
            start_time4 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_MING2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_MING2
        else:
            # 起
            song1 += song_start
            song1 += song_6bars_list[0]
            start_time_index1 = len(song1)
            # 承&转
            # 中间1
            instrument_choice1 = np.random.choice([SUONA, DIZI, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice1 == SUONA:
                # 原音+泛音
                song11 = song_6bars_list[0]
                song11 = set_effect(song11, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song11)
                channel_list.append(2)
            elif instrument_choice1 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song2 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song2 = song_6bars_list[0]
                song2 = set_effect(song2, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[0].interval))
                music_track.append(song2)
                channel_list.append(5)
            elif instrument_choice1 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song3 = song_6bars_list[0].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song3 = song_6bars_list[0]
                song3 = set_effect(song3, fade(200, 1000))
                song1 += song_6bars_list[0]
                music_track.append(song3)
                channel_list.append(5)
            # 中间2
            song1 += song_6bars_list[1]
            start_time_index2 = len(song1)
            instrument_choice2 = np.random.choice([SUONA, DIZI, 11], p=[0.3, 0.3, 0.4])
            if instrument_choice2 == SUONA:
                song12 = song_6bars_list[1]
                song12 = set_effect(song12, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song12)
                channel_list.append(2)
            elif instrument_choice2 == DIZI:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song4 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song4 = song_6bars_list[1]
                song4 = set_effect(song4, fade(200, 1000))
                song1 = song1.rest(sum(song_6bars_list[1].interval))
                music_track.append(song4)
                channel_list.append(5)
            elif instrument_choice2 == 11:
                if song_main_badu != INSTRUMENTS_PITCH[DIZI][1]:
                    song5 = song_6bars_list[1].reset_pitch(INSTRUMENTS_PITCH[DIZI])
                else:
                    song5 = song_6bars_list[1]
                song5 = set_effect(song5, fade(200, 1000))
                song1 += song_6bars_list[1]
                music_track.append(song5)
                channel_list.append(5)
            # 加上中间剩余部分
            for i in range(2, len(song_6bars_list)):
                song1 += song_6bars_list[i]
            # 合
            song1 += song_start
            song1 += song_end
            if song_main_badu != INSTRUMENTS_PITCH[SUONA][1]:
                song1 = song1.reset_pitch(INSTRUMENTS_PITCH[SUONA])
            music_track.append(song1)
            channel_list.append(2)
            start_time1 = 0
            if if_add_lun == SUONA_LOOPS:
                start_time1 = song_lun.bars()
                # 换音色的开始时刻
                start_time2 = start_time1 + song1[
                                            :start_time_index1].bars()  # 注意这里的song1，start_time_index1是根据song1计算的，所以必须是song1
                start_time3 = start_time1 + song1[:start_time_index2].bars()
                start_list = [0, start_time2, start_time3, start_time1]
            else:
                start_time2 = song1[:start_time_index1].bars()
                start_time3 = song1[:start_time_index2].bars()
                start_list = [start_time2, start_time3, 0]
            song_hua, song_huai = __fAddTechnique2__(song1)  # 唢呐滑音
            music_track.append(song_hua)
            channel_list.append(3)
            start_time4 = song1[:song_huai[0]].bars() + start_time1
            start_list.append(start_time4)
            song_add_MING2 = piece(music_track, bpm=song_bpm, sampler_channels=channel_list, start_times=start_list)
            return song_add_MING2


def __fAddTimbre__(song, song_bpm, play_way, dynasty, identify):
    """添加音色"""
    channel_num = 0
    channel_source = ['temp']
    instruments_index = np.random.choice([i for i in range(len(DYNASTY_INSTRUMENTS[dynasty]))],
                                         p=DYNASTY_INSTRUMENTS_RATE[dynasty])
    instruments = DYNASTY_INSTRUMENTS[dynasty][instruments_index]
    for i in instruments:
        channel_num += len(INSTRUMENTS_DICT[i])
        channel_source_temp = [t[1] for t in INSTRUMENTS_DICT[i]]
        channel_source.extend(channel_source_temp)
    music_sampler = sampler(channel_num + 1, name='china')
    for i in range(1, channel_num + 1):
        music_sampler.load(i, os.path.join(MUSICSF2_PATH, channel_source[i]))

    song_add_timbre = None
    # 根据主乐器合适的八度重置乐曲八度
    song_pre10_badu = [i.num for i in song[:20]]
    song_main_badu = str(round(sum(song_pre10_badu) / 20))
    if instruments == DYNASTY_INSTRUMENTS[QIN][0]:
        song_add_timbre = __fAddQIN_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[QIN][1]:
        song_add_timbre = __fAddQIN_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[QIN][2]:
        song_add_timbre = __fAddQIN_2__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[HAN][0]:
        song_add_timbre = __fAddHAN_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[HAN][1]:
        song_add_timbre = __fAddHAN_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[HAN][2]:
        song_add_timbre = __fAddHAN_2__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[HAN][3]:
        song_add_timbre = __fAddHAN_3__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[JIN][0]:
        song_add_timbre = __fAddJIN_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[JIN][1]:
        song_add_timbre = __fAddJIN_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[JIN][2]:
        song_add_timbre = __fAddJIN_2__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[TANG1][0]:
        song_add_timbre = __fAddTANG1_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[TANG1][1]:
        song_add_timbre = __fAddTANG1_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[TANG2][0]:
        song_add_timbre = __fAddTANG2_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[TANG2][1]:
        song_add_timbre = __fAddTANG2_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[SONG][0]:
        song_add_timbre = __fAddSONG_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[SONG][1]:
        song_add_timbre = __fAddSONG_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[MING][0]:
        song_add_timbre = __fAddMING_0__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[MING][1]:
        song_add_timbre = __fAddMING_1__(song, song_main_badu, play_way, song_bpm)
    elif instruments == DYNASTY_INSTRUMENTS[MING][2]:
        song_add_timbre = __fAddMING_2__(song, song_main_badu, play_way, song_bpm)

    print(song_add_timbre)
    mid_save_path = os.path.join(TEMP_PATH, identify + FINAL_PATH_SEG + 'result.mid')
    write(song_add_timbre, bpm=song_bpm, name=mid_save_path)
    print('mid写入完毕', mid_save_path)
    mp3_save_path = os.path.join(TEMP_PATH, identify + FINAL_MP3_PATH_SEG, 'result.mp3')
    music_sampler.export(song_add_timbre, mode='mp3', filename=mp3_save_path)
    print('mp3写入完毕', mp3_save_path)


def __int2note__(music_type: str):
    vocabulary_path = os.path.join(VOCABULARY_PATH, music_type[-2:] + '.json')
    with open(vocabulary_path, 'r') as filepath:
        vocabulary = json.load(filepath)
    return dict((index, note) for index, note in enumerate(vocabulary))


def __note2int__(music_type: str):
    vocabulary_path = os.path.join(VOCABULARY_PATH, music_type[-2:] + '.json')
    with open(vocabulary_path, 'r') as filepath:
        vocabulary = json.load(filepath)
    return dict((note, index) for index, note in enumerate(vocabulary))


def __fTrans__(song):
    r"""移调，将调移至C调或A大调"""
    for element in song.recurse():
        if isinstance(element, key21.Key):
            if element.mode == 'major':
                tonic = element.tonic
            else:
                tonic = element.parallel.tonic
            gap = interval21.Interval(tonic, pitch21.Pitch('C'))
            song = song.transpose(gap)
            break
        elif isinstance(element, note21.Note) or \
                isinstance(element, note21.Rest) or \
                isinstance(element, chord21.Chord):
            break
        else:
            continue
    return song


def __fModifyDuration__(d):
    candidate_durations = np.arange(0.25, 4, 0.25)
    diff = []
    for c in candidate_durations:
        diff.append(abs(c - d))
    substitute_note = candidate_durations[diff.index(min(diff))]
    return substitute_note


def __fEncodeData__(input_path: str = None) -> (list, list):
    r"""
    将要续写的文件编码
    :param input_path: 待编码的音乐文件
    :return 编码后的歌曲数据和文件
    """
    res_song = []  # 编码的歌曲数据
    file_path = input_path
    try:
        song = converter21.parse(file_path)
    except Exception('This song can not be parsed.') as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    song = song.parts[0].flat
    song = __fTrans__(song)  # 移调
    for i in song.recurse():
        if isinstance(i, note21.Note):
            nt_drtion = i.quarterLength  # duration
            nt_p = i.pitch.midi  # pitch
        elif isinstance(i, chord21.Chord):
            nt_drtion = i.quarterLength
            nt_p = i.notes[-1].pitch.midi
        elif isinstance(i, note21.Rest):
            nt_drtion = i.quarterLength
            nt_p = 0
        else:
            continue
        if nt_drtion % 0.25 == 0:
            nt_sp = int(nt_drtion / 0.25)
            res_song += [str(nt_p)] + ['-'] * (nt_sp - 1)
        else:
            nt_drtion = __fModifyDuration__(nt_drtion)
            nt_sp = int(nt_drtion / 0.25)
            res_song += [str(nt_p)] + ['-'] * (nt_sp - 1)
    if res_song is None:
        raise Exception('This song can not be transform')
    return res_song


def __fGetSample__(pred: np.array) -> int:
    """
    对LSTM输出的结果向量进行采样
    :vocabulary pred: 模型得出的结果
    :return index: 采样结果的下标
    """
    temperature = TEMPERATURE
    pred = np.log(pred) / temperature
    probas = np.exp(pred) / np.sum(np.exp(pred))
    index = np.random.choice(range(len(probas)), p=probas)  # 采取随机选择
    return index


def __fSaveAsMid__(song: list, out_file_path: str):
    """
    将编码的歌曲转换为mid文件
    :vocabulary song: 已经编码后的歌曲
    :vocabulary out_file_path: mid文件的路径
    """
    mid_nts = []
    pre_element = None
    drtion = 0.0
    ofst = 0.0
    for element in song:
        if element == '*':
            continue
        if element != '-':
            if pre_element is not None:
                if pre_element == '0':
                    new_note = note21.Rest()
                else:
                    new_note = note21.Note(int(pre_element))
                new_note.quarterLength = drtion
                new_note.offset = ofst
                mid_nts.append(new_note)
            ofst += drtion
            pre_element = element
            drtion = 0.25
        else:
            drtion += 0.25
    score_stream = stream21.Stream(mid_nts)
    score_stream.write('mid', fp=out_file_path)


def __fMyLstmModel__(music_type: str):
    weights_path = os.path.join(WEIGHTS_PATH, music_type[-2:] + r'.h5')
    model = Sequential()
    model.add(Input(shape=(SEG_LEN, len(__note2int__(music_type)))))
    model.add(LSTM(units=RNN_SIZE))
    model.add(Dense(units=len(__note2int__(music_type)), activation="softmax"))
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
    model.load_weights(weights_path)
    return model


def __saveMid__(music_type: str, identify: str):
    r"""
    利用LSTM模型，续写对应情绪笔顺生成的音乐，并放在中间文件里面
    :param music_type: 对应音乐小节的片段情绪片段
    :param identify: 用户标识符
    """
    input_file_path = os.path.join(TEMP_PATH, identify + INPUT_PATH_SEG + music_type + '.mid')
    output_file_path = os.path.join(TEMP_PATH, identify + OUTPUT_PATH_SEG + music_type + '.mid')
    model = __fMyLstmModel__(music_type)
    max_nts = MAX_BARS * 16
    seg_len = SEG_LEN

    # 根据对应的码表来编码歌曲
    data = __fEncodeData__(input_file_path)
    song = ['*'] * seg_len + data
    con_music_len = len(data)
    try:
        input_nts = [__note2int__(music_type)[nt] for nt in song[-seg_len:]]
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise e
    output_nt = None
    num_nts = 0
    while num_nts < max_nts:
        one_hot_input = to_categorical(input_nts, num_classes=len(__note2int__(music_type)))
        one_hot_input = one_hot_input[np.newaxis, ...]
        predi = model.predict(one_hot_input)[0]
        nt_i = __fGetSample__(predi)
        output_nt = __int2note__(music_type)[nt_i]
        input_nts = input_nts[1:]
        input_nts.append(nt_i)
        num_nts += 1
        song.append(output_nt)
    __fSaveAsMid__(song[seg_len + con_music_len:], output_file_path)


async def __prepareMid__(identify: str, key_words: list) -> bool:
    r"""用关键词的笔顺生成待续写的mid文件"""
    assert len(key_words) != 0, '没有关键词'
    input_path = os.path.join(TEMP_PATH, identify + INPUT_PATH_SEG)
    # 控制生成音乐的长度
    if len(key_words) >= 5:
        key_words = key_words[0:5]
    try:
        index = 1
        for word in key_words:
            word_notes = __fBishunDecoder__(word[0])
            duration = __fGenerateDuration__(len(word_notes), word[1])
            badu = __fGenerateBadu__(word)
            A = chord([])
            for i in word_notes:
                A.append(i + str(badu))
            A = A.set(duration=duration, interval=duration)
            word_bpm = __fGenerateBpm__(word[1])
            song_name = str(index) + word[1] + '.mid'
            save_path = os.path.join(input_path, song_name)
            write(A, bpm=word_bpm, name=save_path)
            index += 1

    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        return False
    return True


async def __createTempMid__(identify: str) -> bool:
    r"""
    利用LSTM来续写由关键词生成的prepareMid文件
    """
    prepare_mid_path = os.path.join(TEMP_PATH, identify + r'/music/prepare_mid')
    files = os.listdir(prepare_mid_path)
    assert len(files) > 0, '笔顺没有生成文件'
    for file in files:
        try:
            file_name = file.split('.')[0]
            __saveMid__(str(file_name), identify)
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
            continue
    return True


async def __createFinalMid__(identify: str, sentence_emotion: str, dynasty: int) -> bool:
    r"""修饰LSTM生成的音乐并生成最终结果"""
    try:
        temp_mid_path = os.path.join(TEMP_PATH, identify + TEMPMID_PATH_SEG)
        music_scale = __fChoiceScale__(sentence_emotion)
        music_phrase_list = []
        file_names = os.listdir(temp_mid_path)
        for name in file_names:
            file_path = os.path.join(temp_mid_path, name)
            bpm, song, start_time = read(file_path).merge()
            music_phrase_list.append(song.only_notes())
        # 生成起始式
        music_phrase_list_new1 = __fGenStartingForm__(music_phrase_list, music_scale)
        # 生成终止式
        music_phrase_list_new2 = __fGenEndingForm__(music_phrase_list_new1)
        # 调整音乐片段之间的音高
        music_phrase_list_new3 = __fAdjustPitch__(music_phrase_list_new2)
        music_phrase_list_new4 = __fAdjustDurationAndInterval__(music_phrase_list_new3)
        # 整合音乐片段列表为一个和弦
        song = concat(music_phrase_list_new4)
        # 若选择齐奏，则在这里进行mid修饰；选择重奏，则mid不变，在加音色那里进行修饰
        play_way = np.random.choice([UNISON_PLAY, REPEAT_PLAY])
        if play_way == UNISON_PLAY:
            song_new1 = __fMusicDevelop__(song, sentence_emotion)
        else:
            song_new1 = song
        # 判断调式
        my_music_scale = None
        if music_scale == CHAR_MAJOR:
            my_music_scale = S('C major pentatonic')
        elif music_scale == CHAR_MINOR:
            my_music_scale = S('C minor pentatonic')
        song_new2 = song_new1.modulation(S('C major'), my_music_scale)
        # 复查和弦内的音符
        song_new3 = __fAdjustScaleNote__(song_new2, my_music_scale)
        song_new4 = __fAdjustLongDuration__(song_new3)
        song_bpm = __fGenerateBpm__(sentence_emotion)
        __fAddTimbre__(song_new4, song_bpm, play_way, dynasty, identify)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        return False
    return True


if __name__ == '__main__':
    asyncio.run(__createFinalMid__('1651314495889173600', 'pa', JIN))
