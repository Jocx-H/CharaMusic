#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import date, datetime
from enum import Enum


class MusicInfo(BaseModel):
    r"""
    identify: 用户标识符
    sentence_emo_label: 整句话的情感倾向
    key_tokens: 关键词列表
    section_emo_values: 关键词情绪列表
    """
    identify: str
    sentence_emo_label: str
    key_tokens: List[str]
    section_emo_values: List[float]
    dynasty: int


class TokenInfo(BaseModel):
    identify: str
    section_emo_values: List[float]