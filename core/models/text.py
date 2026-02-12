from pydantic import BaseModel
from typing import List


class TextData(BaseModel):
    sentences: List[str]