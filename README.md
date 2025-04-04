# FRED Economic Data Dashboard

This Streamlit application displays economic indicators from the Federal Reserve Economic Data (FRED) API.

## Features

- Interactive selection of economic indicators
- Historical data visualization with multiple chart types
- Key statistics for each indicator
- Raw data display option
- Responsive layout

## Project Structure

```
fred-economic-dashboard/
├── app.py                 # Main application file
├── logger_config.py       # Logging configuration
├── requirements.txt       # Python dependencies
├── .env                   # API key configuration (create from .env.example)
├── .env.example           # Example environment variables file
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
└── logs/                  # Log files directory (created automatically)
    └── app_YYYY-MM-DD.log # Daily log files
```

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd fred-economic-dashboard
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Get FRED API Key:
   - Visit https://fred.stlouisfed.org/docs/api/api_key.html to get your API key
   - Copy `.env.example` to `.env` and add your API key

5. Run the application:
   ```
   streamlit run app.py
   ```

## Data Sources

This application uses the Federal Reserve Economic Data (FRED) API to retrieve economic indicators. The following indicators are available:

- Gross Domestic Product (GDP)
- Real GDP
- GDP Growth Rate
- Personal Consumption Expenditures
- Unemployment Rate
- Consumer Price Index (CPI)
- Federal Funds Rate

## License

[MIT License](LICENSE)
