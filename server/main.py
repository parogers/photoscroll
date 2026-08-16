
import os
import asyncio
from contextlib import asynccontextmanager
import subprocess
from typing import Annotated
from fastapi import FastAPI, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from job_manager import JobManager


async def worker(queue):
    print('starting worker...')
    while True:
        job_dir = await queue.get()
        try:
            images = [
                os.path.join(job_dir, fname)
                for fname in os.listdir(job_dir)
            ]
            subprocess.run([
                './print_scroll.sh',
            ] + images)
        except Exception as exc:
            print('worker exception', exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(worker(job_manager.queue))
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

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
