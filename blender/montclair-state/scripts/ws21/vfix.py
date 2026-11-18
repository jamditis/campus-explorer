# ws21: Life Hall walls facade V became inconsistent at the raised top verts (per-loop shifts applied unevenly) -> diagonal stucco wedges across upper windows.
# Per face: take V-z offset from the face's lowest loops and set every loop V = z + offset (V is linear in z on these walls).
import bpy,bmesh,os,statistics
SAVE=os.environ.get('SAVE')=='1'
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data)
uvl=bm.loops.layers.uv['facade']
n=0;mx=0
for f in bm.faces:
    L=list(f.loops); Z=[(M@l.vert.co).z for l in L]
    if max(Z)-min(Z)<0.3: continue
    zmin=min(Z)
    offs=[l[uvl].uv.y-z for l,z in zip(L,Z) if z<zmin+0.05]
    off=statistics.median(offs)
    d=max(abs(l[uvl].uv.y-(z+off)) for l,z in zip(L,Z))
    if d>0.02:
        n+=1; mx=max(mx,d)
        for l,z in zip(L,Z): l[uvl].uv.y=z+off
print('FIXED faces',n,'max dev',round(mx,2))
if SAVE:
    bm.to_mesh(o.data); o.data.update(); o['ws21']='facade V made linear in z per face (wedge fix)'
    bpy.ops.wm.save_mainfile(); print('SAVED')
