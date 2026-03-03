#!/usr/bin/env python3

import asyncio
import logging
from typing import List, Dict, Any, Optional
import json
import pandas as pd

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool

from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.valuation import Valuation
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ticker import Ticker
from finvizfinance.news import News
from finvizfinance.insider import Insider
from finvizfinance.forex import Forex
from finvizfinance.crypto import Crypto
from finvizfinance.future import Future
from finvizfinance.earnings import Earnings
from finvizfinance.calendar import Calendar

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("finviz-free-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_stock_quote",
            description="Get detailed quote information for a stock ticker",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_stock_fundamentals",
            description="Get fundamental data for a stock ticker",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_stock_news",
            description="Get recent news for a stock ticker",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="screen_stocks_overview",
            description="Screen stocks using overview filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filters to apply (e.g., {'Market Cap': '+Large', 'Sector': 'Technology'})"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="screen_stocks_valuation",
            description="Screen stocks using valuation filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Valuation filters (e.g., {'P/E': '<20', 'P/B': '<2'})"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="screen_stocks_performance",
            description="Screen stocks using performance filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Performance filters (e.g., {'Perf Week': '+5%', 'Perf Month': '+10%'})"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="screen_stocks_technical",
            description="Screen stocks using technical filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Technical filters (e.g., {'RSI': '<30', 'Price': 'Above SMA200'})"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_market_news",
            description="Get general market news from Finviz",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_insider_trading",
            description="Get insider trading information",
            inputSchema={
                "type": "object",
                "properties": {
                    "option": {
                        "type": "string",
                        "description": "Type of insider info: 'latest', 'top week', or 'top owner trade'",
                        "default": "latest"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="screen_stocks_financial",
            description="Screen stocks using financial filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Financial filters (e.g., {'Debt/Eq': '<0.5', 'ROE': '>15%'})"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="screen_stocks_ownership",
            description="Screen stocks using ownership filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Ownership filters (e.g., {'Insider Own': '>10%', 'Inst Own': '<50%'})"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="screen_stocks_ticker",
            description="Screen stocks and return ticker symbols only",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Filters to apply for ticker screening"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tickers to return (default: -1 for all)",
                        "default": -1
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="compare_stocks",
            description="Compare a stock with similar stocks by sector, industry, or country",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol to compare"
                    },
                    "compare_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Properties to compare by: 'Sector', 'Industry', 'Country'"
                    },
                    "screener_type": {
                        "type": "string",
                        "description": "Type of screener: 'overview', 'valuation', 'financial', 'ownership', 'performance', 'technical'",
                        "default": "overview"
                    },
                    "order": {
                        "type": "string",
                        "description": "Column to order results by",
                        "default": "ticker"
                    }
                },
                "required": ["ticker", "compare_list"]
            }
        ),
        Tool(
            name="get_forex_performance",
            description="Get forex performance data",
            inputSchema={
                "type": "object",
                "properties": {
                    "change": {
                        "type": "string",
                        "description": "Change format: 'percent' or 'PIPS'",
                        "default": "percent"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_forex_chart",
            description="Get forex chart URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "forex": {
                        "type": "string",
                        "description": "Foreign exchange pair (e.g., 'EUR/USD', 'GBP/USD')"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Chart timeframe: '5M', 'H', 'D', 'W', 'M'",
                        "default": "D"
                    },
                    "url_only": {
                        "type": "boolean",
                        "description": "Return only URL (true) or download chart (false)",
                        "default": True
                    }
                },
                "required": ["forex"]
            }
        ),
        Tool(
            name="get_crypto_performance",
            description="Get cryptocurrency performance data",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_crypto_chart",
            description="Get cryptocurrency chart URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "crypto": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'ADA')"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Chart timeframe: '5M', 'H', 'D', 'W', 'M'",
                        "default": "D"
                    },
                    "url_only": {
                        "type": "boolean",
                        "description": "Return only URL (true) or download chart (false)",
                        "default": True
                    }
                },
                "required": ["crypto"]
            }
        ),
        Tool(
            name="get_future_performance",
            description="Get future performance data",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "description": "Performance timeframe: 'D', 'W', 'M', 'Q', 'HY', 'Y'",
                        "default": "D"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_earnings_calendar",
            description="Get earnings calendar for a specific period",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Earnings period: 'This Week', 'Next Week', 'Previous Week', 'This Month'",
                        "default": "This Week"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Data mode: 'financial', 'overview', 'valuation', 'ownership', 'performance', 'technical'",
                        "default": "financial"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_economic_calendar",
            description="Get economic calendar information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="export_earnings_csv",
            description="Export earnings calendar data to CSV files",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Earnings period: 'This Week', 'Next Week', 'Previous Week', 'This Month'",
                        "default": "This Week"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Name of the output directory",
                        "default": "earning_days"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="export_earnings_excel",
            description="Export earnings calendar data to Excel file",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Earnings period: 'This Week', 'Next Week', 'Previous Week', 'This Month'",
                        "default": "This Week"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Name of the output Excel file",
                        "default": "earning_days.xlsx"
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "get_stock_quote":
            return await get_stock_quote(arguments["ticker"])

        elif name == "get_stock_fundamentals":
            return await get_stock_fundamentals(arguments["ticker"])

        elif name == "get_stock_news":
            return await get_stock_news(arguments["ticker"])

        elif name == "screen_stocks_overview":
            filters = arguments.get("filters", {})
            return await screen_stocks_overview(filters)

        elif name == "screen_stocks_valuation":
            filters = arguments.get("filters", {})
            return await screen_stocks_valuation(filters)

        elif name == "screen_stocks_performance":
            filters = arguments.get("filters", {})
            return await screen_stocks_performance(filters)

        elif name == "screen_stocks_technical":
            filters = arguments.get("filters", {})
            return await screen_stocks_technical(filters)

        elif name == "get_market_news":
            return await get_market_news()

        elif name == "get_insider_trading":
            option = arguments.get("option", "latest")
            return await get_insider_trading(option)

        elif name == "screen_stocks_financial":
            filters = arguments.get("filters", {})
            return await screen_stocks_financial(filters)

        elif name == "screen_stocks_ownership":
            filters = arguments.get("filters", {})
            return await screen_stocks_ownership(filters)

        elif name == "screen_stocks_ticker":
            filters = arguments.get("filters", {})
            limit = arguments.get("limit", -1)
            return await screen_stocks_ticker(filters, limit)

        elif name == "compare_stocks":
            ticker = arguments["ticker"]
            compare_list = arguments["compare_list"]
            screener_type = arguments.get("screener_type", "overview")
            order = arguments.get("order", "ticker")
            return await compare_stocks(ticker, compare_list, screener_type, order)

        elif name == "get_forex_performance":
            change = arguments.get("change", "percent")
            return await get_forex_performance(change)

        elif name == "get_forex_chart":
            forex = arguments["forex"]
            timeframe = arguments.get("timeframe", "D")
            url_only = arguments.get("url_only", True)
            return await get_forex_chart(forex, timeframe, url_only)

        elif name == "get_crypto_performance":
            return await get_crypto_performance()

        elif name == "get_crypto_chart":
            crypto = arguments["crypto"]
            timeframe = arguments.get("timeframe", "D")
            url_only = arguments.get("url_only", True)
            return await get_crypto_chart(crypto, timeframe, url_only)

        elif name == "get_future_performance":
            timeframe = arguments.get("timeframe", "D")
            return await get_future_performance(timeframe)

        elif name == "get_earnings_calendar":
            period = arguments.get("period", "This Week")
            mode = arguments.get("mode", "financial")
            return await get_earnings_calendar(period, mode)

        elif name == "get_economic_calendar":
            return await get_economic_calendar()

        elif name == "export_earnings_csv":
            period = arguments.get("period", "This Week")
            output_dir = arguments.get("output_dir", "earning_days")
            return await export_earnings_csv(period, output_dir)

        elif name == "export_earnings_excel":
            period = arguments.get("period", "This Week")
            output_file = arguments.get("output_file", "earning_days.xlsx")
            return await export_earnings_excel(period, output_file)

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def get_stock_quote(ticker: str) -> List[TextContent]:
    """Get stock quote information."""
    try:
        stock = finvizfinance(ticker.upper())
        fundament = stock.ticker_fundament()

        if not fundament:
            return [TextContent(type="text", text=f"No data found for ticker: {ticker}")]

        # Format the fundamental data nicely
        result = f"**{ticker.upper()} Stock Information**\n\n"

        # Basic info
        if 'Company' in fundament:
            result += f"**Company:** {fundament['Company']}\n"
        if 'Sector' in fundament:
            result += f"**Sector:** {fundament['Sector']}\n"
        if 'Industry' in fundament:
            result += f"**Industry:** {fundament['Industry']}\n"

        result += "\n**Key Metrics:**\n"

        # Price info
        key_metrics = ['Market Cap', 'P/E', 'Price', 'Change', 'Volume']
        for metric in key_metrics:
            if metric in fundament:
                result += f"- {metric}: {fundament[metric]}\n"

        result += "\n**Performance:**\n"
        perf_metrics = ['Perf Week', 'Perf Month', 'Perf Quarter', 'Perf Half Y', 'Perf Year']
        for metric in perf_metrics:
            if metric in fundament:
                result += f"- {metric}: {fundament[metric]}\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting quote for {ticker}: {str(e)}")]

