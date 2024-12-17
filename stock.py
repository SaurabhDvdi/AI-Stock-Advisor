import streamlit as st
import pandas as pd

# Function to load CSV data and handle different formats
def load_csv_data(ticker):
    try:
        # Assuming the CSV files are named based on the ticker symbol
        file_path = f"data/{ticker}.csv"  # Modify this path to your folder structure
        data = pd.read_csv(file_path)

        # Strip any leading/trailing spaces from column names
        data.columns = data.columns.str.strip()

        # Check the first few rows and columns to determine format
        st.write(f"Columns in the data for {ticker}: {data.columns}")
        st.write(f"First few rows of the data for {ticker}:")
        st.write(data.head())

        # Ensure 'Date' column exists, if not, try renaming
        if 'Date' not in data.columns:
            st.write(f"Columns in the data: {data.columns}")
            # Manually rename if necessary
            if 'date' in data.columns:
                data.rename(columns={'date': 'Date'}, inplace=True)
            elif 'Datetime' in data.columns:
                data.rename(columns={'Datetime': 'Date'}, inplace=True)

        # Handle date column
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')  # Use 'coerce' to handle errors
        data = data.dropna(subset=['Date'])  # Drop rows with missing date values
        data.set_index('Date', inplace=True)

        # Handle extra 'Close' or 'Adj Close' columns
        if 'Adj Close' in data.columns:
            data.rename(columns={'Adj Close': 'Close'}, inplace=True)

        if data.columns.tolist().count('Close') > 1:
            # Drop duplicate 'Close' columns if there are multiple 'Close' columns
            data = data.loc[:, ~data.columns.duplicated()]

        # Ensure only relevant columns are kept
        data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

        return data
    except FileNotFoundError:
        st.error(f"CSV file for {ticker} not found.")
        return pd.DataFrame()

# Streamlit UI Setup
st.title("AI Stock Advisor")
st.sidebar.header("Settings")

# Predefined list of stock tickers
stock_ticker_options = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NFLX"]
index_ticker_options = ["IXIC", "GSPC"]

# Dropdowns for selecting tickers
selected_ticker = st.sidebar.selectbox("Select a Stock Ticker", stock_ticker_options, index=0)
selected_index_ticker = st.sidebar.selectbox("Select an Index Ticker", index_ticker_options, index=0)

# Submit button
if st.sidebar.button("Submit"):
    # Load data for the selected stock and index ticker
    stock_data = load_csv_data(selected_ticker)
    index_data = load_csv_data(selected_index_ticker)

    # Display stock data
    st.subheader(f"Stock Data for {selected_ticker}")
    if not stock_data.empty:
        st.dataframe(stock_data.tail(5))  # Show last 5 rows
        st.line_chart(stock_data["Close"])
    else:
        st.warning(f"No data available for {selected_ticker}")

    # Display index data
    st.subheader(f"Index Data for {selected_index_ticker}")
    if not index_data.empty:
        if "Close" in index_data.columns:
            st.dataframe(index_data.tail(5))  # Show last 5 rows
            st.line_chart(index_data["Close"])
        else:
            st.warning(f"No 'Close' column found in the index data for {selected_index_ticker}")
    else:
        st.warning(f"No data available for {selected_index_ticker}")

    # Insights (placeholder logic)
    st.subheader("Insights")
    if not stock_data.empty:
        st.write(f"Latest closing price for {selected_ticker}: ${stock_data['Close'].iloc[-1]:.2f}")
    if not index_data.empty:
        st.write(f"Latest closing price for {selected_index_ticker}: ${index_data['Close'].iloc[-1]:.2f}")
