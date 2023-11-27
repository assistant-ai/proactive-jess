from . import get_api

from extensions.jess_extension import jess_extension


@jess_extension(
    description="Get overall account performance from all the investments",
    param_descriptions={}
)
def get_performance():
    api = get_api()
    orders = api.list_orders(status='all')

    # Calculate net investment
    net_investment = 0
    for order in orders:
        # Check if the order was filled
        if order.status == 'filled':
            # Calculate the total value of the order
            total_value = float(order.filled_avg_price) * float(order.filled_qty)

            # Add to or subtract from net investment
            if order.side == 'buy':
                net_investment += total_value
            elif order.side == 'sell':
                net_investment -= total_value

    # Get current portfolio value
    positions = api.list_positions()
    current_value = sum(float(position.market_value) for position in positions)

    # Calculate performance
    performance = ((current_value - net_investment) / net_investment) * 100

    result = f"Net Investment: ${net_investment:.2f}"
    result = result + f"\nCurrent Portfolio Value: ${current_value:.2f}"
    result = result + f"\nPortfolio Performance: {performance:.2f}%"
    return result

if __name__ == "__main__":
    get_performance()