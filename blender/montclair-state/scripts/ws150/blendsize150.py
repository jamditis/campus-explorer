# streaming size audit of a zstd blend: bytes per ID block (+ trailing DATA) — no Blender load
import zstandard, struct, sys, collections, json
f=open(sys.argv[1],'rb'); r=zstandard.ZstdDecompressor().stream_reader(f)
def rd(n):
    b=b''
    while len(b)<n:
        c=r.read(n-len(b))
        if not c: return b
        b+=c
    return b
h=rd(12)
if h.startswith(b'BLENDER17'):
    h+=rd(5); large=True
else: large=False
print("HDR",h)
bycode=collections.Counter(); byid=collections.Counter(); cur=None; tot=0
while True:
    if large:
        hd=rd(32)
        if len(hd)<32: break
        code=hd[:4]; sdna,old,ln,cnt=struct.unpack('<iQqq',hd[4:32])
    else:
        hd=rd(24)
        if len(hd)<24: break
        code=hd[:4]; ln,old,sdna,cnt=struct.unpack('<iQii',hd[4:24])
    if code==b'ENDB': break
    body=rd(ln) if ln<200 else rd(ln)
    tot+=ln+len(hd)
    c=code.rstrip(b'\0').decode('latin1')
    bycode[c]+=ln
    if c not in ('DATA','REND','TEST','GLOB','DNA1','USER') and len(body)>=60:
        nm=body[40:40+258].split(b'\0')[0].decode('latin1','replace'); cur=nm
    byid[cur or c]+=ln
print("TOTAL_MB",tot/1e6)
for k,v in bycode.most_common(20): print("CODE",k,round(v/1e6,1))
for k,v in byid.most_common(60): print("ID",k,round(v/1e6,1))
json.dump(byid.most_common(400),open(sys.argv[2],'w'))
