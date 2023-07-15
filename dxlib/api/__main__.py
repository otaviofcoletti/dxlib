from .logger import CustomLogger
from .terminal import Terminal
from .data.AlphaVantage import AlphaVantageAPI
from .utils import append_to_csv
import time
from rich.table import Table


def print_currency_exchange_table(terminal, dataframe):
    table = Table(show_header=True, header_style="bold")
    table.add_column("Currency")
    table.add_column("Exchange Rate")
    table.add_column("Last Refreshed")

    for index, row in dataframe.iterrows():
        table.add_row(
            row['Currency'],
            row['Exchange Rate'],
            row['Last Refreshed']
        )

    terminal.clear()
    terminal.print(table)


def main():
    logger = CustomLogger()
    terminal = Terminal()
    api_key = 'A7MUFCXLS779G7EZ'
    api = AlphaVantageAPI(api_key)

    try:
        for i in range(5):
            currencies_to_query = ['JPY', 'EUR', 'GBP', 'CAD', 'AUD']
            exchange_rates_df = api.fetch_currency_exchange_rates(currencies_to_query)
            append_to_csv(exchange_rates_df, 'currency_exchange_rates.csv')
            print_currency_exchange_table(terminal, exchange_rates_df)
            time.sleep(60)
        logger.log_info(f"Fetched data for symbol")

    except Exception as e:
        logger.log_exception(f"Error fetching data: {str(e)}")


if __name__ == "__main__":
    main()
