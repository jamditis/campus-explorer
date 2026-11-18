import bpy
from mathutils import Vector
for n in ['WS115_E_walk_N_concrete_OSM312849086_ortho2020_2m_UNVERIFIEDw','WS102_CollegeAve_S_curb_E_LiDARstep12-20cm_UNVERIFIED']:
    o=bpy.data.objects[n]; mw=o.matrix_world; me=o.data
    vs=[mw@v.co for v in me.vertices]
    print(n,len(vs),len(me.polygons),[m.name for m in me.materials], o.modifiers[:] and [m.name for m in o.modifiers])
    for y in range(-240,-196,2):
        sel=[v for v in vs if y-0.6<=v.y<y+0.6]
        if not sel: continue
        if 'walk' in n:
            v=min(sel,key=lambda v:v.x); w=max(sel,key=lambda v:v.x); print(' y',y,'Wedge',round(v.x,2),round(v.z,2),'Eedge',round(w.x,2),round(w.z,2))
        else:
            top=max(v.z for v in sel); v=max(sel,key=lambda v:(v.x if v.z>top-0.05 else -999)); print(' y',y,'curb back top',round(v.x,2),round(v.y,2),round(v.z,2))
for o in bpy.data.objects:
    if any(k in o.name.lower() for k in ('lamp','globe','light_pole','lightpole','post_top')) and o.type=='MESH':
        p=o.matrix_world.translation
        if -300<p.x<-150 and -300<p.y<-100: print('LAMP',o.name,round(p.x,1),round(p.y,1))
