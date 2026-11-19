import csv, json, math, re, sys
INC, EDU = "NY.GNP.PCAP.KD", "NY.ADJ.AEDU.GN.ZS"

def num(s):
    try:
        v = float(str(s).strip())
    except ValueError:
        return None
    return v if math.isfinite(v) else None

def stats(pairs):
    n = len(pairs)
    out = {"n": n, "pearson_r": None, "ols_slope": None}
    if n < 2:
        return out
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sxx = sum((p[0] - mx) ** 2 for p in pairs)
    syy = sum((p[1] - my) ** 2 for p in pairs)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    xconst = len({p[0] for p in pairs}) == 1
    yconst = len({p[1] for p in pairs}) == 1
    if not xconst:
        out["ols_slope"] = sxy / sxx
    if not xconst and not yconst:
        out["pearson_r"] = max(-1.0, min(1.0, sxy / math.sqrt(sxx * syy)))
    return out

def main(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        hdr = next(rd)
        ycols = []
        for i, h in enumerate(hdr):
            m = re.match(r"\s*(\d{4})\b", h)
            if m:
                ycols.append((int(m.group(1)), i))
        ix = {h.strip(): i for i, h in enumerate(hdr)}
        ig, ic, isr = ix["Country Group"], ix["Country Code"], ix["Series Code"]
        data, labels = {}, {}
        for r in rd:
            if len(r) <= max(ig, ic, isr):
                continue
            s = r[isr].strip()
            if s not in (INC, EDU):
                continue
            c = r[ic].strip()
            labels.setdefault(c, r[ig].strip())
            d = data.setdefault(c, {INC: {}, EDU: {}})[s]
            for y, i in ycols:
                v = num(r[i]) if i < len(r) else None
                if v is not None:
                    d[y] = v
    groups = {}
    for c in data:
        xs, ys = data[c][EDU], data[c][INC]
        yrs = sorted(set(xs) & set(ys))
        lev = [(xs[y], ys[y]) for y in yrs]
        dif = [(xs[b] - xs[a], ys[b] - ys[a]) for a, b in zip(yrs, yrs[1:]) if b == a + 1]
        groups[c] = {"label": labels[c], "level": stats(lev), "difference": stats(dif)}
    print(json.dumps({"series": {"income": INC, "education": EDU}, "groups": groups}))

if __name__ == "__main__":
    main(sys.argv[1])
