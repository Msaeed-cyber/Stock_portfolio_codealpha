import requests
import json
from prettytable import PrettyTable

class StockPortfolio:
    def __init__(self, api_key, data_file='portfolio_data.json'):
        self.api_key = api_key
        self.data_file = data_file
        self.portfolio = self.load_portfolio()

    def add_stock(self, symbol, shares):
        if symbol in self.portfolio:
            self.portfolio[symbol] += shares
        else:
            self.portfolio[symbol] = shares
        print(f"Added {shares} shares of {symbol}.")
        self.save_portfolio()

    def remove_stock(self, symbol, shares):
        if symbol in self.portfolio:
            if self.portfolio[symbol] > shares:
                self.portfolio[symbol] -= shares
                print(f"Removed {shares} shares of {symbol}.")
            elif self.portfolio[symbol] == shares:
                del self.portfolio[symbol]
                print(f"Removed all shares of {symbol}.")
            else:
                print(f"Not enough shares to remove. You have {self.portfolio[symbol]} shares.")
            self.save_portfolio()
        else:
            print(f"{symbol} not found in portfolio.")

    def get_stock_price(self, symbol):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={self.api_key}'
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error fetching data for {symbol}: HTTP {response.status_code}")
            return None
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Error parsing JSON for {symbol}")
            return None

        # Debugging: Print raw response
        print(f"Raw API response for {symbol}: {data}")

        if "Time Series (1min)" in data:
            latest_time = list(data["Time Series (1min)"])[0]
            return float(data["Time Series (1min)"][latest_time]["1. open"])
        elif "Error Message" in data:
            print(f"Error fetching data for {symbol}: {data['Error Message']}")
        elif "Note" in data:  # Rate limit reached
            print(f"API call limit exceeded: {data['Note']}")
        else:
            print(f"Unexpected error fetching data for {symbol}")
        
        return None

    def display_portfolio(self):
        table = PrettyTable()
        table.field_names = ["Symbol", "Shares", "Current Price", "Total Value"]
        total_value = 0
        for symbol, shares in self.portfolio.items():
            price = self.get_stock_price(symbol)
            if price:
                value = shares * price
                total_value += value
                table.add_row([symbol, shares, f"${price:.2f}", f"${value:.2f}"])
        print(table)
        print(f"Total Portfolio Value: ${total_value:.2f}")

    def display_all_stock_prices(self):
        """
        Displays stock prices for a predefined list of popular stocks.
        """
        # Add more symbols as needed
        popular_stocks = ["AAPL", "GOOGL", "AMZN", "TSLA", "MSFT", "NFLX", "FB", "NVDA", "BRK.A", "V"] 
        table = PrettyTable()
        table.field_names = ["Symbol", "Current Price"]
        
        for symbol in popular_stocks:
            price = self.get_stock_price(symbol)
            if price:
                table.add_row([symbol, f"${price:.2f}"])
            else:
                table.add_row([symbol, "N/A"])
        
        print(table)

    def save_portfolio(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.portfolio, f)
        print("Portfolio data saved.")

    def load_portfolio(self):
        try:
            with open(self.data_file, 'r') as f:
                portfolio = json.load(f)
            print("Portfolio data loaded.")
            return portfolio
        except FileNotFoundError:
            print("No saved portfolio data found. Starting with an empty portfolio.")
            return {}

if __name__ == "__main__":
    api_key = "751|7DvtnRaNvLuN7loRKePhSkTF0xYugafmHLgxLbzu"  # Your provided API key
    portfolio = StockPortfolio(api_key)

    while True:
        print("\n1. Add stock\n2. Remove stock\n3. View portfolio\n4. View popular stock prices\n5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            symbol = input("Enter stock symbol: ").upper()
            shares = int(input("Enter number of shares: "))
            portfolio.add_stock(symbol, shares)
        elif choice == '2':
            symbol = input("Enter stock symbol: ").upper()
            shares = int(input("Enter number of shares to remove: "))
            portfolio.remove_stock(symbol, shares)
        elif choice == '3':
            portfolio.display_portfolio()
        elif choice == '4':
            portfolio.display_all_stock_prices()
        elif choice == '5':
            portfolio.save_portfolio()
            break
        else:
            print("Invalid choice. Please try again.")
