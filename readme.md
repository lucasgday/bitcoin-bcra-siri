# Bitcoin BCRA Siri

This project simulates the potential value of investing 1% of Argentina's central bank reserves in Bitcoin. The application visualizes the historical price of Bitcoin and the corresponding value of the investment over time.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Update Function](#update-function)
- [Data Source](#data-source)
- [License](#license)

## Features

- Interactive chart displaying the historical price of Bitcoin and the value of the investment.
- Date range slider to filter the data displayed on the chart.
- Dynamic updates to reflect the latest Bitcoin prices.
- Clear visualization of the investment's growth over time.

## Technologies Used

- Python
- Dash
- Plotly
- SQLite
- Pandas
- yfinance

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lucasgday/bitcoin-bcra-siri.git
   cd bitcoin-bcra-siri
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure you have the `fetch_historic_data.py` script to populate the database:
   ```bash
   python fetch_historic_data.py
   ```

## Usage

1. Start the Dash application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. Use the date range slider to filter the data displayed on the chart.

## Update Function

The application includes a function to update the Bitcoin price in the database. This function fetches the latest Bitcoin price from Yahoo Finance and updates the `btc_data.db` database accordingly.

To run the update function, execute the following command:
```bash
python update_latest_price.py
```

This will fetch the most recent Bitcoin price and update the corresponding values in the database.

## Data Source

The historical Bitcoin price data is fetched from Yahoo Finance using the `yfinance` library. The initial investment amount is based on 1% of Argentina's central bank reserves as of June 2024.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
