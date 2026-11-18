# ws171b: WS171 yard-tree crowns were ~24-30 m wide (asset bbox x h/18) vs LiDAR crown radius 6-9 m -> rescale XY about each trunk to
# crown width = 2*r_LiDAR*1.05 (peaks169 r column), keep height h. Keeps crowns S of the wire line (utility clearance as trimmed in reality).
import bpy
from mathutils import Matrix, Vector
OB=bpy.data.objects
R={'A':7.6,'B':6.2,'C':6.0,'D':9.0,'E':9.0,'H':6.7,'I':8.5,'K':6.2}
bpy.context.view_layer.update()
for t in [o for o in OB if o.name.startswith('WS171_tree_S_yard_')]:
    k=t.name.split('S_yard_')[1][0]
    W=[t.matrix_world@v.co for v in t.data.vertices]; zm=min(w.z for w in W); L=[w for w in W if w.z<zm+0.3]
    b=Vector((sum(w.x for w in L)/len(L),sum(w.y for w in L)/len(L),zm))
    w=max(max(v.x for v in W)-min(v.x for v in W),max(v.y for v in W)-min(v.y for v in W))
    s=2*R[k]*1.05/w
    t.matrix_world=Matrix.Translation(b)@Matrix.Diagonal((s,s,1,1))@Matrix.Translation(-b)@t.matrix_world
    bpy.context.view_layer.update()
    bb=[t.matrix_world@Vector(c) for c in t.bound_box]; cx=b.x; ywire=-260+(cx+331.7)*(-0.25)
    print('TREE171b',t.name,'w',round(w,1),'s',round(s,2),'x',round(min(c.x for c in bb),1),round(max(c.x for c in bb),1),'y',round(min(c.y for c in bb),1),round(max(c.y for c in bb),1),'crownN-wire',round(max(c.y for c in bb)-ywire,1),flush=True)
