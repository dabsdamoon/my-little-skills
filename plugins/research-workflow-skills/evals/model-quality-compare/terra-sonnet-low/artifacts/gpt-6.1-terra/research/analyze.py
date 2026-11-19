#!/usr/bin/env python3
"""Summarize paired annual World Bank series for each group in a CSV."""
import csv
import json
import math
import re
import sys

INCOME = 'NY.GNP.PCAP.KD'
EDUCATION = 'NY.ADJ.AEDU.GN.ZS'


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def statistics(pairs):
    n = len(pairs)
    result = {'n': n, 'pearson_r': None, 'ols_slope': None}
    if n < 2:
        return result
    xs, ys = zip(*pairs)
    mx, my = math.fsum(xs) / n, math.fsum(ys) / n
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    xx = math.fsum(x * x for x in dx)
    yy = math.fsum(y * y for y in dy)
    xy = math.fsum(x * y for x, y in zip(dx, dy))
    if xx:
        slope = xy / xx
        result['ols_slope'] = slope if math.isfinite(slope) else None
        if yy:
            r = (xy / math.sqrt(xx)) / math.sqrt(yy)
            result['pearson_r'] = r if math.isfinite(r) else None
    return result


def analyze(path):
    groups = {}
    with open(path, encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        years = {}
        for name in reader.fieldnames:
            match = re.fullmatch(r'(\d{4})(?:\s*\[YR\d{4}\])?', name.strip())
            if match:
                years[int(match.group(1))] = name
        for row in reader:
            code, series = row['Country Code'].strip(), row['Series Code'].strip()
            if not code or series not in (INCOME, EDUCATION):
                continue
            group = groups.setdefault(code, {'label': row['Country Group'], 'series': {}})
            if series in group['series']:
                raise ValueError('Duplicate series for group: ' + code + ' ' + series)
            group['series'][series] = {year: number(row[column]) for year, column in years.items()}
    output = {}
    for code, group in sorted(groups.items()):
        if not all(s in group['series'] for s in (INCOME, EDUCATION)):
            continue
        x, y = group['series'][EDUCATION], group['series'][INCOME]
        paired = [(year, x[year], y[year]) for year in sorted(years)
                  if x[year] is not None and y[year] is not None]
        levels = [(a, b) for _, a, b in paired]
        differences = [(x1 - x0, y1 - y0)
                       for (t0, x0, y0), (t1, x1, y1) in zip(paired, paired[1:])
                       if t1 == t0 + 1]
        output[code] = {'label': group['label'], 'level': statistics(levels),
                        'difference': statistics(differences)}
    return {'series': {'income': INCOME, 'education': EDUCATION}, 'groups': output}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 analyze.py CSV_PATH')
    print(json.dumps(analyze(sys.argv[1]), indent=2, allow_nan=False))