async def get_stock_fundamentals(ticker: str) -> List[TextContent]:
    """Get detailed fundamental data."""
    try:
        stock = finvizfinance(ticker.upper())
        fundament = stock.ticker_fundament()

        if not fundament:
            return [TextContent(type="text", text=f"No fundamental data found for ticker: {ticker}")]

        result = f"**{ticker.upper()} Fundamental Analysis**\n\n"

        # Organize data by categories
        categories = {
            "Company Info": ["Company", "Sector", "Industry", "Country", "Exchange"],
            "Valuation": ["Market Cap", "P/E", "Forward P/E", "PEG", "P/S", "P/B", "P/C", "P/FCF"],
            "Profitability": ["EPS (ttm)", "EPS next Y", "EPS next Q", "EPS this Y", "EPS next 5Y", "ROA", "ROE", "ROI"],
            "Financial": ["Debt/Eq", "LT Debt/Eq", "Quick Ratio", "Current Ratio", "Gross Margin", "Oper. Margin", "Profit Margin"],
            "Trading": ["Volume", "Avg Volume", "Rel Volume", "Price", "Change", "Volatility"],
            "Ownership": ["Insider Own", "Insider Trans", "Inst Own", "Inst Trans", "Short Float", "Short Ratio"]
        }

        for category, metrics in categories.items():
            result += f"**{category}:**\n"
            found_any = False
            for metric in metrics:
                if metric in fundament and fundament[metric] not in ['-', '']:
                    result += f"- {metric}: {fundament[metric]}\n"
                    found_any = True
            if not found_any:
                result += "- No data available\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting fundamentals for {ticker}: {str(e)}")]

