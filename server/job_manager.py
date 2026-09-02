
import glob
from dataclasses import dataclass
import asyncio
import time
import os
import aiofiles
from asyncio import Queue
from fastapi import FastAPI, File, UploadFile
from contextlib import asynccontextmanager


async def stream_file(infile, dest):
    async with aiofiles.open(dest, 'wb') as outfile:
        while chunk := await infile.read(100*1024):
            await outfile.write(chunk)


@dataclass
class Job:
    job_dir: str
    images: list[str] = None


class JobManager:
    def __init__(self, jobs_dir):
        self.queue = Queue()
        self.job_dir = jobs_dir
        self.job_id = int(time.time())

    def get_next_job_id(self):
        next_id = self.job_id
        self.job_id += 1
        return next_id

    async def submit(self, files: list[UploadFile]):
        base_dir = os.path.join(self.job_dir, str(self.get_next_job_id()))
        os.makedirs(base_dir, exist_ok=True)
        for n, file in enumerate(files):
            path = os.path.join(base_dir, f'photo{n:04d}.png')
            await stream_file(file, path)
        await self.queue.put(base_dir)

    @asynccontextmanager
    async def get_job(self, timeout=None):
        if timeout is None:
            job_dir = await self.queue.get()
        else:
            job_dir = await asyncio.wait_for(
                self.queue.get(),
                timeout=timeout,
            )
        images = glob.glob(os.path.join(job_dir, '*.png'))
        yield Job(
            job_dir=job_dir,
            images=images,
        )
        for src in images:
            os.unlink(src)
        os.rmdir(job_dir)
