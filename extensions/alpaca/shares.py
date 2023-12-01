import json

from . import get_api

from extensions.jess_extension import jess_extension

@jess_extension(
    description="Retrive the current price of a stock from Alpaca platform",
    param_descriptions={
        "ticker_symbol": "Ticker symbol of the stock, for which price needs to be retrived"
    }
)
def get_ticker_prices(ticker_symbol: str):
    try:
        api = get_api()
        # Get the quotes for the last 5 minutes
        bar = api.get_latest_bar(ticker_symbol)
        
        result = {
            "high": bar.h,
            "low": bar.l,
            "open": bar.o
        }
        return json.dumps(result)
    except Exception as e:
        return f"An error occurred: {e}"

@jess_extension(
    description="Sell specific amount of shares on Alpaca platform",
    param_descriptions={
        "ticker_symbol": "Ticker symbol of the stock, which to sell",
        "shares_qty": "Number of shares to sell. Should be float"
    }
)
def sell_shares(ticker_symbol: str, shares_qty: str):
    shares = float(shares_qty)
    try:
        api = get_api()
        # Submit a market order to buy 1 share of Apple at market price
        api.submit_order(
            symbol=ticker_symbol,
            qty=shares,
            side='sell',
            type='market',
            time_in_force='day'
        )
        return f"Sold {shares} shares of {ticker_symbol}"
    except Exception as e:
        return f"An error occurred: {e}"

@jess_extension(
    description="Buy specific amount of shares on Alpaca platform",
    param_descriptions={
        "ticker_symbol": "Ticker symbol of the stock, which to buy",
        "shares_qty": "Number of shares to buy.Should be float"
    }
)
def buy_shares(ticker_symbol: str, shares_qty: str):
    shares = float(shares_qty)
    try:
        api = get_api()
        # Submit a market order to buy 1 share of Apple at market price
        print(api.submit_order(
            symbol=ticker_symbol,
            qty=shares,
            side='buy',
            type='market',
            time_in_force='day'
        ))
        return f"Bought {shares} shares of {ticker_symbol}"
    except Exception as e:
        return f"An error occurred: {e}"
    
@jess_extension(
    description="list all open positions on Alpaca platform",
    param_descriptions={}
)
def get_open_positions():
    try:
        api = get_api()
        portfolio = api.list_positions()

        # Print the quantity of shares for each position.
        result = ""
        for position in portfolio:
            result = result + "{} shares of {}\n".format(position.qty, position.symbol)
        if result == "":
            return "No open positions"
        return result
    except Exception as e:
        return f"An error occurred: {e}"
    

@jess_extension(
    description="Get the current buying power on Alpaca platform",
    param_descriptions={}
)
def get_buying_power():
    try:
        api = get_api()
        account = api.get_account()
        equity = float(account.equity)
        margin_multiplier = float(account.multiplier)
        total_buying_power = margin_multiplier * equity
        return total_buying_power
    except Exception as e:
        return f"An error occurred: {e}"


@jess_extension(
    description="Check if the market is open now. Check before opening any positions",
    param_descriptions={}
)
def is_market_open_now():
    try:
        api = get_api()
        clock = api.get_clock()
        return str(clock.is_open)
    except Exception as e:
        return f"An error occurred: {e}"
    
@jess_extension(
    description="Return list of open orders on Alpaca platform",
    param_descriptions={}
)
def get_orders():
    try:
        api = get_api()
        portfolio = api.list_orders(status="open")

        result = ""
        # Print the quantity of shares for each position.
        for position in portfolio:
            print(position)
            result = result + "{} shares of {}, order id is: {}\n".format(position.qty, position.symbol, position.id)
        return result
    except Exception as e:
        return f"An error occurred: {e}"


@jess_extension(
    description="Cancel an open order on Alpaca platform",
    param_descriptions={
        "order_id": "Order id of the order to cancel"
    }
)
def cancel_order(order_id: str):
    try:
        api = get_api()
        api.cancel_order(order_id)
        return f"Order {order_id} cancelled"
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    print(get_orders())
