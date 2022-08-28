#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import character_api, home_api, music_api

RESOURCES_PATH = r'backend/assets/res'

# 声明fast-api的实例
app = FastAPI(title='文档说明', description='整体描述')

# 跨域配置
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8081",
    "http://localhost:8080",
    "http://124.70.70.189",
    "http://124.70.70.189:8080"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

# 注册api模块
app.include_router(home_api.router, prefix='/api')
app.include_router(character_api.router, prefix='/api')
app.include_router(music_api.router, prefix='/api')

# 配置容器启动相应的实例
if __name__ == '__main__':
    # uvicorn.run(app='main:app', port=8000, reload=True, debug=True)
    uvicorn.run(app='main:app', host='127.0.0.1', port=8000, reload=True, debug=True)
