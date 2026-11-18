import bpy, bmesh, numpy as np, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
os.chdir('/workspace/nj-scenes/montclair-state')
SILL=134.48; PADZ=SILL-0.03; X0,X1,Y0,Y1=213.9,216.15,403.1,408.1; FE=3.0
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']; mw=P.matrix_world; inv=mw.inverted()
bak=np.load('data/wg/patch_z_bak.npy')
orig={int(i):z for i,z in bak}
for i,z in orig.items():
    p=mw@P.data.vertices[i].co; P.data.vertices[i].co=inv@Vector((p.x,p.y,z))
P.data.update(); bpy.context.view_layer.update()
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh()
    t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return t
g=lambda t,x,y:(lambda h:h[0].z if h[0] else None)(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))))
old=bvh(P)
n=0
for v in P.data.vertices:
    p=mw@v.co
    if p.x>X1+0.6: continue
    if p.x>=X0-0.3:
        if Y0-0.3<=p.y<=Y1+0.3: w=1.0
        else: continue
    else:
        d=math.hypot(X0-0.3-p.x, max(Y0-0.3-p.y,0,p.y-Y1-0.3))
        if d>FE: continue
        w=1-d/FE; w=w*w*(3-2*w)
    nz=p.z*(1-w)+PADZ*w
    if abs(nz-p.z)>1e-4: v.co=inv@Vector((p.x,p.y,nz)); n+=1
P.data.update(); bpy.context.view_layer.update(); P['wg_grade']=n
print('regraded',n)
# cheek walls
cm=bpy.data.objects['WG_Bohn_W_door_landing_slab_UNVERIFIED'].data.materials[:]
wallmat=None
for o in bpy.data.objects:
    if o.name.startswith('WD_') and 'wall' in o.name.lower() and o.type=='MESH' and o.data.materials: wallmat=o.data.materials[0]; break
col=bpy.data.collections['WG_Bohn_W_door_landing_UNVERIFIED']
for nm,yc in [('WG_Bohn_W_door_cheek_wall_S_UNVERIFIED',Y0-0.1),('WG_Bohn_W_door_cheek_wall_N_UNVERIFIED',Y1+0.1)]:
    if nm in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[nm])
    bm=bmesh.new(); xs=np.arange(X0-0.4,X1+0.35,0.25); top=[];bot=[]
    for x in xs:
        zt=max([g(old,x,yy) or PADZ for yy in (yc-0.6,yc,yc+0.6) if (yy<Y0 or yy>Y1)]+[PADZ+0.15])+0.10
        r=[bm.verts.new((x,yc+s,zz)) for s in (-0.1,0.1) for zz in (133.6,zt)]
        top.append(r)
    for a,b in zip(top[:-1],top[1:]):
        for i,j in [(0,1),(2,3),(1,3),(0,2)]:
            pass
        bm.faces.new((a[0],b[0],b[1],a[1])); bm.faces.new((a[2],a[3],b[3],b[2])); bm.faces.new((a[1],b[1],b[3],a[3])); bm.faces.new((a[0],a[2],b[2],b[0]))
    bm.faces.new((top[0][0],top[0][1],top[0][3],top[0][2])); bm.faces.new((top[-1][0],top[-1][2],top[-1][3],top[-1][1]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(nm,me); col.objects.link(o); o['wg_obj']=1
    me.materials.append(wallmat or (cm[0] if cm else None))
print('wallmat',wallmat and wallmat.name)
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; bs=bvh(sk); bp=bvh(P)
out=[]
for x in np.arange(209,216.2,0.25):
    for y in np.arange(399,412,0.25):
        a=g(bp,x,y); b=g(bs,x,y)
        if a and b and b-a>0.02 and not (X0-0.05<=x<=X1 and Y0-0.25<=y<=Y1+0.25): out.append((x,y,round(b-a,3)))
print('pokes >2cm outside pad+walls',len(out),'max',max([o[2] for o in out] or [0]), out[:15])
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
