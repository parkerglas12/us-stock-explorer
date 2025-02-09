import yfinance as yf
import pandas as pd
import streamlit as st
import altair as alt

def fetch_data(ticker: str) -> yf.Ticker:
    return yf.Ticker(ticker)

def clean_price_df(data: yf.Ticker, period: str) -> pd.DataFrame:
    df: pd.DataFrame = data.history(period=period).reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    return df
    
def main() -> None:
    # Page titles
    st.set_page_config(page_title="U.S. Stock Explorer", layout="centered")
    st.markdown('<div style="text-align: center;"><h1>U.S. Stock Explorer</h1></div>', unsafe_allow_html=True)

    # Gather data
    user_stock: str = st.text_input(label="Please enter the ticker symbol of the desired stock:", value="MSTR", autocomplete="off").strip().upper()
    data: yf.Ticker = fetch_data(user_stock)
    info_dict: dict = data.info
    st.divider()

    # First two heading
    st.metric(label="Company Name", value=info_dict["shortName"])
    st.metric(label="Sector", value=info_dict["sector"])

    # First set of columns
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Current Price", value=f"${info_dict['currentPrice']:.2f}")
        st.metric(label="52 Week Low", value=f"${info_dict['fiftyTwoWeekLow']:.2f}")
        st.metric(label="Volume", value=f"${info_dict['volume']:,}")
        
    with col2:
        st.metric(label="Market Cap", value=f"${info_dict['marketCap']:,}")
        st.metric(label="52 Week High", value=f"${info_dict['fiftyTwoWeekHigh']:.2f}")
        st.metric(label="Avg. Volume", value=f"${info_dict['averageVolume']:,}")

    # Price chart
    month_dict: dict = {
        "1y": "1 Year",
        "6mo": "6 Month",
        "3mo": "3 Month",
        "1mo": "1 Month"
    }

    st.divider()
    period: str = st.selectbox("Choose a timeframe for performance evaluation:", month_dict.keys())
    price_df: pd.DataFrame = clean_price_df(data, period)
    st.header(f"{user_stock} {month_dict[period]} Performance")
    y_min: float = price_df["Close"].min() * 0.95
    y_max: float = price_df["Close"].max() * 1.05
    chart: alt.Chart = (
        alt.Chart(price_df).mark_line(color="#2e7d32")
        .encode(x="Date:T", y=alt.Y("Close:Q", scale=alt.Scale(domain=[y_min, y_max])))
    )
    st.altair_chart(chart, use_container_width=True)
    low_price: float = price_df["Close"].min()
    max_price: float = price_df["Close"].max()
    start_price: float = price_df.loc[0, 'Close']
    last_price: float = price_df.loc[len(price_df) - 1, 'Close']
    percent_change: float = (last_price - start_price) / start_price * 100
    col1, col2, col3 = st.columns(3)
    with col1:
        # st.header(price_df.iloc[0, 2])
        st.metric(label="Start Price", value=f"${price_df.loc[0, 'Close']:.2f}")
        st.metric(label="Low Price", value=f"${price_df["Close"].min():.2f}")
    with col2:
        st.metric(label="Current Price", value=f"${price_df.loc[len(price_df) - 1, 'Close']:.2f}")
        st.metric(label="High Price", value=f"${price_df["Close"].max():.2f}")
    with col3:
        st.metric(label="Percentage Change", value=f"{percent_change:.2f}%")

    # About the company
    st.divider()
    st.header(f"About {user_stock}")
    st.text(info_dict["longBusinessSummary"])

    # yfinance attribution
    st.divider()
    st.text("-All data is derived from the yfinance Python library.")
    
if __name__ == "__main__":
    main()