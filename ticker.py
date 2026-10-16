"""Live terminal board: ticker, price, % change and a block-character graph of today's session."""
import json
import shutil
import sys
import time
from datetime import datetime
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


def render(tickers):
    import yfinance as yf  # imported here so the graph test runs without yfinance

    data = yf.download(tickers, period="1d", interval="1m", group_by="ticker",
                       progress=False, threads=True, auto_adjust=True)
    width = max(shutil.get_terminal_size().columns - 31, 0)  # 30 cols of text + 1 margin
    lines = [f"{BOLD}{'SYMBOL':<8} {'PRICE':>10} {'CHANGE':>8}  {'TODAY':<{width}}{RESET}"]
    for sym in tickers:
        try:
            closes = data[sym]["Close"].dropna().tolist()
            first, last = closes[0], closes[-1]
        except (KeyError, IndexError):
            lines.append(f"{sym:<8} {'n/a':>10}")
            continue
        pct = (last / first - 1) * 100
        color = GREEN if pct >= 0 else RED
        lines.append(f"{color}{sym:<8} {last:>10.2f} {pct:>+7.2f}%  {spark(closes, width)}{RESET}")
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
