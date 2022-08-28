#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder

from model.code import *
from service import chara_service

# 构建api路由
router = APIRouter(
    prefix="/character",
    tags=["Character"],
)


@router.post('/get-tokens/{text}', responses={400: {"model": Code400}})
async def getKeyToken(text: str):
    """
    上传字符串，获得文本分析后的句子情感标签、关键词序列和关键词情感值序列
    Example:
    {
        "text": "床前明月光，疑是地上霜"
    }
    """
    try:
        res = await chara_service.textAnalysis(text)
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return jsonable_encoder(res)


@router.post('/upload-handwriting-picture/identify', responses={400: {"model": Code400}})
async def recognizeHandwritingImg(identify: str, img: UploadFile):
    """
    上传需要识别的手写文字图片，
    identify: home那里获得的用户标识符
    img: 手写识别图片
    识别成功返回True，失败返回False
    Example:
    {
        "identify": 16503705536117435,
        "img": 印刷体汉字图片文件
    }
    """
    try:
        assert identify is not None, "请务必传入一个时间戳"
        res = await chara_service.recognizeHandWritingImg(identify, img)
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return jsonable_encoder(res)


@router.post('/get-handwriting-text/identify', responses={400: {"model": Code400}})
async def getKeyToken(identify: str):
    """
    获得手写出来的图片
    identify: 用户标志符
    Example:
    {
        "identify": "16503705536117435"
    }
    """
    try:
        res = await chara_service.getHandwritingImgText(identify)
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return jsonable_encoder(res)
