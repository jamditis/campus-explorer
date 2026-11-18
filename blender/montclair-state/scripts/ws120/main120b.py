# ws120 self-review fix: #25 residual hump at the stair S corner + open/black S side of the stair
import bpy, bmesh, os
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
zc=122.875
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=ob(nm); mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if -201.6<=w.y<=-199.0 and -217.5<=w.x<=-213.0 and w.z>zc-0.10:
            w.z=zc-0.10; v.co=inv@w; n+=1
    o.data.update(); print('M120b clamp',nm,n)
wm=ob('WS117_Chapin_W_entrance_cheek').data.materials[0]
me=bpy.data.meshes.new('WS120_Chapin_W_entrance_stair_S_cheek_wall_white_UNIFY25_UNVERIFIED'); o=bpy.data.objects.new(me.name,me)
for c in ob('WS117_Chapin_W_entrance_stair_11R').users_collection: c.objects.link(o)
me.materials.append(wm)
x0,x1=-217.15,-215.4; y0,y1=-201.55,-201.28; zb=zc-0.35
zt=lambda x: 122.67+(x+217.1)/3.7*2.1+0.12
bm=bmesh.new()
V=[bm.verts.new(c) for c in ((x0,y0,zb),(x1,y0,zb),(x1,y1,zb),(x0,y1,zb),(x0,y0,zt(x0)),(x1,y0,zt(x1)),(x1,y1,zt(x1)),(x0,y1,zt(x0)))]
for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bm.faces.new([V[i] for i in f])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
print('M120b cheek top',round(zt(x0),2),round(zt(x1),2))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M120b SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M120b SAVED',SAVE)
