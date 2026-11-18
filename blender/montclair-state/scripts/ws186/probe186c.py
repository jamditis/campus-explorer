import bpy
from mathutils import Vector
for pre in ('WS162_Lot3_W_walk_band','WS162_Lot3_S_end_apron','WS170b','WS162_Lot3_W_curb'):
    o=next((o for o in bpy.data.objects if o.name.startswith(pre)),None)
    if not o: print('PC missing',pre); continue
    import bmesh
    bm=bmesh.new(); bm.from_mesh(o.data); M=o.matrix_world
    b=[M@v.co for v in bm.verts if v.is_boundary]; b=[w for w in b if -318<w.x<-305 and -238<w.y<-222]
    print('PC',o.name[:40],len(o.data.vertices),'bnd in box',len(b),sorted([(round(w.x,2),round(w.y,2),round(w.z,2)) for w in b],key=lambda t:t[1])[:60],flush=True)
