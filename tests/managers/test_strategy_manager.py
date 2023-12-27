import unittest
from random import random

import pandas as pd

from dxlib import History


class TestStrategyManager(unittest.TestCase):
    class SimpleStrategy:
        def __init__(self):
            super().__init__()

        def execute(
                self, idx, position: pd.Series, history: History
        ) -> pd.Series:
            return pd.Series([random() for _ in range(len(position))], index=position.index)

    def test_execute(self):
        import asyncio

        async def printable(subscription):
            async def process_signal(value):
                # Process the signal (in this case, just print it)
                print(f"Received signal: {value}")

                # Return the processed signal
                return value + 1

            async def subscription_handler():
                async for value in subscription:
                    processed_value = await process_signal(value)
                    yield processed_value

            return subscription_handler()

        # Example usage
        async def main():
            async def fake_subscription():
                for i in range(5):
                    yield i
                    await asyncio.sleep(1)  # Simulate asynchronous signal emission

            subscription = fake_subscription()
            processed_subscription = await printable(subscription)

            async for processed_value in processed_subscription:
                # Do something with the processed value (in this case, just print it)
                print(f"Processed value: {processed_value}")

        # Run the example
        asyncio.run(main())


if __name__ == '__main__':
    unittest.main()
