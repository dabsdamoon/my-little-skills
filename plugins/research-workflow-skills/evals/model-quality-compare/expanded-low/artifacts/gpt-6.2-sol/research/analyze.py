"""Describe the within-group association of two WDI series."""
import argparse
import csv
import json
import math
import re
from decimal import Decimal, InvalidOperation, localcontext
from itertools import pairwise

SERIES = {"income": "NY.GNP.PCAP.KD", "education": "NY.ADJ.AEDU.GN.ZS"}
YEAR = re.compile(r"(\d{4})(?:\s+\[YR\1\])?")


def number(cell):
    try:
        value = Decimal(cell or "")
    except InvalidOperation:
        return None
    return value if value.is_finite() else None


def json_number(value):
    result = float(value)
    return result if math.isfinite(result) else None


def summarize(pairs):
    n = len(pairs)
    stats = {"n": n, "pearson_r": None, "ols_slope": None}
    if n < 2:
        return stats

    x, y = zip(*pairs)
    # Center for the intercept fit. Shift first to remove common offsets
    # and to make a constant series yield exactly zero variance.
    x = [v - x[0] for v in x]
    y = [v - y[0] for v in y]
    mean_x, mean_y = sum(x) / n, sum(y) / n
    dx = [v - mean_x for v in x]
    dy = [v - mean_y for v in y]
    xx = sum(v * v for v in dx)
    yy = sum(v * v for v in dy)
    if xx:
        xy = sum(a * b for a, b in zip(dx, dy))
        stats["ols_slope"] = json_number(xy / xx)
        if yy:
            r = xy / (xx * yy).sqrt()
            stats["pearson_r"] = json_number(max(-1, min(1, r)))
    return stats


def analyze(path):
    rows = {}
    with open(path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        years = sorted(
            (int(match[1]), header)
            for header in reader.fieldnames or []
            if (match := YEAR.fullmatch(header.strip()))
        )
        for row in reader:
            series = row["Series Code"].strip()
            if series in SERIES.values():
                code = row["Country Code"].strip()
                rows.setdefault(code, {})[series] = row

    groups = {}
    for code, by_series in sorted(rows.items()):
        if len(by_series) != len(SERIES):
            continue
        education = by_series[SERIES["education"]]
        income = by_series[SERIES["income"]]
        paired = []
        for year, header in years:
            x, y = number(education[header]), number(income[header])
            if x is not None and y is not None:
                paired.append((year, x, y))

        with localcontext() as ctx:
            ctx.prec = 50
            groups[code] = {
                "label": education["Country Group"],
                "level": summarize([(x, y) for _, x, y in paired]),
                "difference": summarize([
                    (x1 - x0, y1 - y0)
                    for (t0, x0, y0), (t1, x1, y1) in pairwise(paired)
                    if t1 == t0 + 1
                ]),
            }
    return {"series": SERIES, "groups": groups}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path")
    args = parser.parse_args()
    print(json.dumps(analyze(args.csv_path), indent=2, allow_nan=False))
