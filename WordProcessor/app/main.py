import asyncio
import uuid
from typing import Optional

import uvicorn
import logging
from fastapi import FastAPI, Header
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from WordProcessor.app.objects import WordAdditionRequest, WordProcessorResponse, WordProcessorErrorResponse
from WordProcessor.app.wordservice import WordService

app = FastAPI()
word_service = WordService()

PRE_DEFINED_TOKEN = "cyolo"


@app.post('/words/', description='Add words')
async def post_words(words_request: WordAdditionRequest, token: Optional[str] = Header(None)) -> JSONResponse:
    if token != PRE_DEFINED_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized request")
    request_id = str(uuid.uuid4())
    asyncio.create_task(word_service.add_words(words_request.words,request_id))
    return JSONResponse(content=jsonable_encoder(WordProcessorResponse(request_id=request_id)), status_code=202)


@app.get('/words/', description='Get words summary')
async def get_words_stat(token: Optional[str] = Header(None)) -> JSONResponse:
    if token != PRE_DEFINED_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized request")
    request_id = str(uuid.uuid4())
    stat_summary= await word_service.get_stats_summary(request_id)
    return JSONResponse(content=jsonable_encoder(stat_summary), status_code=200)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    request_id = str(uuid.uuid4())
    logging.debug(f'bad request {request_id} was made: {request}. {exc}')
    return JSONResponse(content=jsonable_encoder(WordProcessorErrorResponse(request_id=request_id,
                                                                            error="bad request was made by user")),
                                                                            status_code=400)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    request_id = str(uuid.uuid4())
    logging.debug(f'exception was raised on request {request_id} was made: {request}. {exc}')
    return JSONResponse(content=jsonable_encoder(WordProcessorErrorResponse(request_id=request_id,
                                                                            error=str(exc.detail))), status_code=exc.status_code)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")

