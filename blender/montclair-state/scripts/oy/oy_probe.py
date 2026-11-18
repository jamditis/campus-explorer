import bpy, math
from mathutils import Vector
s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
F=bpy.data.objects['Footpaths_OSM']; FE=F.evaluated_get(dg); FI=F.matrix_world.inverted()
for cn in ('OR_CAM_eye_CELS_skirt_windows_base_course','OQ_CAM_eye_calcia_skirt_windows','OT_CAM_aerial_north_strip_CELS_Calcia','OW2_CAM_closeup_CELS_walk_road_edge'):
    c=bpy.data.objects[cn]; print('CAM',cn,tuple(round(x,2) for x in c.location),tuple(round(math.degrees(a),1) for a in c.rotation_euler))
    fr=c.data.view_frame(scene=s); mw=c.matrix_world; o=mw.translation
    hits=[]
    for iy in range(24):
        for ix in range(40):
            u=ix/39; v=iy/23
            p=fr[3].lerp(fr[0],u)  # top-left->top-right
            q=fr[2].lerp(fr[1],u)
            pt=p.lerp(q,v); d=(mw@pt-o).normalized()
            ok,loc,n,i=FE.ray_cast(FI@o,(FI.to_3x3()@d).normalized(),distance=400)
            if ok: hits.append(F.matrix_world@loc)
    if hits:
        xs=[h.x for h in hits]; ys=[h.y for h in hits]
        print('  walk hits',len(hits),'x %.1f..%.1f y %.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys)))
        # coarse 5m histogram
        cells={}
        for h in hits: k=(int(h.x//5)*5,int(h.y//5)*5); cells[k]=cells.get(k,0)+1
        print('  cells',sorted(cells.items()))
