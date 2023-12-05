import json

from . import get_api, get_api_per_user
from rest.token_management import get_user_id
from quart import jsonify, request
from rest.main_app import app

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
        "ticker_symbol": "Ticker symbol of the stock, which to buy.",
        "notional": "notional to buy. Should be float passed as string."
    }
)
def buy_shares(ticker_symbol: str, notional: str):
    notional = float(notional)
    try:
        api = get_api()
        # Submit a market order to buy 1 share of Apple at market price
        print(api.submit_order(
            symbol=ticker_symbol,
            notional=notional,
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


@app.route('/finances/alpaca/sell/all', methods=['POST'])
async def sell_all():
    data = await request.json
    ticker = data.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker parameter is missing"}), 400

    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "please re-authentificate"}), 500
    if not user_id:
        return jsonify({"error": "please re-authentificate"}), 500
    api = get_api_per_user(user_id)

    # Fetch current position
    position = api.get_position(ticker)
    qty = position.qty

    # Submit sell order
    api.submit_order(symbol=ticker, qty=qty, side='sell')
    return jsonify({"message": f"Submitted sell order for all shares of {ticker}"}), 200


@app.route('/finances/alpaca/sell/stoploss', methods=['POST'])
async def sell_stop_loss():
    data = await request.json
    ticker = data.get('ticker')
    stop_price = data.get('stop_price')
    if not ticker or not stop_price:
        return jsonify({"error": "Ticker and stop price parameters are required"}), 400

    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "please re-authentificate"}), 500
    if not user_id:
        return jsonify({"error": "please re-authentificate"}), 500
    api = get_api_per_user(user_id)

    position = api.get_position(ticker)
    qty = position.qty

    # Submit sell order with stop price
    api.submit_order(symbol=ticker, qty=qty, side='sell', type='stop', stop_price=stop_price)
    return jsonify({"message": f"Submitted stop loss sell order for {ticker} at {stop_price}"}), 200


@app.route('/finances/alpaca/sell/takeprofit', methods=['POST'])
async def sell_take_profit():
    data = await request.json
    ticker = data.get('ticker')
    limit_price = data.get('limit_price')
    if not ticker or not limit_price:
        return jsonify({"error": "Ticker and limit price parameters are required"}), 400

    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "please re-authentificate"}), 500
    if not user_id:
        return jsonify({"error": "please re-authentificate"}), 500
    api = get_api_per_user(user_id)

    position = api.get_position(ticker)
    qty = position.qty

    # Submit sell order with limit price
    api.submit_order(symbol=ticker, qty=qty, side='sell', type='limit', limit_price=limit_price)
    return jsonify({"message": f"Submitted take profit sell order for {ticker} at {limit_price}"}), 200


@app.route('/finances/alpaca/portfolio', methods=['GET'])
async def rest_get_open_positions():
    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "please re-authentificate"}), 500
    if not user_id:
        return jsonify({"error": "please re-authentificate"}), 500
    api = get_api_per_user(user_id)
    api = get_api()
    result = {}
    portfolio = api.list_positions()
    if not portfolio:
        return jsonify("No open positions"), 200
    for position in portfolio:
        result[position.symbol] = position.qty
    return  jsonify(result), 200


@app.route('/finances/alpaca/buy/conditional', methods=['POST'])
async def buy_conditional():
    data = await request.json
    ticker = data.get('ticker')
    limit_price = data.get('limit_price')
    notional = data.get('notional')

    if not ticker or not limit_price or not notional:
        return jsonify({"error": "Ticker, limit price, and notional amount are required"}), 400

    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "please re-authenticate"}), 500
    if not user_id:
        return jsonify({"error": "please re-authenticate"}), 500

    api = get_api_per_user(user_id)

    # Submit buy limit order
    api.submit_order(symbol=ticker, notional=notional, side='buy', type='limit', limit_price=limit_price)
    return jsonify({"message": f"Submitted limit buy order for {ticker} at ${limit_price}, total notional ${notional}"}), 200


@app.route('/finances/alpaca/orders', methods=['GET'])
async def rest_get_orders():
    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "Please re-authenticate"}), 500
    if not user_id:
        return jsonify({"error": "Please re-authenticate"}), 500

    api = get_api_per_user(user_id)

    try:
        orders = api.list_orders(status="open")
        orders_info = [{"symbol": order.symbol, "quantity": order.qty, "order_id": order.id} for order in orders]
        return jsonify(orders_info), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/finances/alpaca/market/open', methods=['GET'])
async def rest_is_market_open_now():
    token = request.headers.get('Authorization').split(' ')[1]
    user_id = None
    try:
        user_id = get_user_id(token)
    except:
        return jsonify({"error": "please re-authentificate"}), 500
    if not user_id:
        return jsonify({"error": "please re-authentificate"}), 500
    api = get_api_per_user(user_id)
    clock = api.get_clock()
    return jsonify(clock.is_open), 200