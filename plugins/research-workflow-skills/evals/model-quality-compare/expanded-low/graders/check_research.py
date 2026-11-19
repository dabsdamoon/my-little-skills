import csv
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

INCOME='NY.GNP.PCAP.KD'
EDUCATION='NY.ADJ.AEDU.GN.ZS'


def reference(rows):
    bygroup={}
    for row in rows:
        bygroup.setdefault(row['Country Code'],{})[row['Series Code']]=row
    result={'series':{'income':INCOME,'education':EDUCATION},'groups':{}}
    def summarize(pairs):
        x,y=[p[0] for p in pairs],[p[1] for p in pairs]
        slope=r=None
        if len(pairs)>=2:
            if len(set(x))>1: slope=statistics.linear_regression(x,y).slope
            if len(set(x))>1 and len(set(y))>1: r=statistics.correlation(x,y)
        return dict(n=len(pairs),pearson_r=r,ols_slope=slope)
    for code,series in bygroup.items():
        if INCOME not in series or EDUCATION not in series: continue
        xrow,yrow=series[EDUCATION],series[INCOME];pairs=[]
        for col in xrow:
            if '[YR' not in col: continue
            try: year=int(col[:4]);x=float(xrow[col]);y=float(yrow[col])
            except (ValueError,TypeError): continue
            if math.isfinite(x) and math.isfinite(y): pairs.append((year,x,y))
        pairs.sort()
        diffs=[(b[1]-a[1],b[2]-a[2]) for a,b in zip(pairs,pairs[1:]) if b[0]==a[0]+1]
        result['groups'][code]=dict(label=xrow['Country Group'],level=summarize([(p[1],p[2]) for p in pairs]),difference=summarize(diffs))
    return result


def equivalent(actual,expected):
    if isinstance(expected,dict):
        return isinstance(actual,dict) and all(k in actual and equivalent(actual[k],v) for k,v in expected.items())
    if expected is None: return actual is None
    if isinstance(expected,(int,float)):
        return type(actual) in (int,float) and math.isfinite(actual) and math.isclose(actual,expected,rel_tol=1e-6,abs_tol=1e-7)
    return actual==expected


def main():
    root=Path('/workspace');checks=[]
    original=list(csv.DictReader((root/'data.csv').open()))
    variants=[('original',original)]
    reordered=list(reversed(original));variants.append(('reordered',reordered))
    gapped=[dict(r) for r in original]
    for r in gapped:
        if r['Country Code']=='LMC' and r['Series Code']==INCOME: r['1993 [YR1993]']='..'
    variants.append(('gapped',gapped))
    scaled=[dict(r) for r in original]
    for r in scaled:
        if r['Series Code']==INCOME:
            for k,v in r.items():
                if '[YR' in k:
                    try:r[k]=str(float(v)*2+3)
                    except ValueError:pass
    variants.append(('scaled',scaled))
    constant=[dict(r) for r in original]
    for r in constant:
        if r['Series Code']==EDUCATION:
            for k in r:
                if '[YR' in k:r[k]='4'
    variants.append(('constant',constant))
    observed=None
    for name,rows in variants:
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.csv'
            with path.open('w') as f:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            run=subprocess.run([sys.executable,'-B',str(root/'analyze.py'),str(path)],cwd=root,capture_output=True,text=True)
            try:actual=json.loads(run.stdout);passed=run.returncode==0 and equivalent(actual,reference(rows))
            except (ValueError,TypeError):actual=None;passed=False
            checks.append({'id':name,'passed':passed,'actual':actual,'expected':reference(rows),'stderr':run.stderr})
            if name=='original':observed=actual
    try:saved=json.loads((root/'results.json').read_text());same=equivalent(saved,reference(original)) and equivalent(saved,observed)
    except (OSError,ValueError,TypeError):same=False
    checks.append({'id':'saved-results-reproduce','passed':same})
    checks.append({'id':'report-artifact','passed':(root/'report.md').exists() and (root/'report.md').stat().st_size>0})
    print(json.dumps({'checks':len(checks),'passed':sum(c['passed'] for c in checks),'details':checks}))


if __name__=='__main__':main()
