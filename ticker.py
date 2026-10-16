"""Live terminal board: ticker, price, day/week/month % change and a block graph of today."""
import json
import shutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

BARS = "▁▂▃▄▅▆▇█"
REFRESH = 60  # seconds; override with `python ticker.py 30`
GREEN, RED, BOLD, RESET = "\033[32m", "\033[31m", "\033[1;4m", "\033[0m"


def spark(values, width):
    """Resample values to `width` points and map each to a block character."""
    if not values or width <= 0:
        return ""
    pts = [values[round(i * (len(values) - 1) / max(width - 1, 1))] for i in range(width)]
    lo, hi = min(pts), max(pts)
    if hi == lo:
        return BARS[3] * width
    return "".join(BARS[int((v - lo) / (hi - lo) * (len(BARS) - 1))] for v in pts)


def change(daily, last, days):
    """% change of `last` vs the latest daily close at least `days` before the newest bar."""
    base = daily[daily.index <= daily.index[-1] - timedelta(days=days)]
    return (last / base.iloc[-1] - 1) * 100 if len(base) else None


def fmt(pct):
    if pct is None:
        return f"{'n/a':>8}"
    return f"{GREEN if pct >= 0 else RED}{pct:>+7.2f}%{RESET}"


def render(tickers):
    import yfinance as yf  # imported here so the graph test runs without yfinance

    opts = dict(group_by="ticker", progress=False, threads=True, auto_adjust=True)
    intraday = yf.download(tickers, period="1d", interval="1m", **opts)
    daily = yf.download(tickers, period="2mo", interval="1d", **opts)
    width = max(shutil.get_terminal_size().columns - 49, 0)  # 48 cols of text + 1 margin
    lines = [f"{BOLD}{'SYMBOL':<8} {'PRICE':>10} {'DAY':>8} {'WEEK':>8} {'MONTH':>8}  "
             f"{'TODAY':<{width}}{RESET}"]
    for sym in tickers:
        try:
            closes = intraday[sym]["Close"].dropna().tolist()
            last = closes[-1]
            d = daily[sym]["Close"].dropna()
            day, week, month = (change(d, last, n) for n in (1, 7, 30))
        except (KeyError, IndexError):
            lines.append(f"{sym:<8} {'n/a':>10}")
            continue
        color = RED if day is not None and day < 0 else GREEN
        lines.append(f"{sym:<8} {last:>10.2f} {fmt(day)} {fmt(week)} {fmt(month)}  "
                     f"{color}{spark(closes, width)}{RESET}")
    print("\033[H\033[2J", end="")
    print("\n".join(lines)
          + f"\n\nupdated {datetime.now():%H:%M:%S}  (Ctrl+C to quit)", flush=True)


def main():
    refresh = int(sys.argv[1]) if len(sys.argv) > 1 else REFRESH
    tickers = json.loads(Path(__file__).with_name("tickers.json").read_text())
    try:
        while True:
            try:
                render(tickers)
            except Exception as e:  # network hiccup: keep the loop alive
                print(f"fetch failed: {e}", file=sys.stderr)
            time.sleep(refresh)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
