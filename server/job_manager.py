
import asyncio
import time
import os
import aiofiles
from asyncio import Queue
from fastapi import FastAPI, File, UploadFile


async def stream_file(infile, dest):
    async with aiofiles.open(dest, 'wb') as outfile:
        while chunk := await infile.read(100*1024):
            await outfile.write(chunk)


class JobManager:
    def __init__(self):
        self.queue = Queue()
        self.job_dir = './jobs'
        self.job_id = int(time.time())
        if not os.path.exists(self.job_dir):
            os.mkdir(self.job_dir)

    def get_next_job_id(self):
        next_id = self.job_id
        self.job_id += 1
        return next_id

    async def submit(self, files: list[UploadFile]):
        base_dir = os.path.join(self.job_dir, str(self.get_next_job_id()))
        os.mkdir(base_dir)
        for n, file in enumerate(files):
            path = os.path.join(base_dir, f'photo{n:04d}.png')
            await stream_file(file, path)
        await self.queue.put(base_dir)

    async def get_job(self, timeout=None):
        if timeout is None:
            return await self.queue.get()

        job = await asyncio.wait_for(
            self.queue.get(),
            timeout=timeout,
        )
        return job
