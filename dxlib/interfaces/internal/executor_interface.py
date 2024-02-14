from ... import History, Inventory
from ...core import Executor
from ..servers.endpoint import Endpoint, Method
from .internal_interface import InternalInterface


class ExecutorHTTPInterface(InternalInterface):
    def __init__(self, executor: Executor):
        super().__init__()
        self.executor = executor

    @Endpoint.http(Method.POST, "/run", "Executes a single observation and returns the result")
    def run(self, obj: any, in_place: bool = False):
        # Transform the object into an observation
        history = History.from_dict(**obj)
        result: History = self.executor.run(history, in_place=in_place)
        response = {
            "status": "success",
            "result": result.to_json(),
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
