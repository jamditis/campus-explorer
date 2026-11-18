# Session jc: UV seams (U jumps across shared edges) between amphitheater stone faces
import bpy, bmesh, numpy as np, collections, os
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
STONE={i for i,n in enumerate(names) if n in ('hn_amphi_seat_stone_blocks','hn_amphi_riser_coursed_stone','io_amphi_aisle_stone','ip_amphi_aisle_nosing_worn')}
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); uvl=bm.loops.layers.uv['UVMap']
cnt=collections.Counter(); samp=[]
for e in bm.edges:
    if len(e.link_faces)!=2: continue
    f1,f2=e.link_faces
    if f1.material_index not in STONE or f2.material_index not in STONE: continue
    def uvs(f):
        return {l.vert.index:l[uvl].uv.copy() for l in f.loops if l.vert in e.verts}
    a,b=uvs(f1),uvs(f2); d=max(abs(a[k].x-b[k].x) for k in a)
    t=lambda f:'up' if f.normal.z>0.9 else 'vt' if abs(f.normal.z)<0.5 else 'o'
    key=tuple(sorted((t(f1)+names[f1.material_index][3:8],t(f2)+names[f2.material_index][3:8])))
    if d>0.02:
        cnt[key]+=1
        if -170<e.verts[0].co.x<-164 and e.verts[0].co.y<13 and t(f1)=='vt' and t(f2)=='vt': samp.append((round(d,3),[round(c,2) for c in e.verts[0].co]))
print('JCS seams |du|>0.02 by face pair',cnt.most_common(12))
print('JCS vt-vt samples in close-up region',len(samp),samp[:10])
