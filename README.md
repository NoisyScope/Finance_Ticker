# Finance_Ticker
Finance Ticker

Live terminal ticker board powered by `yfinance`. Edit `tickers.json`, then:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python ticker.py        # refresh every 60s; `python ticker.py 30` for 30s
```
