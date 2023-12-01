import yaml
from .memory_extension import Memory
from .google_calendar_extension import get_upcoming_calendar_events, create_google_calendar_event
from .simple_utils_extension import current_date_time
from .local_bash_extension import send_bash_command_to_local_host
from .alpaca.shares import cancel_order, get_ticker_prices, sell_shares, buy_shares, get_open_positions, get_buying_power, is_market_open_now, get_orders
from .alpaca.account import get_performance
from .fmp.client import FMP
from .internet import google, get_text_from_url, get_raw_html

def _read_config():
    with open("./config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    return config

def get_extensions():
    config = _read_config()

    extensions = {}
    fmp = None
    if config["extensions"]["long_term_memory"]:
        memory = Memory.create_memory_extension()
        extensions["store_in_long_term_memory"] = memory.store_in_long_term_memory
        extensions["query_from_long_term_memory"] = memory.query_from_long_term_memory
    if config["extensions"]["google_calendar"]:
        extensions["get_upcoming_calendar_events"] = get_upcoming_calendar_events
        extensions["create_google_calendar_event"] = create_google_calendar_event
    if config["extensions"]["current_date_time"]:
        extensions["current_date_time"] = current_date_time
    if config["extensions"]["local_bash"]:
        extensions["send_bash_command_to_local_host"] = send_bash_command_to_local_host
    if config["extensions"]["trading"]:
        fmp = FMP.create_fmp()
        extensions["get_ticker_prices"] = get_ticker_prices
        extensions["sell_shares"] = sell_shares
        extensions["buy_shares"] = buy_shares
        extensions["get_open_positions"] = get_open_positions
        extensions["get_buying_power"] = get_buying_power
        extensions["is_market_open_now"] = is_market_open_now
        extensions["get_orders"] = get_orders
        extensions["cancel_order"] = cancel_order
        extensions["get_performance"] = get_performance
        extensions["get_events_next_week"] = fmp.get_events_next_week
        extensions["get_events_next_day"] = fmp.get_events_next_day
        extensions["get_financial_news_about_specific_ticker"] = fmp.get_financial_news_about_specific_ticker
    if config["extensions"]["news"]:
        fmp = FMP.create_fmp()
        extensions["get_financial_news"] = fmp.get_financial_news
    if config["extensions"]["internet"]:
        extensions["google"] = google
        extensions["get_text_from_url"] = get_text_from_url
        extensions["get_raw_html"] = get_raw_html
    return extensions