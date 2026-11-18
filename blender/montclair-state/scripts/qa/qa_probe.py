import bpy, collections
from mathutils import Vector
G=[((-182.0,85.05),'W'),((-177.78,78.43),'S')]
for gc,lab in G:
    c=Vector(gc)
    print('=== GAP',lab,gc)
    for on in ('Dickson Hall walls','PX_Dickson_wing_parapet_infill_UNVERIFIED','PY_Dickson_wing_parapet_raise_UNVERIFIED','PY_Dickson_wing_parapet_back_roofstrip_UNVERIFIED','PY_Dickson_wing_parapet_coping_UNVERIFIED','Dickson Hall roof (LiDAR)','PZ_Dickson_wing_coping_drip_stain_UNVERIFIED'):
        o=bpy.data.objects.get(on)
        if not o: print('missing',on); continue
        me=o.data; mw=o.matrix_world; WV=[mw@v.co for v in me.vertices]
        near=[(i,v) for i,v in enumerate(WV) if (v.xy-c).length<1.6 and v.z>148]
        print('--',on,len(near))
        ec=collections.defaultdict(list)
        for p in me.polygons:
            for k in p.edge_keys: ec[k].append(p.index)
        S=set(i for i,v in near)
        for k,fl in ec.items():
            if k[0] in S and k[1] in S:
                a=WV[k[0]];b=WV[k[1]]
                print('  E%s (%.3f,%.3f,%.3f)-(%.3f,%.3f,%.3f) nf%d mat%d'%('B' if len(fl)==1 else ' ',a.x,a.y,a.z,b.x,b.y,b.z,len(fl),me.polygons[fl[0]].material_index))
