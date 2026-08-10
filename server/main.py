
import subprocess
from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def index():
    return ''


@app.post('/upload')
async def hello(file: UploadFile):
    with open('out.png', 'wb') as outfile:
        outfile.write(await file.read())
    subprocess.run([
        './print_scroll.sh',
        'out.png',
    ])
    return ''
