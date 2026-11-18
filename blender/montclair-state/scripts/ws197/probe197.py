import bpy,numpy as np
from mathutils import Vector
O=bpy.data.objects
I=O['WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED']; m=I.matrix_world
V=np.array([tuple(m@v.co) for v in I.data.vertices]); n=len(V)//18
print('P197 ISA nverts',len(V),'per',n,len(V)%18)
for s in range(18):
    S=V[s*n:(s+1)*n]; print('P197 sym',s,'c %.2f %.2f z %.3f'%(S[:,0].mean(),S[:,1].mean(),S[:,2].mean()))
for nm in ['WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED','WS76_lot_stall_paint_white_ortho2020_UNVERIFIED','WS76_lot_zebra_walkway_paint_ortho2020_UNVERIFIED','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']:
    o=O[nm]; mw=o.matrix_world; P=np.array([tuple(mw@v.co) for v in o.data.vertices])
    print('P197',nm[:40],'bbox',P.min(0).round(2).tolist(),P.max(0).round(2).tolist())
# objects near NE end region
for o in O:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[b.x for b in bb]; ys=[b.y for b in bb]
    if max(xs)>-262 and min(xs)<-212 and max(ys)>-95 and min(ys)<-60 and (max(xs)-min(xs))<15 and (max(ys)-min(ys))<15:
        print('P197 small',o.name,'x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f nv %d'%(min(xs),max(xs),min(ys),max(ys),min(b.z for b in bb),max(b.z for b in bb),len(o.data.vertices)),[ms.name for ms in o.data.materials if ms])
