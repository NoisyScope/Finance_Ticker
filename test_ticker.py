import pandas as pd
from ticker import change, spark

assert spark([1, 2, 3, 4, 5, 6, 7, 8], 8) == "▁▂▃▄▅▆▇█"
assert spark([5, 5, 5], 10) == "▄" * 10
assert len(spark(list(range(390)), 50)) == 50
assert spark([], 10) == ""
s = pd.Series([100.0, 110.0, 120.0, 130.0],
              index=pd.to_datetime(["2026-09-15", "2026-10-08", "2026-10-15", "2026-10-16"]))
assert round(change(s, 130, 1), 2) == 8.33     # vs previous bar (120)
assert round(change(s, 130, 7), 2) == 18.18    # vs last close on/before 10-09 (110)
assert round(change(s, 130, 30), 2) == 30.0    # vs last close on/before 09-16 (100)
assert change(s, 130, 90) is None              # not enough history
print("ok")
