import logging
from abc import ABC

from dxlib.interfaces.servers import Server, HTTPServer
from dxlib.interfaces.servers.endpoint import get_endpoints
from dxlib.logger import LoggerMixin


class Manager(ABC, LoggerMixin):
    def __init__(
        self,
        comms: list[Server] = None,
        logger: logging.Logger = None,
    ):
        super().__init__(logger)
        if isinstance(comms, Server):
            self.comms = [comms]

        self.set_comms(comms or [])

    def set_comms(self, comms: list[Server]):
        self.comms = comms
        for comm in self.comms:
            comm.logger = self.logger

    def add_comm(self, comm: Server):
        if isinstance(comm, HTTPServer):
            comm.add_endpoints(get_endpoints(self))

        self.comms.append(comm)
        comm.logger = self.logger

    def start(self):
        if not self.comms:
            self.logger.warning("No communicators to start. Skipping...")
            return
        for comm in self.comms:
            comm.start()

    def stop(self):
        for comm in self.comms:
            comm.stop()

    def alive(self):
        return all([comm.alive for comm in self.comms]) and any(
            [comm.alive for comm in self.comms]
        )
