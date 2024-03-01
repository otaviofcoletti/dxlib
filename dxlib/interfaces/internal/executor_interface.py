from .internal_interface import InternalInterface
from ..servers.endpoint import Endpoint, Method
from ...core import Executor, History, Inventory


class ExecutorInterface(InternalInterface):
    def __init__(self, executor: Executor = None, interface_url: str = None, headers: dict = None):
        super().__init__(interface_url, headers)
        if executor is None and interface_url is None:
            raise ValueError("Executor or URL must be provided")
        self.executor = executor

    @Endpoint.http(Method.POST,
                   "/run",
                   "Executes a single history and returns the result")
    def run(self, obj: any):
        try:
            history = History.from_dict(serialized=True, **obj)
        except Exception as e:
            raise ValueError(f"Could not parse history: {e}")

        try:
            result: History = self.executor.run(history)
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

    @Endpoint.http(Method.GET, "/position", "Gets the total aggregated position", output=Inventory)
    def get_position(self):
        return {
            "status": "success",
            "data": self.executor.position.to_dict(serializable=True),
        }
