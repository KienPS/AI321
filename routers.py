from dataclasses import dataclass
import io
from typing import Annotated

from litestar import get, post, Controller, MediaType
from litestar.params import Body
from litestar.enums import RequestEncodingType
from litestar.response import Template
from litestar.datastructures import UploadFile

from pydantic import BaseModel, BaseConfig
import numpy as np
import cv2

import detectors as dt


class TOEICAnswerSheet(BaseModel):
    image: UploadFile
    scanned: bool = False
    
    class Config(BaseConfig):
        arbitrary_types_allowed=True


class ToeicParserController(Controller):
    
    @get(path="/", name="toeic_image_upload_form")
    async def get_toeic_image_upload_form(self) -> Template:
        return Template(template_name="toeic_image_form.html.jinja2")
    
    @post(path="/parse", name="parse_toeic_image")
    async def parse_toeic_answer_sheet_image(
            self,
            data: Annotated[TOEICAnswerSheet, Body(media_type=RequestEncodingType.MULTI_PART)]
    ) -> Template:
        content = await data.image.read()
        width, height = 2481, 3508
        image = np.fromstring(content, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        toeic_answer_sheet = cv2.resize(image, (width, height))
        if not data.scanned:
            toeic_answer_sheet = dt.findFullAnswerSheet(toeic_answer_sheet, width, height)
        
        listening_test, reading_test = dt.get_listen_test_image(toeic_answer_sheet), dt.get_reading_test_image(toeic_answer_sheet)
        listening_test_set, reading_test_set = dt.get_columns(listening_test), dt.get_columns(reading_test)
        
        user_listening_answer, user_reading_answer = [], []
        listening_answer_keys, reading_answer_keys = ['A'] * 100, ['B'] * 100 # For demo purpose only
        
        image_clone = image.copy()
        for i, sheet in enumerate(listening_test_set):
            keys = listening_answer_keys[25*i:25*(i+1)]
            ans = dt.get_my_ans(sheet, keys, image_clone, i, 'listening')
            for x in ans:
                user_listening_answer.append(x)
            
        for i, sheet in enumerate(reading_test_set):
            keys = reading_answer_keys[25*i:25*(i+1)]
            ans = dt.get_my_ans(sheet, keys, image_clone, i, 'reading')
            for x in ans:
                user_reading_answer.append(x)
                
            toeic_result = {
                'listening': [],
                'reading': []
            }
            listening_score, reading_score = 0, 0
            
            for i, (user, key) in enumerate(zip(user_listening_answer, listening_answer_keys)):
                toeic_result['listening'].append({'question': i+1, 'expected': key, 'yours': user, 'correct': user==key})
                if user == key:
                    listening_score += 1
            
            for i, (user, key) in enumerate(zip(user_reading_answer, reading_answer_keys)):
                toeic_result['reading'].append({'question': i+1, 'expected': key, 'yours': user, 'correct': user==key})
                if user == key:
                    reading_score += 1
                
            listening_score = listening_score / 100.
            reading_score = reading_score / 100.
        return Template(
            template_name='toeic_image_result.html.jinja2',
            context={
                'toeic_result': toeic_result,
                'listeing_score': listening_score,
                'reading_score': reading_score
            }
        )