async def get_stock_news(ticker: str) -> List[TextContent]:
    """Get recent news for a stock."""
    try:
        stock = finvizfinance(ticker.upper())
        news_df = stock.ticker_news()

        if news_df.empty:
            return [TextContent(type="text", text=f"No news found for ticker: {ticker}")]

        result = f"**Recent News for {ticker.upper()}**\n\n"

        # Show first 10 news items
        for i, row in news_df.head(10).iterrows():
            result += f"**{row['Title']}**\n"
            result += f"Date: {row['Date']}\n"
            if 'Link' in row and pd.notna(row['Link']):
                result += f"Link: {row['Link']}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting news for {ticker}: {str(e)}")]

async def screen_stocks_overview(filters: Dict[str, Any]) -> List[TextContent]:
    """Screen stocks using overview filters."""
    try:
        foverview = Overview()

        if filters:
            foverview.set_filter(filters_dict=filters)

        df = foverview.screener_view()

        if df.empty:
            return [TextContent(type="text", text="No stocks found matching the criteria")]

        result = "**Stock Screen Results (Overview)**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(df)} stocks:**\n\n"

        # Show first 20 results
        for i, row in df.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')
            sector = row.get('Sector', 'N/A')
            market_cap = row.get('Market Cap', 'N/A')
            price = row.get('Price', 'N/A')
            change = row.get('Change', 'N/A')

            result += f"**{ticker}** - {company}\n"
            result += f"Sector: {sector} | Market Cap: {market_cap} | Price: {price} | Change: {change}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening stocks: {str(e)}")]

