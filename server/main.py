
import base64
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from job_manager import JobManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    job_manager.queue.shutdown()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

job_manager = JobManager()

@app.get('/')
async def index():
    return ''


@app.post('/upload')
async def hello(files: list[UploadFile]):
    await job_manager.submit(files)
    return ''


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('websocket connected')
    while True:
        try:
            async with job_manager.get_job(timeout=1) as job:
                payload = {
                    'job' : job.job_dir,
                    'images' : [],
                }
                for img_src in job.images:
                    img_data = open(img_src, 'rb').read()
                    img_encoded = base64.encodebytes(img_data).decode('utf-8')
                    payload['images'].append(img_encoded)
                await websocket.send_json(payload)

        except asyncio.TimeoutError:
            try:
                await websocket.send_text('')
            except WebSocketDisconnect:
                break
            continue

        except WebSocketDisconnect:
            break
    print('websocket disconnected')
