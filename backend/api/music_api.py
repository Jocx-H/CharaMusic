#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from model.code import *
from model.music import MusicInfo, TokenInfo
from service.music_service import *

# 构建api路由
router = APIRouter(
    prefix="/music",
    tags=["Music"],
)


@router.get("/get-mid/{identify}", responses={400: {"model": Code400}})
def getMid(identify: str):
    r"""
    只需要输入用户独有的标签，就能下载他独有的mid文件

    example:
    {
        identify: 1650551534844182000
    }
    """
    try:
        result = getMidFile(identify)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    file_response = FileResponse(result, filename='chara_music.mid', media_type='mid')
    file_response.headers['Access-Control-Expose-Headers'] = "Content-Disposition"
    return file_response


@router.get("/get-mp3/{identify}", responses={400: {"model": Code400}})
def getMp3(identify: str):
    r"""
    获取给用户展示的mp3文件

    example:
    {
        identify: 1650551534844182000
    }
    """
    try:
        result = getMp3File(identify)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    file_response = FileResponse(result, filename='chara_music.mp3', media_type='mp3')
    file_response.headers['Access-Control-Expose-Headers'] = "Content-Disposition"
    return file_response


@router.post("/create-music", responses={400: {"model": Code400}})
async def createMusic(music_info: MusicInfo):
    r"""
    生成music_temp.mid和music_temp.mp4文件
    mid文件和mp4文件都生成成功就返回True，否则返回False

    example:
    {
        identify: 1650551534844182000
        sentence_emo_label: 'ha'
        key_tokens: ['开心', '砸']
        section_emo_values: [0.9823723478, 0.23435354]
    }
    """
    assert music_info.sentence_emo_label == 'ha' or music_info.sentence_emo_label == 'sa' or music_info.sentence_emo_label == 'pa', '情感不对 '
    assert len(music_info.key_tokens) == len(music_info.section_emo_values), '关键词情感匹配错误'
    try:
        result = await createMid(music_info.identify, music_info.sentence_emo_label,
                                 music_info.key_tokens, music_info.section_emo_values,
                                 music_info.dynasty)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return jsonable_encoder(result)


@router.post("/get-colors-poems", responses={400: {"model": Code400}})
async def getKeyInfo(token_info: TokenInfo):
    r"""
    获得歌曲相关的颜色和唐诗

    example:
    {
        identify: 1650551534844182000
        emos: [0.9823723478, 0.23435354]
    }
    """
    assert len(token_info.section_emo_values) > 0, '颜色情绪标签错误'
    try:
        result = await getBg(token_info.identify, token_info.section_emo_values)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return jsonable_encoder(result)