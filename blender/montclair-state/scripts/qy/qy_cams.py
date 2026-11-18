# qy close-up camera at the plaza rim nearest a walk junction (REVERT=1 removes QY_CAM*). UNVERIFIED viewpoint.
import bpy,os,json
from mathutils import Vector
for o in [o for o in bpy.data.objects if o.name.startswith('QY_CAM')]: bpy.data.objects.remove(o,do_unlink=True)
for c in [c for c in bpy.data.cameras if c.name.startswith('QY_CAM') and c.users==0]: bpy.data.cameras.remove(c)
if os.environ.get('REVERT')!='1':
    D=json.load(open('data/scene_data.json')); F={str(f['id']):f for f in D['features']}
    P=[Vector((p[0],p[1])) for p in F['313024781']['pts']]; cen=sum(P,Vector((0,0)))/len(P)
    dec=bpy.data.objects['QY_walk_junction_wear_decals_UNVERIFIED'].data
    # decal centres = verts with qy_w==1
    W=dec.attributes['qy_w'].data; cs=[Vector(dec.vertices[i].co) for i in range(len(dec.vertices)) if W[i].value>0.999]
    def segd(p,a,b):
        ab=b-a; t=max(0,min(1,(p-a).dot(ab)/max(ab.length_squared,1e-9))); return (p-(a+ab*t)).length
    best=min(cs,key=lambda c: min(segd(c.xy,a,b) for a,b in zip(P,P[1:]+P[:1])))
    d=(cen-best.xy).normalized(); eye=best.xy+d*7.0
    cd=bpy.data.cameras.new('QY_CAM_closeup_plaza_rim_junction'); cd.lens=30
    c=bpy.data.objects.new('QY_CAM_closeup_plaza_rim_junction',cd); bpy.data.collections['QY_plaza_rim_band_UNVERIFIED'].objects.link(c)
    c.location=(eye.x,eye.y,best.z+1.7); dv=Vector((best.x,best.y,best.z+0.2))-c.location
    c.rotation_euler=dv.to_track_quat('-Z','Y').to_euler(); print('QYCAM',tuple(round(v,2) for v in c.location),'tgt',tuple(round(v,2) for v in best))
    # rim close-up: midpoint of the longest outline segment north of y 255, camera 6 m inside and 4 m along, 1.6 m up
    segs=[(a,b) for a,b in zip(P,P[1:]+P[:1]) if min(a.y,b.y)>255]
    a,b=max(segs,key=lambda s:(s[1]-s[0]).length); mp=(a+b)/2; t=(b-a).normalized(); n=Vector((-t.y,t.x))
    if n.dot(cen-mp)<0: n=-n
    band=bpy.data.objects['QY_plaza_rim_band_313024781_UNVERIFIED'].data
    z=min((v.co.z for v in band.vertices if (v.co.xy-mp).length<3),default=best.z)+0.14
    def pip(x,y,poly):
        ins=False
        for i in range(len(poly)):
            x1,y1=poly[i]; x2,y2=poly[(i+1)%len(poly)]
            if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
        return ins
    eye=mp+n*6+t*4
    if not pip(eye.x,eye.y,P): n=-n; eye=mp+n*6+t*4
    cd=bpy.data.cameras.new('QY_CAM_closeup_plaza_rim'); cd.lens=28
    c=bpy.data.objects.new('QY_CAM_closeup_plaza_rim',cd); bpy.data.collections['QY_plaza_rim_band_UNVERIFIED'].objects.link(c)
    c.location=(eye.x,eye.y,z+1.6); dv=Vector((mp.x-t.x*2,mp.y-t.y*2,z))-c.location
    c.rotation_euler=dv.to_track_quat('-Z','Y').to_euler(); print('QYCAM2',tuple(round(v,2) for v in c.location),'tgt',tuple(round(v,2) for v in mp),round(z,2))
if os.environ.get('QYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
