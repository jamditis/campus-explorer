# W59 check: evaluated Context_skirt boundary edges (box + whole skirt) and the W57 eye-view rays (probe241l camera)
import bpy, os, bmesh
from mathutils import Vector
O=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; out=[]
dg=bpy.context.evaluated_depsgraph_get(); ev=O.evaluated_get(dg); me=ev.to_mesh(); mw=O.matrix_world
bm=bmesh.new(); bm.from_mesh(me)
B=[(mw@e.verts[0].co) for e in bm.edges if e.is_boundary]
box=[p for p in B if -420<=p.x<=-320 and -80<=p.y<=10]
out.append('faces %d boundary_all %d boundary_box %d'%(len(bm.faces),len(B),len(box)))
import collections
c=collections.Counter((int(p.x//50)*50,int(p.y//50)*50) for p in B)
out.append('boundary by 50m cell (top 25): %s'%c.most_common(25))
bm.free(); ev.to_mesh_clear()
sc=bpy.context.scene
E=Vector((-348,-64,120.3)); T=Vector((-352,0,121.6)); f=(T-E).normalized()
r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f); W,H=704,396; fw=36/28.0; miss=0; tot=0
for px in range(0,704,8):
    for py in range(200,396,4):
        sx=(px+0.5)/W-0.5; sy=0.5-(py+0.5)/H
        d=(f+r*(sx*fw)+u*(sy*fw*H/W)).normalized(); h=sc.ray_cast(dg,E,d,distance=800); tot+=1
        if not h[0]: miss+=1; out.append('MISS px %d,%d'%(px,py)) if miss<30 else None
out.append('rays below horizon %d miss %d'%(tot,miss))
open('/workspace/nj-scenes/montclair-state/scripts/ws242/'+os.environ.get('PO','probe242b.out'),'w').write('\n'.join(o for o in out if o)); print('P242B ok',flush=True); os._exit(0)