async def screen_stocks_valuation(filters: Dict[str, Any]) -> List[TextContent]:
    """Screen stocks using valuation filters."""
    try:
        fvaluation = Valuation()

        if filters:
            fvaluation.set_filter(filters_dict=filters)

        df = fvaluation.screener_view()

        if df.empty:
            return [TextContent(type="text", text="No stocks found matching the valuation criteria")]

        result = "**Stock Screen Results (Valuation)**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(df)} stocks:**\n\n"

        # Show first 20 results with valuation focus
        for i, row in df.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')
            pe = row.get('P/E', 'N/A')
            pb = row.get('P/B', 'N/A')
            ps = row.get('P/S', 'N/A')
            price = row.get('Price', 'N/A')

            result += f"**{ticker}** - {company}\n"
            result += f"P/E: {pe} | P/B: {pb} | P/S: {ps} | Price: {price}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening stocks by valuation: {str(e)}")]

async def screen_stocks_performance(filters: Dict[str, Any]) -> List[TextContent]:
    """Screen stocks using performance filters."""
    try:
        fperformance = Performance()

        if filters:
            fperformance.set_filter(filters_dict=filters)

        df = fperformance.screener_view()

        if df.empty:
            return [TextContent(type="text", text="No stocks found matching the performance criteria")]

        result = "**Stock Screen Results (Performance)**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(df)} stocks:**\n\n"

        # Show first 20 results with performance focus
        for i, row in df.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')
            perf_week = row.get('Perf Week', 'N/A')
            perf_month = row.get('Perf Month', 'N/A')
            perf_year = row.get('Perf Year', 'N/A')

            result += f"**{ticker}** - {company}\n"
            result += f"Week: {perf_week} | Month: {perf_month} | Year: {perf_year}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening stocks by performance: {str(e)}")]

async def screen_stocks_technical(filters: Dict[str, Any]) -> List[TextContent]:
    """Screen stocks using technical filters."""
    try:
        ftechnical = Technical()

        if filters:
            ftechnical.set_filter(filters_dict=filters)

        df = ftechnical.screener_view()

        if df.empty:
            return [TextContent(type="text", text="No stocks found matching the technical criteria")]

        result = "**Stock Screen Results (Technical)**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(df)} stocks:**\n\n"

        # Show first 20 results with technical focus
        for i, row in df.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')
            rsi = row.get('RSI (14)', 'N/A')
            price = row.get('Price', 'N/A')
            volume = row.get('Volume', 'N/A')

            result += f"**{ticker}** - {company}\n"
            result += f"RSI: {rsi} | Price: {price} | Volume: {volume}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening stocks by technical: {str(e)}")]

