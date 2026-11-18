# ws95: Footpaths_OSM hook stub off the lot E end (source mesh).
# 2020 ortho shows the diagonal walk (lot SE corner -> lane at x~-204) but NO walk on the hook's N leg (x~-205, y -91..-86)
# or W leg (y~-85..-88, over the mulch bed / white utility pad) -> delete those faces (dead-end stub with V-notched end),
# square the new NE edge of the diagonal, and fill the V-notch at the S-leg/diagonal corner (116-117-118-119).
import bpy,bmesh,os
from mathutils import Vector
o=bpy.data.objects['Footpaths_OSM']; me=o.data; mw=o.matrix_world; imw=mw.inverted()
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def W(v): return mw@v.co
# sanity: the known verts must be where ws95 dumped them
chk={116:(-217.62,-97.13),119:(-216.74,-96.1),126:(-207.15,-92.13),151:(-204.14,-91.86),8234:(-205.0,-91.0)}
for k,(x,y) in chk.items():
    w=W(bm.verts[k]); assert abs(w.x-x)<0.05 and abs(w.y-y)<0.05,(k,w)
R={k:bm.verts[k] for k in (116,117,118,119,126,151,8234)}
dele=[]
for f in bm.faces:
    c=sum((W(v) for v in f.verts),Vector())/len(f.verts)
    if -218.5<c.x<-203.3 and -91.75<c.y<-82.5: dele.append(f)
print("FX95 delete faces",len(dele))
bmesh.ops.delete(bm,geom=dele,context='FACES')
# square the new edge 126 -> 8234 -> 151: put 8234 on the straight line 126-151
a,b=W(R[126]),W(R[151]); v=R[8234]; assert v.is_valid and R[126].is_valid and R[151].is_valid; p=W(v)
t=((p-a).to_2d().dot((b-a).to_2d()))/((b-a).to_2d().length_squared)
q=a.lerp(b,t); v.co=imw@Vector((q.x,q.y,p.z)); dm=(q.to_2d()-p.to_2d()).length; print("FX95 8234 moved",round(dm,3)); assert dm<1.2
# fill V-notch at the S-leg / diagonal corner
vs=[R[i] for i in (116,117,118,119)]
try:
    f=bm.faces.new(vs); f.normal_update()
    if (mw.to_3x3()@f.normal).z<0: f.normal_flip()
    print("FX95 notch filled")
except ValueError as e: print("FX95 notch skip",e)
loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS'); print("FX95 loose removed",len(loose))
bm.to_mesh(me); me.update(); bm.free()
print("FX95 verts now",len(me.vertices))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("FX95 SAVED")
