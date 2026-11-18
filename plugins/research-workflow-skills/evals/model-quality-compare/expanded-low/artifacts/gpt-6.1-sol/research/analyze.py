"""Descriptive, contemporaneous education/income associations from WDI wide CSV."""
import csv
import json
import math
import re
import sys

SERIES = {"income": "NY.GNP.PCAP.KD", "education": "NY.ADJ.AEDU.GN.ZS"}


def numeric(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def summarize(pairs):
    n = len(pairs)
    result = {"n": n, "pearson_r": None, "ols_slope": None}
    if n < 2:
        return result
    xs, ys = zip(*pairs)
    mx, my = math.fsum(xs) / n, math.fsum(ys) / n
    dx, dy = [x - mx for x in xs], [y - my for y in ys]
    xx = math.fsum(x*x for x in dx)
    yy = math.fsum(y*y for y in dy)
    xy = math.fsum(x*y for x, y in zip(dx, dy))
    if xx:
        result['ols_slope'] = numeric(xy / xx)
    if xx and yy:
        result['pearson_r'] = numeric(xy / math.sqrt(xx) / math.sqrt(yy))
    return result


def analyze(path):
    groups = {}
    with open(path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        years = []
        for field in reader.fieldnames or []:
            match = re.fullmatch(r'(\d{4})(?: \[YR\1\])?', field.strip())
            if match:
                years.append((int(match.group(1)), field))
        years.sort()
        for row in reader:
            code, series = row['Country Code'].strip(), row['Series Code'].strip()
            if not code or series not in SERIES.values():
                continue
            group = groups.setdefault(code, {'label': row['Country Group'], 'data': {}})
            if series in group['data']:
                raise ValueError('Duplicate group/series: ' + code + '/' + series)
            group['data'][series] = {year: numeric(row[field]) for year, field in years}
    output = {}
    for code, group in sorted(groups.items()):
        data = group['data']
        if not all(series in data for series in SERIES.values()):
            continue
        x, y = data[SERIES['education']], data[SERIES['income']]
        paired = [(year, x[year], y[year]) for year in sorted(x.keys() & y.keys())
                  if x[year] is not None and y[year] is not None]
        differences = [(b[1]-a[1], b[2]-a[2]) for a, b in zip(paired, paired[1:])
                       if b[0] == a[0]+1]
        output[code] = {'label': group['label'],
                        'level': summarize([(x, y) for _, x, y in paired]),
                        'difference': summarize(differences)}
    return {'series': SERIES, 'groups': output}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 analyze.py CSV_PATH')
    print(json.dumps(analyze(sys.argv[1]), allow_nan=False))