async def get_market_news() -> List[TextContent]:
    """Get general market news."""
    try:
        fnews = News()
        all_news = fnews.get_news()

        result = "**Recent Market News**\n\n"

        # Get news
        if 'news' in all_news and not all_news['news'].empty:
            result += "**News:**\n"
            for i, row in all_news['news'].head(10).iterrows():
                result += f"- **{row['Title']}**\n"
                result += f"  Date: {row['Date']} | Link: {row.get('Link', 'N/A')}\n\n"

        # Get blogs if available
        if 'blogs' in all_news and not all_news['blogs'].empty:
            result += "\n**Blogs:**\n"
            for i, row in all_news['blogs'].head(5).iterrows():
                result += f"- **{row['Title']}**\n"
                result += f"  Date: {row['Date']} | Link: {row.get('Link', 'N/A')}\n\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting market news: {str(e)}")]

async def get_insider_trading(option: str = "latest") -> List[TextContent]:
    """Get insider trading information."""
    try:
        finsider = Insider(option=option)
        insider_data = finsider.get_insider()

        if insider_data.empty:
            return [TextContent(type="text", text=f"No insider trading data found for option: {option}")]

        result = f"**Insider Trading ({option})**\n\n"

        # Show first 20 insider transactions
        for i, row in insider_data.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            owner = row.get('Owner', 'N/A')
            relationship = row.get('Relationship', 'N/A')
            transaction = row.get('Transaction', 'N/A')
            cost = row.get('#Shares', 'N/A')
            value = row.get('Value ($)', 'N/A')

            result += f"**{ticker}** - {owner}\n"
            result += f"Relationship: {relationship}\n"
            result += f"Transaction: {transaction} | Shares: {cost} | Value: {value}\n\n"

        if len(insider_data) > 20:
            result += f"\n... and {len(insider_data) - 20} more transactions"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting insider trading data: {str(e)}")]

async def screen_stocks_financial(filters: Dict[str, Any]) -> List[TextContent]:
    """Screen stocks using financial filters."""
    try:
        ffinancial = Financial()

        if filters:
            ffinancial.set_filter(filters_dict=filters)

        df = ffinancial.screener_view()

        if df.empty:
            return [TextContent(type="text", text="No stocks found matching the financial criteria")]

        result = "**Stock Screen Results (Financial)**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(df)} stocks:**\n\n"

        # Show first 20 results with financial focus
        for i, row in df.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')
            debt_eq = row.get('Debt/Eq', 'N/A')
            roe = row.get('ROE', 'N/A')
            roa = row.get('ROA', 'N/A')
            gross_margin = row.get('Gross Margin', 'N/A')

            result += f"**{ticker}** - {company}\n"
            result += f"Debt/Eq: {debt_eq} | ROE: {roe} | ROA: {roa} | Gross Margin: {gross_margin}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening stocks by financial: {str(e)}")]

async def screen_stocks_ownership(filters: Dict[str, Any]) -> List[TextContent]:
    """Screen stocks using ownership filters."""
    try:
        fownership = Ownership()

        if filters:
            fownership.set_filter(filters_dict=filters)

        df = fownership.screener_view()

        if df.empty:
            return [TextContent(type="text", text="No stocks found matching the ownership criteria")]

        result = "**Stock Screen Results (Ownership)**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(df)} stocks:**\n\n"

        # Show first 20 results with ownership focus
        for i, row in df.head(20).iterrows():
            ticker = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')
            insider_own = row.get('Insider Own', 'N/A')
            inst_own = row.get('Inst Own', 'N/A')
            short_float = row.get('Short Float', 'N/A')
            short_ratio = row.get('Short Ratio', 'N/A')

            result += f"**{ticker}** - {company}\n"
            result += f"Insider Own: {insider_own} | Inst Own: {inst_own} | Short Float: {short_float} | Short Ratio: {short_ratio}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening stocks by ownership: {str(e)}")]

