import bpy
from mathutils import Vector
up=bpy.data.objects['PN_Feliciano_tier_161.3_UNVERIFIED']; lo=bpy.data.objects['PN_Feliciano_tier_156.6_UNVERIFIED']
tw=up.matrix_world; lw=lo.matrix_world
for fi in (71,72):
    p=up.data.polygons[fi]; print('UPF',fi,[tuple(round(c,2) for c in tw@up.data.vertices[i].co) for i in p.vertices])
for fi in (57,):
    p=lo.data.polygons[fi]; print('LOF',fi,[tuple(round(c,2) for c in lw@lo.data.vertices[i].co) for i in p.vertices], tuple(round(c,3) for c in lw.to_3x3()@p.normal))
