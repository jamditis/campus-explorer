# ws60: give the apron the skirt's ortho material with UVs from a linear XY fit to the skirt's own UVs
import bpy,numpy as np
s=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; me=s.data; mw=s.matrix_world
uvl=me.uv_layers.active
A=[];U=[]
for li,l in enumerate(me.loops[:200000]):
    w=mw@me.vertices[l.vertex_index].co; A.append((w.x,w.y,1)); U.append(tuple(uvl.data[li].uv))
A=np.array(A);U=np.array(U); co,res,_,_=np.linalg.lstsq(A,U,rcond=None)
print('UV60 fit resid',res)
ob=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; am=ob.data
am.materials.clear()
for m in me.materials: am.materials.append(m)
if not am.uv_layers: am.uv_layers.new(name=uvl.name)
au=am.uv_layers[0]; amw=ob.matrix_world
for li,l in enumerate(am.loops):
    w=amw@am.vertices[l.vertex_index].co; au.data[li].uv=tuple(np.array((w.x,w.y,1))@co)
for p in am.polygons: p.material_index=0
print('UV60 done',[m.name for m in am.materials])
