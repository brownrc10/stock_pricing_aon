from datetime import datetime
from dataclasses import dataclass, field
import yfinance as yf


@dataclass
class StockMarketInfo:
    """Dataclass that stores stock market to update the c5 widget in the dashboard.
    Parameters:
        ticker (str): Stock Ticker. Default is HSY(Hershey)
        last_price (float): Last gathered price from the yfinance API
        is_open (bool): open variable from yfinance API to set the refresh conditions
        last_updated(str): Timestamp of last updated

    Methods:
        refresh: If the market is open, get fresh data.
        price_change_color: Returns values for streamlits st.delta parameter based on stock price comparison
        price_change: calculates price change.
    """

    ticker: str = field(default="HSY")
    last_price: float = field(default=0.0, init=False)
    is_open: bool = field(default=False, init=False)
    last_updated: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        self.is_open = yf.Market("US").status["status"] == "open"
        if self.is_open:
            self.last_price = round(yf.Ticker(self.ticker).fast_info["last_price"], 2)
            self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def price_change_color(current: float, previous: float) -> str:
        # https://docs.streamlit.io/develop/api-reference/data/st.metric

        match current:
            case _ if current < previous:
                return "inverse"
            case _ if current > previous:
                return "normal"
            case _:
                return "off"

    @staticmethod
    def price_change(current_price: float, previous_price: float) -> float | None:
        return (
            round(current_price - previous_price, 2)
            if previous_price is not None
            else None
        )
