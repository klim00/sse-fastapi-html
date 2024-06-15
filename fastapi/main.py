from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from sse_starlette.sse import EventSourceResponse
from asyncio import sleep

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data = None

@app.post("/")
async def save_data(req:Request):
    req_body = await req.json()
    global data
    data = req_body.copy()
    return req_body


STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond

@app.get("/sse")
async def stream_data(request:Request):
    global data
    def isNewData():
        return data != None
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            
            if isNewData():
                global data
                yield {
                    "event":"test",
                    "retry":RETRY_TIMEOUT,
                    "data":data
                }
                data = None

            await sleep(STREAM_DELAY)
    return EventSourceResponse(event_generator())