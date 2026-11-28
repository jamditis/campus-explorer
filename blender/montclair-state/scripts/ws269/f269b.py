# ws269b: move the Lot 33 island tree onto the 2023 LiDAR crown (las269.py: class-1 max 11.9 m over ground at (-349.5,-36.5),
# crown x -354..-347, y -34..-44) -> trunk (-350.0,-38.0) on the island axis, height 12 m (was (-347.5,-38.4), 13 m from the ortho).
import bpy
from mathutils import Vector, Matrix
OB=bpy.data.objects; TAG='F269B'
t=OB['WS269_tree_Lot33_island_ortho2020_h13m_UNVERIFIEDspecies']; src=[o for o in OB if o.name.startswith('WS165_tree_aisle_mouth')][0]
_mw=src.matrix_world; _W=[_mw@v.co for v in src.data.vertices]; _zm=min(w.z for w in _W); _L=[w for w in _W if w.z<_zm+0.3]
B0=Vector((sum(w.x for w in _L)/len(_L),sum(w.y for w in _L)/len(_L),_zm))
pav=OB['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
from mathutils.bvhtree import BVHTree
import bmesh
bm=bmesh.new(); bm.from_mesh(pav.data); bm.transform(pav.matrix_world); T=BVHTree.FromBMesh(bm); bm.free()
tx,ty,h=-350.0,-38.0,12.0; s=h/18.0; z=T.ray_cast(Vector((tx,ty,200)),Vector((0,0,-1)))[0].z
t.matrix_world=Matrix.Translation(Vector((tx,ty,z+0.10-0.12)))@Matrix.Rotation(2.1,4,'Z')@Matrix.Diagonal((s,s,s,1))@Matrix.Translation(-B0)@src.matrix_world
t.name='WS269_tree_Lot33_island_LiDAR2023_h12m_UNVERIFIEDspecies'
print(TAG,'tree',t.name,'base z',round(z-0.02,2),flush=True)
