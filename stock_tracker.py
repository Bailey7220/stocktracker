import requests
import json
import time
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread

# Load configuration from config.json
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Fetch the latest stock/ETF price using Alpha Vantage API
def fetch_stock_price(symbol, api_key, api_url):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": api_key
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            latest_time = list(data["Time Series (1min)"].keys())[0]
            latest_price = float(data["Time Series (1min)"][latest_time]["1. open"])
            return latest_price
        except KeyError:
            raise Exception(f"Error: Could not fetch data for {symbol}. Check the API response.")
    else:
        raise Exception(f"API request failed for {symbol} with status code {response.status_code}")

# Monitor all stocks/ETFs and notify based on thresholds
def track_stocks(output_text):
    config = load_config()
    symbols = config["symbols"]
    api_key = config["api_key"]
    api_url = config["api_url"]
    thresholds = config["thresholds"]

    while True:
        for symbol in symbols:
            try:
                current_price = fetch_stock_price(symbol, api_key, api_url)
                output_text.insert(tk.END, f"Current price of {symbol}: ${current_price:.2f}\n")

                # Check against thresholds for the current stock/ETF
                low_threshold = thresholds[symbol]["low"]
                high_threshold = thresholds[symbol]["high"]

                if current_price < low_threshold:
                    output_text.insert(tk.END, f"Alert: {symbol} has fallen below the threshold (${low_threshold})!\n")
                elif current_price > high_threshold:
                    output_text.insert(tk.END, f"Alert: {symbol} has exceeded the threshold (${high_threshold})!\n")
            except Exception as e:
                output_text.insert(tk.END, f"Error fetching data for {symbol}: {e}\n")
        output_text.insert(tk.END, "Waiting 1 minute before the next check...\n")
        output_text.yview(tk.END)  # Scroll to the end of the text area
        time.sleep(60)  # Wait 60 seconds between checks

# Run the tracker continuously with a delay in a separate thread
def start_tracking(output_text):
    output_text.delete(1.0, tk.END)  # Clear previous results
    tracking_thread = Thread(target=track_stocks, args=(output_text,))
    tracking_thread.daemon = True
    tracking_thread.start()

# Create the GUI
def create_gui():
    window = tk.Tk()
    window.title("Stock Price Tracker")
    window.geometry("500x450")
    window.configure(bg="#2e2e2e")  # Dark background

    # Create a frame for the output text area
    frame = tk.Frame(window, bg="#2e2e2e")
    frame.pack(padx=10, pady=11)

    # Create a label for the title
    title_label = tk.Label(window, text="Real-time Stock Price Tracker", bg="#2e2e2e", fg="white", font=("Times New Roman", 16, "bold"))
    title_label.pack(pady=10)

    # Create a text area for displaying results
    output_text = scrolledtext.ScrolledText(frame, width=70, height=15, bg="#f0f0f0", fg="#333333", font=("Times New Roman", 12))
    output_text.pack()

    # Create a button to start tracking
    track_button = tk.Button(window, text="Start Tracking", command=lambda: start_tracking(output_text),
                             bg="#4CAF50", fg="white", font=("Times New Roman", 12, "bold"))
    track_button.pack(pady=5)

    # Create a button to exit the application
    exit_button = tk.Button(window, text="Exit", command=window.quit,
                            bg="#F44336", fg="white", font=("Times New Roman", 12, "bold"))
    exit_button.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
