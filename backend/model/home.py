#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import date, datetime
from enum import Enum


class Token(BaseModel):
    pass