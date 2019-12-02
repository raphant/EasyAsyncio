import abc
import asyncio
from abc import abstractmethod

from easyasyncio.baseasyncioobject import BaseAsyncioObject


class Prosumer(BaseAsyncioObject, metaclass=abc.ABCMeta):

    def __init__(self, data):
        self.data = data

    @abstractmethod
    async def fill_queue(self):
        """implement the queue filling logic here"""
        pass

    async def worker(self):
        """get each item from the queue and pass it to self.work"""
        while self.context.running:
            data = await self.queue.get()
            if data is None:
                break
            result = await self.work(data)
            if result:
                self.append()
            self.queue.task_done()

    async def run(self):
        await self.fill_queue()
        self.logger.info('%s starting...', self.name)
        for _ in range(min(self.queue.qsize(), self.max_concurrent)):
            self.workers.add(self.loop.create_task(self.worker()))
        await asyncio.gather(*self.workers)
        await self.queue.join()
        self.logger.info('%s is finished', self.name)
