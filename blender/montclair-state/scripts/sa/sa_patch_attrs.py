# sa: sample the skirt's evaluated shader attributes (ou_edge, ow2_strip, any FLOAT point attr) onto SA_ground_lower_patch (they were 0 -> pale raw ortho).
# Temporarily swaps the skirt back to its pre-sa mesh (SA_skirt_mesh_backup) to evaluate, then swaps back. Patch-attribute only.
import bpy, numpy as np
from mathutils import Vector, interpolate
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; P=bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']; b=bpy.data.meshes['SA_skirt_mesh_backup']
cur=sk.data; sk.data=b; bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get(); ske=sk.evaluated_get(dg); d=ske.data
attrs=[a.name for a in d.attributes if a.domain=='POINT' and a.data_type=='FLOAT' and not a.name.startswith('.')]
print('SA attrs',attrs)
mw=sk.matrix_world; iw=mw.inverted(); pm=P.matrix_world
V=[pm@v.co for v in P.data.vertices]; vals={a:np.zeros(len(V),np.float32) for a in attrs}
for k,w in enumerate(V):
    r=ske.ray_cast(iw@Vector((w.x,w.y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
    if not r[0]: continue
    p=d.polygons[r[3]]; vs=[d.vertices[i].co for i in p.vertices]; ww=interpolate.poly_3d_calc(vs,r[1])
    for a in attrs: vals[a][k]=sum(x*d.attributes[a].data[i].value for x,i in zip(ww,p.vertices))
sk.data=cur; bpy.context.view_layer.update()
me=P.data
for a in attrs:
    at=me.attributes.get(a) or me.attributes.new(a,'FLOAT','POINT'); at.data.foreach_set('value',vals[a])
    print('SA',a,float(vals[a].min()),float(vals[a].max()),float(vals[a].mean()))
bpy.ops.wm.save_mainfile(); print('SAVED')
