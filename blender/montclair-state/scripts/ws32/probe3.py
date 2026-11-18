import bpy
m=bpy.data.materials['CCOM_dock_asphalt_20261014jf3']; b=m.node_tree.nodes['Principled BSDF']
print('AP',tuple(round(x,3) for x in b.inputs['Base Color'].default_value),b.inputs['Roughness'].default_value)
a=bpy.data.materials['Asphalt']; print('ASPH nodes',[(n.type,n.name) for n in a.node_tree.nodes])
fp=bpy.data.objects['Footpaths_OSM']; print('FP mods',[(md.type,md.name) for md in fp.modifiers], 'verts',len(fp.data.vertices))
for n in ('OZ_walk_joints_auto_GN_UNVERIFIED','PA_walk_panel_tone_chips_UNVERIFIED'):
    o=bpy.data.objects[n]; print(n,[(md.type,md.name) for md in o.modifiers], len(o.data.vertices))
import mathutils
c=0
for v in fp.data.vertices:
    p=fp.matrix_world@v.co
    if -1<p.x<9 and -39<p.y<-24: c+=1
print('FP verts in box',c)
