from typing import List, Optional

from pydantic import BaseModel


class WordAdditionRequest(BaseModel):
    words: List[str]


class WordProcessorResponse(BaseModel):
    request_id: str


class WordProcessorSummaryResponse(WordProcessorResponse):
    top5: Optional[dict]
    least: int
    median: int
    timestamp: str


class WordProcessorErrorResponse(WordProcessorResponse):
    error: Optional[str]
