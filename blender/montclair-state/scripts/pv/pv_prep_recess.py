# pv prep (read-only): Dickson wall faces carrying framed shader slots, per facing direction, + wall thickness probe
# (ray from 0.05 m inside each slot centre inward) for the next 'Dickson window recesses / blinds' pass.
import bpy, json, math
from mathutils import Vector
w=bpy.data.objects['Dickson Hall walls']; me=w.data; mw=w.matrix_world
fr=bpy.data.objects['PU_Dickson_window_frames_UNVERIFIED']; fm=fr.data
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
dirs={}; faces=[]
for p in me.polygons:
    n=-(mw.to_3x3()@p.normal)
    if abs(n.z)>0.1 or p.area<1: continue
    c=mw@p.center; ang=round(math.degrees(math.atan2(n.y,n.x))/5)*5
    dirs.setdefault(ang,[0,0.0]); dirs[ang][0]+=1; dirs[ang][1]+=p.area
    if len(faces)<400:
        hit,loc,_,_,ob,_=sc.ray_cast(dg,c-n*0.05,-n,distance=3.0)
        faces.append(dict(i=p.index,c=[round(x,2) for x in c],ang=ang,area=round(p.area,1),inner_hit=(ob.name if hit else None),depth=(round((loc-c).length,2) if hit else None)))
out=dict(note='pv prep read-only; wall normals point inward (outward=-normal); east face x>-134 is the pe skin',dirs={str(k):[v[0],round(v[1],1)] for k,v in sorted(dirs.items())},frame_obj_polys=len(fm.polygons),faces=faces)
json.dump(out,open('data/pv/prep_dickson_recess.json','w'),indent=0); print('PREP',out['dirs'],len(faces))
