# ws121 c: dark slot under the lowest S-side risers = the stair's S side above the WS120 apron was open E of the
# ws120 cheek (x > -215.4). A stair between a plaza and a building wing gets a full-length cheek: extend it to the S-wing face.
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
B=[]
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('WS107_Chapin'):
        mw=o.matrix_world; B.append(BVHTree.FromPolygons([tuple(mw@v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]))
xs=[h[0].x for h in (b.ray_cast(Vector((-216,-201.42,123.3)),Vector((1,0,0)),15) for b in B) if h[0] is not None]
xF=min(xs) if xs else -212.5; print('M121c S-wing face x',round(xF,2))
zc=122.875; zb=zc-0.35
zt=lambda x: min(122.67+(x+217.1)/3.7*2.1+0.12, 124.75+0.12)
wm=ob('WS117_Chapin_W_entrance_cheek').data.materials[0]
me=bpy.data.meshes.new('WS121_Chapin_W_entrance_stair_S_cheek_wall_ext_to_S_wing_white_UNVERIFIED'); o=bpy.data.objects.new(me.name,me)
for c in ob('WS117_Chapin_W_entrance_stair_11R').users_collection: c.objects.link(o)
me.materials.append(wm)
y0,y1=-201.55,-201.28; X=[-215.42+(xF+0.10+215.42)*k/6 for k in range(7)]
bm=bmesh.new(); bot=[];top=[]
for x in X:
    bot.append((bm.verts.new((x,y0,zb)),bm.verts.new((x,y1,zb)))); top.append((bm.verts.new((x,y0,zt(x))),bm.verts.new((x,y1,zt(x)))))
for i in range(6):
    a,b=i,i+1
    bm.faces.new((top[a][0],top[b][0],top[b][1],top[a][1])); bm.faces.new((bot[a][1],bot[b][1],bot[b][0],bot[a][0]))
    bm.faces.new((bot[a][0],bot[b][0],top[b][0],top[a][0])); bm.faces.new((bot[b][1],bot[a][1],top[a][1],top[b][1]))
bm.faces.new((bot[0][0],top[0][0],top[0][1],bot[0][1])); bm.faces.new((bot[6][1],top[6][1],top[6][0],bot[6][0]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
print('M121c cheek ext x',round(X[0],2),round(X[-1],2),'top',round(zt(X[0]),2),round(zt(X[-1]),2))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M121c SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M121c SAVED',SAVE)
