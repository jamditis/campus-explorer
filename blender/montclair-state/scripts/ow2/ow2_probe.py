import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
f=bpy.data.objects['Footpaths_OSM']
for m in f.modifiers:
    print('MOD',m.name,m.type,m.node_group.name if m.type=='NODES' and m.node_group else '', [(k,getattr(m[k],'name',m[k])) for k in m.keys()][:8])
rd=bpy.data.objects['Roads_OSM']; print('RMOD',[m.name for m in rd.modifiers])
def cast(camn,pts,W=1024,H=576):
    cam=bpy.data.objects[camn]; fr=cam.data.view_frame(scene=sc); tr,br,bl,tl=fr
    for px,py in pts:
        u=px/W; v=1-py/H; p=bl+(br-bl)*u+(tl-bl)*v
        d=(cam.matrix_world.to_3x3()@p).normalized(); o=cam.matrix_world.translation
        ok,loc,n,i,ob,mx=sc.ray_cast(dg,o,d)
        mat=''
        if ok and ob.type=='MESH':
            try: e=ob.evaluated_get(dg); pp=e.data.polygons[i]; mat=e.material_slots[pp.material_index].material.name if e.material_slots else ''
            except Exception as ex: mat='?'
        print('HIT',camn[:6],px,py,ob.name if ok else None,tuple(round(c,2) for c in loc) if ok else '',round(n.z,3) if ok else '',mat)
cast('OR_CAM_eye_CELS_skirt_windows_base_course',[(880,400),(920,420),(960,440),(990,460),(940,480),(1000,500),(880,440),(1010,420),(850,380),(800,330),(760,350)])
cast('OT_CAM_aerial_north_strip_CELS_Calcia',[(100,245),(250,250),(400,250),(470,260),(250,270),(250,235),(600,255),(700,255),(330,248)])
# terrain under walk in box
dt=[o for o in bpy.data.objects if 'DTM' in o.name or 'LiDAR terrain' in o.name.lower() or o.name.startswith('Terrain')]
print('TERR',[o.name for o in dt][:10])
