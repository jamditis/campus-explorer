# ok (Oct 31 2026): Schmitt Hall follow-ups after oj, after schmitt_01/02 (refs/web/20261031):
# (1) og punched windows still visible on the NW/WNW/SSW/NNE and ESE lower rows get per-row mullion/transom grids in the
#     red-brown frame family (1F/walk-out: 2x2 lites like the photographed 1F windows; 2F: 3 mullions + transom like the
#     arched 2F grid; top floor: 3 mullions + high transom like the top bands) and a light cast-stone sill under each;
# (2) pavilion return faces get the split-face block plinth course (same pier plinth material) + a light cast-stone cap
#     ledge, which also caps the front pier plinths (schmitt_02 shows the cap). Nothing deleted/hidden; no wall booleans.
# All sizes UNVERIFIED (photo shows only the pavilion facade). REVERT=1 removes the collection + materials.
# Usage: blender -b main --python ok_build.py -- --save
import bpy, bmesh, math, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OK_Schmitt_window_grids_sills_return_plinth_20261031ok'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
for n in [m.name for m in bpy.data.materials if m.name.startswith('OK_Schmitt_')]: bpy.data.materials.remove(bpy.data.materials[n])
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
sc=bpy.context.scene; bpy.context.view_layer.update()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
red=bpy.data.materials['OH_Schmitt_win_frame_red_brown']; blk=bpy.data.materials['OI_Schmitt_pier_block_plinth_UNVERIFIED']
cs=bpy.data.materials.new('OK_Schmitt_cast_stone_sill_UNVERIFIED'); cs.use_nodes=True; nt=cs.node_tree; p=nt.nodes['Principled BSDF']
p.inputs['Base Color'].default_value=(0.60,0.585,0.55,1); p.inputs['Roughness'].default_value=0.82
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.name='OK_noise'; nz.inputs['Scale'].default_value=90; bp=nt.nodes.new('ShaderNodeBump'); bp.name='OK_bump'; bp.inputs['Strength'].default_value=0.12
nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],p.inputs['Normal'])
def newobj(name,bm,m,note):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['UNVERIFIED']=note; return o
def cube(bm,F,x0,x1,y0,y1,z0,z1,wash=0.0):
    vs=[]
    for z in (z0,z1):
        for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
            zz=z-(wash if (z==z1 and y==y1) else 0.0); vs.append(bm.verts.new(F(x,y,zz)))
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
# ---- 1 window grids + cast-stone sills ----
mb=bmesh.new(); sb=bmesh.new(); n=0
for o in bpy.data.objects:
    if not o.name.startswith('SCH_win_') or o.hide_render: continue
    M=o.matrix_world; c=M.translation.copy(); X=(M.to_3x3()@Vector((1,0,0))).normalized(); Y=(M.to_3x3()@Vector((0,1,0))).normalized()
    def F(x,y,z,c=c,X=X,Y=Y): return c+X*x+Y*y+Vector((0,0,z))
    HW=1.3*o.scale.x; H=2.6*o.scale.z; row=o.get('row',0); W=0.055; y0,y1=-0.165,-0.10
    if row<=0: xs=[0.0]; zt=[H*0.52]
    elif row==1: xs=[-HW/2,0.0,HW/2]; zt=[H*0.70]
    else: xs=[-HW/2,0.0,HW/2]; zt=[H*0.78]
    for x in xs: cube(mb,F,x-W/2,x+W/2,y0,y1,0.0,H)
    for z in zt: cube(mb,F,-HW,HW,y0,y1-0.005,z-W/2,z+W/2)
    cube(sb,F,-0.95*HW/0.8,0.95*HW/0.8,-0.03,0.10,-0.105,-0.035,wash=0.012)
    n+=1
newobj('OK_Schmitt_punched_window_mullion_grids',mb,red,'ok: lite pattern by storey from schmitt_01/02 (pavilion facade only)')
newobj('OK_Schmitt_punched_window_cast_stone_sills',sb,cs,'ok: sill size/colour guessed from schmitt_02')
print('windows',n)
# ---- 2 pavilion return plinth + cap ledge (pavilion frame as in oi/oj) ----
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb)
OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0)); cen.z=0
def P(a,o_,z): return cen+AL*a+OUT*o_+Vector((0,0,z))
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tmi=ter.matrix_world.inverted()
def tz(q):
    h,l,n_,i=ter.ray_cast(tmi@Vector((q.x,q.y,400)),tmi.to_3x3()@Vector((0,0,-1))); return (ter.matrix_world@l).z if h else 138.3
HA=3.80; AW=2.30; OF=0.67; OW=-4.95
pb=bmesh.new(); cb=bmesh.new(); zb={}
for s in (-1,1):
    zmin=min(tz(P(s*3.9,o_,0)) for o_ in [OW+k*(OF-OW)/12 for k in range(13)]); zb[s]=round(zmin,3)
    def Fa(x,y,z,s=s): return P(s*x,y,z)
    # block course: outer face 3.86 (2 cm inside the oi pier plinth face 3.88 where they overlap, no coplanar faces)
    a0,a1=HA-0.03,HA+0.06
    cube(pb,lambda x,y,z,s=s: P(x,y,z),min(s*a0,s*a1),max(s*a0,s*a1),OW,-0.10,zmin-0.30,139.955)
    # cap ledge over return plinth + front pier plinth (pier plinth: a 2.32..3.88, o -0.23..0.75, top 139.98)
    c0,c1=HA-0.02,HA+0.115
    cube(cb,lambda x,y,z: P(x,y,z),min(s*c0,s*c1),max(s*c0,s*c1),OW,OF+0.115,139.955,140.045,)
    c0,c1=AW+0.005,HA-0.02
    cube(cb,lambda x,y,z: P(x,y,z),min(s*c0,s*c1),max(s*c0,s*c1),OF-0.93,OF+0.115,139.975,140.045)
newobj('OK_Schmitt_pavilion_return_block_plinth',pb,blk,'ok: return plinth height/extent from schmitt_02 (one return visible)')
newobj('OK_Schmitt_pavilion_plinth_cast_stone_cap',cb,cs,'ok: cap ledge from schmitt_02; size guessed')
print('return terrain min',zb)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