async def screen_stocks_ticker(filters: Dict[str, Any], limit: int = -1) -> List[TextContent]:
    """Screen stocks and return ticker symbols only."""
    try:
        fticker = Ticker()

        if filters:
            fticker.set_filter(filters_dict=filters)

        tickers = fticker.screener_view(limit=limit)

        if not tickers:
            return [TextContent(type="text", text="No tickers found matching the criteria")]

        result = "**Ticker Screen Results**\n\n"
        if filters:
            result += f"**Filters Applied:** {json.dumps(filters, indent=2)}\n\n"

        result += f"**Found {len(tickers)} tickers:**\n\n"

        # Format tickers in rows of 10
        ticker_chunks = [tickers[i:i+10] for i in range(0, len(tickers), 10)]
        for chunk in ticker_chunks:
            result += " | ".join(chunk) + "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error screening tickers: {str(e)}")]

async def compare_stocks(ticker: str, compare_list: List[str], screener_type: str = "overview", order: str = "ticker") -> List[TextContent]:
    """Compare a stock with similar stocks by sector, industry, or country."""
    try:
        # Map screener types to classes
        screener_map = {
            "overview": Overview(),
            "valuation": Valuation(),
            "financial": Financial(),
            "ownership": Ownership(),
            "performance": Performance(),
            "technical": Technical()
        }

        if screener_type not in screener_map:
            return [TextContent(type="text", text=f"Invalid screener type: {screener_type}. Use one of: {list(screener_map.keys())}")]

        screener = screener_map[screener_type]
        df = screener.compare(ticker=ticker.upper(), compare_list=compare_list, order=order)

        if df.empty:
            return [TextContent(type="text", text=f"No comparison data found for {ticker} with criteria: {compare_list}")]

        result = f"**Stock Comparison Results for {ticker.upper()}**\n\n"
        result += f"**Comparison Criteria:** {', '.join(compare_list)}\n"
        result += f"**Screener Type:** {screener_type}\n"
        result += f"**Ordered By:** {order}\n\n"
        result += f"**Found {len(df)} similar stocks:**\n\n"

        # Show first 20 results
        for i, row in df.head(20).iterrows():
            ticker_symbol = row.get('Ticker', 'N/A')
            company = row.get('Company', 'N/A')

            # Get relevant metrics based on screener type
            if screener_type == "valuation":
                pe = row.get('P/E', 'N/A')
                pb = row.get('P/B', 'N/A')
                result += f"**{ticker_symbol}** - {company} | P/E: {pe} | P/B: {pb}\n"
            elif screener_type == "financial":
                roe = row.get('ROE', 'N/A')
                debt_eq = row.get('Debt/Eq', 'N/A')
                result += f"**{ticker_symbol}** - {company} | ROE: {roe} | Debt/Eq: {debt_eq}\n"
            elif screener_type == "performance":
                perf_week = row.get('Perf Week', 'N/A')
                perf_month = row.get('Perf Month', 'N/A')
                result += f"**{ticker_symbol}** - {company} | Week: {perf_week} | Month: {perf_month}\n"
            elif screener_type == "ownership":
                insider_own = row.get('Insider Own', 'N/A')
                inst_own = row.get('Inst Own', 'N/A')
                result += f"**{ticker_symbol}** - {company} | Insider Own: {insider_own} | Inst Own: {inst_own}\n"
            elif screener_type == "technical":
                rsi = row.get('RSI (14)', 'N/A')
                price = row.get('Price', 'N/A')
                result += f"**{ticker_symbol}** - {company} | RSI: {rsi} | Price: {price}\n"
            else:  # overview
                sector = row.get('Sector', 'N/A')
                market_cap = row.get('Market Cap', 'N/A')
                result += f"**{ticker_symbol}** - {company} | Sector: {sector} | Market Cap: {market_cap}\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more stocks"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error comparing stocks: {str(e)}")]

