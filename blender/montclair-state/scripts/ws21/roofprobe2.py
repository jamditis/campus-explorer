import bpy,collections
o=bpy.data.objects['Life Hall roof (LiDAR)']; me=o.data; M=o.matrix_world
rc=me.attributes['roofc']; ef=me.attributes['em_ringforce']
print('roofc domain',rc.domain,rc.data_type,'ring',ef.domain)
import numpy as np
bins=collections.defaultdict(list)
for p in me.polygons:
    nz=(M.to_3x3()@p.normal).normalized().z
    c=M@p.center
    if p.material_index!=0: continue
    v=rc.data[p.index].color[:3] if rc.domain=='FACE' else None
    k=('slope' if nz<0.93 else 'flat', int(c.x//15)*15, int(c.y//15)*15)
    bins[k].append((v, ef.data[p.index].value, p.area))
for k in sorted(bins):
    L=bins[k]
    if k[0]!='slope': continue
    cs=np.array([l[0] for l in L if l[0] is not None]) if L[0][0] is not None else None
    print(k,len(L),'area',round(sum(l[2] for l in L),1),'ring',round(np.mean([l[1] for l in L]),2),'roofc',None if cs is None else np.round(cs.mean(0),2))
