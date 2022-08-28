#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from model.code import *
from service.home_service import *

# 构建api路由
router = APIRouter(
    prefix="/home",
    tags=["Home"],
)


@router.get('/token', responses={400: {"model": Code400}})
def createToken():
    try:
        result = getToken()
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return {'code': 200, 'message': 'success', 'data': result}


@router.get('/get-picture', responses={400: {"model": Code400}})
def getPicture(pic_id: int):
    r"""
    获取给用户展示的图片文件

    example:
    {
        pic_id: 56
    }
    """
    try:
        result = getPic(pic_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    file_response = FileResponse(result, filename='chara_music.jpg', media_type='jpg')
    file_response.headers['Access-Control-Expose-Headers'] = "Content-Disposition"
    return file_response


@router.post('/get-picture-info', responses={400: {"model": Code400}})
def getPicture(pic_id: int):
    r"""
    获取给用户展示的图片文件简介

    example:
    {
        pic_id: 56
    }
    """
    try:
        result = getPictureInfo(pic_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="客户端运行错误，请检查输入内容或联系管理员！")
    return result