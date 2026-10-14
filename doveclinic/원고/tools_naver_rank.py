import re,sys
x=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
seen=[]
for m in re.finditer(r'https?://(?:m\.)?blog\.naver\.com/([A-Za-z0-9_\-]+)/(\d{9,})',x):
    k=(m.group(1),m.group(2))
    if k not in seen: seen.append(k)
for i,(b,n) in enumerate(seen[:15],1): print(i,b,n, '<==' if b=='doveclinic' else '')