async def get_forex_performance(change: str = "percent") -> List[TextContent]:
    """Get forex performance data."""
    try:
        fforex = Forex()
        df = fforex.performance(change=change)

        if df.empty:
            return [TextContent(type="text", text="No forex performance data available")]

        result = f"**Forex Performance ({change})**\n\n"
        result += f"**Found {len(df)} currency pairs:**\n\n"

        # Show all results
        for i, row in df.iterrows():
            pair = row.get('Currency', 'N/A')
            price = row.get('Price', 'N/A')
            change_val = row.get('Change', 'N/A')
            volume = row.get('Volume', 'N/A')

            result += f"**{pair}**\n"
            result += f"Price: {price} | Change: {change_val} | Volume: {volume}\n\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting forex performance: {str(e)}")]

async def get_forex_chart(forex: str, timeframe: str = "D", url_only: bool = True) -> List[TextContent]:
    """Get forex chart URL."""
    try:
        fforex = Forex()
        chart_url = fforex.chart(forex=forex, timeframe=timeframe, urlonly=url_only)

        if not chart_url:
            return [TextContent(type="text", text=f"No chart available for {forex}")]

        result = f"**Forex Chart for {forex}**\n\n"
        result += f"**Timeframe:** {timeframe}\n"
        result += f"**Chart URL:** {chart_url}\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting forex chart: {str(e)}")]

async def get_crypto_performance() -> List[TextContent]:
    """Get cryptocurrency performance data."""
    try:
        fcrypto = Crypto()
        df = fcrypto.performance()

        if df.empty:
            return [TextContent(type="text", text="No cryptocurrency performance data available")]

        result = "**Cryptocurrency Performance**\n\n"
        result += f"**Found {len(df)} cryptocurrencies:**\n\n"

        # Show first 20 results
        for i, row in df.head(20).iterrows():
            crypto = row.get('Cryptocurrency', 'N/A')
            price = row.get('Price', 'N/A')
            change = row.get('Change', 'N/A')
            volume = row.get('Volume', 'N/A')
            market_cap = row.get('Market Cap', 'N/A')

            result += f"**{crypto}**\n"
            result += f"Price: {price} | Change: {change} | Volume: {volume} | Market Cap: {market_cap}\n\n"

        if len(df) > 20:
            result += f"\n... and {len(df) - 20} more cryptocurrencies"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting crypto performance: {str(e)}")]

async def get_crypto_chart(crypto: str, timeframe: str = "D", url_only: bool = True) -> List[TextContent]:
    """Get cryptocurrency chart URL."""
    try:
        fcrypto = Crypto()
        chart_url = fcrypto.chart(crypto=crypto, timeframe=timeframe, urlonly=url_only)

        if not chart_url:
            return [TextContent(type="text", text=f"No chart available for {crypto}")]

        result = f"**Crypto Chart for {crypto}**\n\n"
        result += f"**Timeframe:** {timeframe}\n"
        result += f"**Chart URL:** {chart_url}\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting crypto chart: {str(e)}")]

async def get_future_performance(timeframe: str = "D") -> List[TextContent]:
    """Get future performance data."""
    try:
        ffuture = Future()
        df = ffuture.performance(timeframe=timeframe)

        if df.empty:
            return [TextContent(type="text", text="No future performance data available")]

        result = f"**Future Performance ({timeframe})**\n\n"
        result += f"**Found {len(df)} futures:**\n\n"

        # Show all results
        for i, row in df.iterrows():
            future = row.get('Future', 'N/A')
            price = row.get('Price', 'N/A')
            change = row.get('Change', 'N/A')
            volume = row.get('Volume', 'N/A')

            result += f"**{future}**\n"
            result += f"Price: {price} | Change: {change} | Volume: {volume}\n\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting future performance: {str(e)}")]

