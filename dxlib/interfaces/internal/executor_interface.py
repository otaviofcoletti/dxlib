from .internal_interface import InternalInterface
from ..servers.endpoint import Endpoint, Method
from ...core import Executor, History, Inventory


class ExecutorHTTPInterface(InternalInterface):
    def __init__(self, executor: Executor):
        super().__init__()
        self.executor = executor

    @Endpoint.http(Method.POST, "/run", "Executes a single observation and returns the result")
    def run(self, obj: any, in_place: bool = False):
        try:
            history = History.from_dict(serialized=True, **obj)
        except Exception as e:
            raise ValueError(f"Could not parse history: {e}")

        try:
            result: History = self.executor.run(history, in_place=in_place)
        except Exception as e:
            raise ValueError(f"Could not run executor on history: {e}")

        response = {
            "status": "success",
            "data": result.to_dict(serializable=True),
        }
        return response

    @Endpoint.http(Method.POST, "/position", "Aggregates given inventory to the current position")
    def set_position(self, obj: any):
        try:
            position = Inventory.from_dict(**obj, serialized=True)
            self.executor.position += position
        except Exception as e:
            raise ValueError(f"Could not set position: {e}")

        response = {
            "status": "success",
        }

        return response

    @Endpoint.http(Method.GET, "/position", "Gets the total aggregated position")
    def get_position(self):
        return {
            "status": "success",
            "data": self.executor.position.to_dict(serializable=True),
        }
