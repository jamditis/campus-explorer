import bpy, hashlib
o=bpy.data.objects
names=sorted(x.name for x in o)
fin=o.get('Finley Hall walls')
zs=sorted(v.co.z for v in fin.data.vertices) if fin else []
h=hashlib.sha256()
# hash Finley wall z's + object name list + presence of UC objs
h.update('\n'.join(names).encode())
if fin:
    for v in fin.data.vertices:
        h.update(f'{v.index}:{v.co.x:.5f}:{v.co.y:.5f}:{v.co.z:.5f}\n'.encode())
uc=sum(1 for x in o if x.get('uc_obj'))
print('UCSIG', len(names), 'uc_obj', uc, 'fin_zmax', round(max(zs),5) if zs else None, 'fin_uc', bool(fin.get('uc_fix') if fin else None), h.hexdigest()[:24])
