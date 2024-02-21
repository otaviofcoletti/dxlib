import json

from .internal_interface import InternalInterface
from ..servers.endpoint import Endpoint, Method
from ... import History, Inventory
from ...core import Executor


class ExecutorHTTPInterface(InternalInterface):
    def __init__(self, executor: Executor):
        super().__init__()
        self.executor = executor

    @Endpoint.http(Method.POST, "/run", "Executes a single observation and returns the result")
    def run(self, obj: any, in_place: bool = False):
        if isinstance(obj, str):
            obj = json.loads(obj)
        history = History.from_dict(serialize=True, **obj)
        result: History = self.executor.run(history, in_place=in_place)
        response = {
            "status": "success",
            "result": result.to_dict(serialize=True),
        }
        return response

    @Endpoint.http(Method.POST, "/position", "Adds to the current position")
    def set_position(self, obj: any):
        position = Inventory.from_dict(**obj)
        self.executor.position += position

        response = {
            "status": "success",
        }

        return response

    @Endpoint.http(Method.GET, "/position", "Gets the current position")
    def get_position(self):
        return self.executor.position.to_json()
