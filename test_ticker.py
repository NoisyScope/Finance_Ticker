from ticker import spark

assert spark([1, 2, 3, 4, 5, 6, 7, 8], 8) == "▁▂▃▄▅▆▇█"
assert spark([5, 5, 5], 10) == "▄" * 10
assert len(spark(list(range(390)), 50)) == 50
assert spark([], 10) == ""
print("ok")
