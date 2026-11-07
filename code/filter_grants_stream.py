"""Stream-filter the national grants & contributions CSV (stdin) to rows mentioning tariffs (stdout)."""
import sys, io, re, csv
csv.field_size_limit(10 ** 8)
inp = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8-sig", errors="replace", newline="")
out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
rd, w = csv.reader(inp), csv.writer(out)
w.writerow(next(rd))
pat = re.compile(r"tarif|tariff|pivot to grow|strategic response fund|fonds de r.ponse strat|work-sharing|travail partag|countermeasure|contre-mesures", re.I)
for row in rd:
    if pat.search("|".join(row)):
        w.writerow(row)
out.flush()
