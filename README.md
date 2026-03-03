# Finviz Free MCP Server

A free Model Context Protocol (MCP) server that provides stock market data and screening capabilities using the `finvizfinance` package. No API keys or subscriptions required!

## Features

### Stock Information
- **get_stock_quote**: Get detailed quote information for any stock ticker
- **get_stock_fundamentals**: Get comprehensive fundamental analysis data
- **get_stock_news**: Get recent news articles for a specific stock

### Stock Screening
- **screen_stocks_overview**: Screen stocks using general overview filters
- **screen_stocks_valuation**: Screen stocks using valuation metrics (P/E, P/B, etc.)
- **screen_stocks_performance**: Screen stocks using performance metrics
- **screen_stocks_technical**: Screen stocks using technical indicators
- **screen_stocks_financial**: Screen stocks using financial statement filters
- **screen_stocks_ownership**: Screen stocks by ownership metrics
- **screen_stocks_ticker**: Return only ticker symbols for a given screener
- **compare_stocks**: Compare a stock with peers by sector, industry, or country

### Market & News Data
- **get_market_news**: Get general market news and blog posts
- **get_insider_trading**: Get insider trading information (latest, top week, etc.)

### Forex / Crypto / Futures
- **get_forex_performance**: Get current forex performance (percent or PIPS)
- **get_forex_chart**: Retrieve forex chart URLs or download images
- **get_crypto_performance**: Get cryptocurrency performance data
- **get_crypto_chart**: Retrieve crypto chart URLs or download images
- **get_future_performance**: Get futures performance for various timeframes

### Calendar & Earnings
- **get_earnings_calendar**: Fetch upcoming or past earnings calendar data
- **get_economic_calendar**: Get economic calendar information
- **export_earnings_csv**: Save earnings calendar data to CSV files
- **export_earnings_excel**: Save earnings calendar data to an Excel workbook

### Additional Details
All tools are exposed via a standard MCP `list_tools` call so clients can discover them dynamically. See the example usage section below for JSON payloads.

## Installation

1. Clone or create the project directory:
```bash
mkdir finviz-free-mcp
cd finviz-free-mcp
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

The server uses the free `finvizfinance` package to access Finviz data without requiring any API keys.

### Example Usage

1. **Get stock quote:**
```json
{
  "tool": "get_stock_quote",
  "arguments": {"ticker": "AAPL"}
}
```

2. **Screen for large-cap technology stocks:**
```json
{
  "tool": "screen_stocks_overview",
  "arguments": {
    "filters": {
      "Market Cap": "+Large",
      "Sector": "Technology"
    }
  }
}
```

3. **Find undervalued stocks:**
```json
{
  "tool": "screen_stocks_valuation",
  "arguments": {
    "filters": {
      "P/E": "<20",
      "P/B": "<2"
    }
  }
}
```

## Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "finviz": {
      "command": "/path/to/finviz-free-mcp/venv/bin/python",
      "args": ["/path/to/finviz-free-mcp/src/finviz_free_mcp/server.py"],
      "cwd": "/path/to/finviz-free-mcp",
      "type": "stdio"
    }
  }
}
```

## Dependencies

- `finvizfinance`: Free package for accessing Finviz data
- `mcp`: Model Context Protocol server framework
- `pandas`: Data manipulation and analysis

## Advantages

- **Free**: No API keys, subscriptions, or rate limits
- **Simple**: Easy to set up and use
- **Comprehensive**: Access to stock quotes, fundamentals, news, and screening
- **Fast**: Direct access to Finviz data

## Limitations

- Data is limited to what's freely available on Finviz
- No historical data or advanced analytics
- Depends on Finviz website availability

## License

MIT License