async def get_earnings_calendar(period: str = "This Week", mode: str = "financial") -> List[TextContent]:
    """Get earnings calendar for a specific period."""
    try:
        fearnings = Earnings(period=period)
        earnings_data = fearnings.partition_days(mode=mode)

        if not earnings_data:
            return [TextContent(type="text", text=f"No earnings data available for {period}")]

        result = f"**Earnings Calendar - {period}**\n"
        result += f"**Mode:** {mode}\n\n"

        # earnings_data is a dictionary of dataframes by date
        for date, df in earnings_data.items():
            if df.empty:
                continue

            result += f"**{date}:**\n"
            for i, row in df.head(10).iterrows():  # Show first 10 per date
                ticker = row.get('Ticker', 'N/A')
                company = row.get('Company', 'N/A')
                time = row.get('Time', 'N/A')

                result += f"- **{ticker}** ({company}) - {time}\n"

                # Add relevant data based on mode
                if mode == "financial" and 'EPS' in row:
                    eps = row.get('EPS', 'N/A')
                    result += f"  EPS: {eps}\n"
                elif mode == "overview" and 'Market Cap' in row:
                    market_cap = row.get('Market Cap', 'N/A')
                    result += f"  Market Cap: {market_cap}\n"

            if len(df) > 10:
                result += f"  ... and {len(df) - 10} more companies\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting earnings calendar: {str(e)}")]

async def get_economic_calendar() -> List[TextContent]:
    """Get economic calendar information."""
    try:
        fcalendar = Calendar()
        df = fcalendar.calendar()

        if df.empty:
            return [TextContent(type="text", text="No economic calendar data available")]

        result = "**Economic Calendar**\n\n"
        result += f"**Found {len(df)} events:**\n\n"

        # Show all events
        for i, row in df.iterrows():
            time = row.get('Time', 'N/A')
            event = row.get('Event', 'N/A')
            actual = row.get('Actual', 'N/A')
            forecast = row.get('Forecast', 'N/A')
            previous = row.get('Previous', 'N/A')

            result += f"**{time}** - {event}\n"
            if actual != 'N/A' or forecast != 'N/A' or previous != 'N/A':
                result += f"Actual: {actual} | Forecast: {forecast} | Previous: {previous}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting economic calendar: {str(e)}")]

async def export_earnings_csv(period: str = "This Week", output_dir: str = "earning_days") -> List[TextContent]:
    """Export earnings calendar data to CSV files."""
    try:
        import os

        fearnings = Earnings(period=period)

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Export to CSV
        fearnings.output_csv(output_dir=output_dir)

        # List the files created
        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]

        result = f"**Earnings Calendar CSV Export - {period}**\n\n"
        result += f"**Output Directory:** {output_dir}\n"
        result += f"**Files Created:** {len(csv_files)}\n\n"

        for file in sorted(csv_files):
            result += f"- {file}\n"

        result += f"\nCSV files have been saved to the '{output_dir}' directory."

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error exporting earnings to CSV: {str(e)}")]

async def export_earnings_excel(period: str = "This Week", output_file: str = "earning_days.xlsx") -> List[TextContent]:
    """Export earnings calendar data to Excel file."""
    try:
        import os

        fearnings = Earnings(period=period)

        # Export to Excel
        fearnings.output_excel(output_file=output_file)

        # Check if file was created
        file_exists = os.path.exists(output_file)
        file_size = os.path.getsize(output_file) if file_exists else 0

        result = f"**Earnings Calendar Excel Export - {period}**\n\n"
        result += f"**Output File:** {output_file}\n"

        if file_exists:
            result += f"**File Size:** {file_size:,} bytes\n"
            result += f"**Status:** ✅ Successfully created\n\n"
            result += f"Excel file has been saved as '{output_file}'."
        else:
            result += "**Status:** ❌ File creation failed"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error exporting earnings to Excel: {str(e)}")]

async def run_server():
    """Run the server asynchronously."""
    from mcp.server.stdio import stdio_server
    from mcp.server.lowlevel import NotificationOptions

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="finviz-free-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    NotificationOptions(),
                    {}
                )
            )
        )

def main():
    """Main entry point for script."""
    asyncio.run(run_server())

if __name__ == "__main__":
    main()