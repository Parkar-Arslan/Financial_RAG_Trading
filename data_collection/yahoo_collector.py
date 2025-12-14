import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from tqdm import tqdm
import time
import random
import requests

class YahooFinanceCollector:
    """
    Robust Financial Data Collector
    1. Checks local cache first
    2. Tries Yahoo Finance API with backoff
    3. Falls back to mock data if API fails
    """
    
    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def collect_stock_data(self, ticker: str) -> Optional[Dict]:
        """Collect stock data with Cache -> API -> Fallback priority"""
        
        # 1. TRY LOCAL CACHE FIRST
        local_file = os.path.join(self.output_dir, f"{ticker}_data.json")
        if os.path.exists(local_file):
            try:
                with open(local_file, 'r') as f:
                    data = json.load(f)
                    # Validate essential fields
                    if data.get('ticker') == ticker and data.get('documents'):
                        # print(f"   📂 Loaded cached data for {ticker}")
                        return data
            except Exception as e:
                print(f"   ⚠️ Cache corrupt for {ticker}, refetching...")

        # 2. TRY YAHOO FINANCE API
        max_retries = 3
        base_wait = 2

        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1.0, 3.0)) # Polite delay
                
                stock = yf.Ticker(ticker, session=self.session)
                
                # Fetch basic info to test connection
                try:
                    info = stock.info
                except:
                    info = {}
                
                if not info and attempt < max_retries - 1:
                    raise ValueError("Empty info received")

                # Fetch history
                try:
                    hist = stock.history(period="1y")
                except:
                    hist = pd.DataFrame()

                # Fetch financials
                try:
                    financials = stock.financials
                except:
                    financials = pd.DataFrame()
                
                # Fetch news
                try:
                    news = stock.news
                except:
                    news = []

                # Build Data Object
                data = {
                    'ticker': ticker,
                    'company_name': info.get('longName', ticker),
                    'sector': info.get('sector', 'Technology'),
                    'industry': info.get('industry', 'Consumer Electronics'),
                    'market_cap': info.get('marketCap', 1000000000),
                    'pe_ratio': info.get('trailingPE', 25.0),
                    'forward_pe': info.get('forwardPE', 20.0),
                    'dividend_yield': info.get('dividendYield', 0.0),
                    'beta': info.get('beta', 1.0),
                    '52_week_high': info.get('fiftyTwoWeekHigh', 100.0),
                    '52_week_low': info.get('fiftyTwoWeekLow', 50.0),
                    'current_price': info.get('currentPrice', hist['Close'].iloc[-1] if not hist.empty else 100.0),
                    'target_price': info.get('targetMeanPrice', 110.0),
                    'revenue': 0,
                    'gross_profit': 0,
                    'operating_income': 0,
                    'business_summary': info.get('longBusinessSummary', f"Summary for {ticker}"),
                    'recent_news': news[:5] if news else [],
                    'analyst_recommendation': info.get('recommendationKey', 'buy'),
                    'collected_date': datetime.now().isoformat()
                }

                # Safe extraction of financials
                if not financials.empty:
                    try:
                        if 'Total Revenue' in financials.index:
                            data['revenue'] = float(financials.loc['Total Revenue'].iloc[0])
                        if 'Gross Profit' in financials.index:
                            data['gross_profit'] = float(financials.loc['Gross Profit'].iloc[0])
                        if 'Operating Income' in financials.index:
                            data['operating_income'] = float(financials.loc['Operating Income'].iloc[0])
                    except:
                        pass

                # Generate RAG Documents
                data['documents'] = self._generate_documents(data, hist, financials)
                
                return data

            except Exception as e:
                wait_time = base_wait * (2 ** attempt)
                if attempt < max_retries - 1:
                    print(f"   ⚠️ Retry {attempt+1}/{max_retries} for {ticker} (Wait {wait_time}s)...")
                    time.sleep(wait_time)
        
        # 3. EMERGENCY FALLBACK (MOCK DATA)
        print(f"   ⚠️ API failed for {ticker}. Generating synthetic data.")
        return self._get_mock_data(ticker)

    def _get_mock_data(self, ticker: str) -> Dict:
        """Generate plausible mock data so the app doesn't crash"""
        mock_price = 150.0
        
        data = {
            'ticker': ticker,
            'company_name': f"{ticker} Corporation",
            'sector': "Technology",
            'industry': "Software",
            'market_cap': 2500000000000,
            'pe_ratio': 30.5,
            'forward_pe': 25.0,
            'dividend_yield': 0.005,
            'beta': 1.2,
            '52_week_high': 180.0,
            '52_week_low': 120.0,
            'current_price': mock_price,
            'target_price': 175.0,
            'revenue': 100000000000,
            'gross_profit': 60000000000,
            'operating_income': 40000000000,
            'business_summary': f"{ticker} is a leading technology company that designs and manufactures consumer electronics and software services.",
            'recent_news': [
                {
                    'title': f"{ticker} announces strong quarterly earnings",
                    'link': '#',
                    'publisher': 'Finance Daily',
                    'published': datetime.now().isoformat()
                },
                {
                    'title': f"Analysts upgrade {ticker} following AI announcements",
                    'link': '#',
                    'publisher': 'Tech News',
                    'published': datetime.now().isoformat()
                }
            ],
            'analyst_recommendation': 'buy',
            'collected_date': datetime.now().isoformat()
        }
        
        # Create synthetic docs
        docs = []
        docs.append({
            'type': 'Company Overview',
            'content': f"Company: {ticker}\nSummary: {data['business_summary']}\nPrice: ${mock_price}",
            'date': datetime.now().isoformat()
        })
        docs.append({
            'type': 'Financial Performance',
            'content': f"Financials for {ticker}:\nRevenue: $100B\nStrong growth expected in 2025.",
            'date': datetime.now().isoformat()
        })
        docs.append({
            'type': 'Trading Signals',
            'content': f"Trading Signals for {ticker}:\n- BULLISH: Strong momentum\n- BULLISH: AI sector growth",
            'date': datetime.now().isoformat()
        })
        
        data['documents'] = docs
        return data

    def _generate_documents(self, data: Dict, hist: pd.DataFrame, financials: pd.DataFrame) -> List[Dict]:
        """Generate text documents from financial data"""
        documents = []
        
        # Company Overview
        overview_doc = f"""
        Company: {data['company_name']} ({data['ticker']})
        Sector: {data['sector']}
        Industry: {data['industry']}
        
        Business Summary:
        {data['business_summary']}
        
        Key Metrics:
        - Market Cap: ${data.get('market_cap', 0):,.0f}
        - P/E Ratio: {data.get('pe_ratio', 0):.2f}
        - Current Price: ${data.get('current_price', 0):.2f}
        - Analyst Recommendation: {data.get('analyst_recommendation', 'N/A')}
        """
        documents.append({
            'type': 'Company Overview',
            'content': overview_doc,
            'date': datetime.now().isoformat()
        })
        
        # Technical Analysis
        if not hist.empty:
            try:
                current = hist['Close'].iloc[-1]
                change_30 = ((current / hist['Close'].iloc[0] - 1) * 100) if len(hist) > 0 else 0
                tech_doc = f"""
                Technical Analysis for {data['ticker']}
                - Current Price: ${current:.2f}
                - 30-Day Change: {change_30:.2f}%
                - 50-Day MA: ${hist['Close'].tail(50).mean():.2f}
                """
                documents.append({
                    'type': 'Technical Analysis',
                    'content': tech_doc,
                    'date': datetime.now().isoformat()
                })
            except:
                pass

        return documents

    def collect_multiple_tickers(self, tickers: List[str]) -> List[Dict]:
        """Collect data for multiple tickers"""
        all_data = []
        for ticker in tickers:
            data = self.collect_stock_data(ticker)
            if data:
                all_data.append(data)
                # Save individual ticker data
                output_file = os.path.join(self.output_dir, f"{ticker}_data.json")
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
        
        if all_data:
            output_file = os.path.join(self.output_dir, "all_stocks_data.json")
            with open(output_file, 'w') as f:
                json.dump(all_data, f, indent=2, default=str)
        
        return all_data