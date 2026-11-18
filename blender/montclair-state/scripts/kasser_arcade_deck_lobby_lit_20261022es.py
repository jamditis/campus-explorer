"""Session es (Oct 22 ~8:45 AM ET). MAIN blend. The deck door glass at the west (deck) end of Kasser's level-4 arcade read as opaque dark,
because the single-sided 'Alexander Kasser Theater walls' face sat 5 cm behind the glass; Joe's Oct 19 photo
(refs/joe/kasser_level4_arcade_joe_20261019.jpg) shows a lit interior behind that door. This script:
  1. bisects the walls mesh at the door opening (u 0.475..2.275, z 131.40..133.70 in the er door frame) and deletes only the wall
     faces inside the opening (|s-1.80| < 0.12), so the glass now looks through;
  2. adds 'Kasser_arcade_deck_lobby_es' - a closed 4.0 m deep lobby box behind the door (white painted walls, grey sealed-concrete
     floor, ceiling) with two emissive linear ceiling fixtures, plus a small area light 'Kasser_arcade_deck_lobby_light_es'.
Interior layout/finishes UNVERIFIED (photo only shows a bright interior through the glass). A rerun of the ck/cl Kasser chain restores the
deleted wall faces -> rerun er door + this script after it. Idempotent for the lobby objects; SAVE=1 saves."""
import bpy, bmesh, os, numpy as np
from mathutils import Vector
SAVE = os.environ.get('SAVE','0')=='1'
A=np.array([-250.1,-46.7]); B=np.array([-237.3,3.8]); d=(B-A)/np.linalg.norm(B-A); n=np.array([d[1],-d[0]])
def xy(s,u): return A+n*s+d*u
def su(co): p=np.array(co[:2])-A; return float(p@n), float(p@d)
U0,U1,Z0,ZH=0.475,2.275,131.40,133.70
wo=bpy.data.objects['Alexander Kasser Theater walls']; me=wo.data; mw=wo.matrix_world
bm=bmesh.new(); bm.from_mesh(me); bm.transform(mw)
def near(f):
    c=f.calc_center_median(); vs=[su(v.co) for v in f.verts]; zs=[v.co.z for v in f.verts]
    return min(abs(s-1.80) for s,_ in vs)<0.15 and max(abs(s-1.80) for s,_ in vs)<0.15 and min(u for _,u in vs)<U1+0.3 and max(u for _,u in vs)>U0-0.3 and min(zs)<ZH+0.3 and max(zs)>Z0-0.3
fs=[f for f in bm.faces if near(f)]
print('es lobby: wall faces near opening', len(fs), flush=True)
dvec=Vector((d[0],d[1],0))
for co,no in ((Vector((*xy(1.8,U0),0)),dvec),(Vector((*xy(1.8,U1),0)),dvec),(Vector((0,0,Z0)),Vector((0,0,1))),(Vector((0,0,ZH)),Vector((0,0,1)))):
    geom=list(set([e for f in fs if f.is_valid for e in f.edges]+[f for f in fs if f.is_valid]+[v for f in fs if f.is_valid for v in f.verts]))
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    fs=[f for f in bm.faces if f.is_valid and near(f)]
dele=[]
for f in fs:
    c=f.calc_center_median(); s,u=su(c)
    if U0+0.01<u<U1-0.01 and Z0+0.01<c.z<ZH-0.01 and abs(s-1.80)<0.12: dele.append(f)
print('es lobby: wall faces deleted', len(dele), 'area %.2f'%sum(f.calc_area() for f in dele), flush=True)
bmesh.ops.delete(bm, geom=dele, context='FACES'); bm.transform(mw.inverted()); bm.to_mesh(me); bm.free(); me.update()
# 3. door glass: the ck glass faces use the shared opaque dark Kasser_window_glass_cj (transmission 0) -> give only the faces inside
#    the door opening a clear, lightly tinted transmissive glass so the lit lobby shows through (other Kasser windows untouched)
ro=bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; rm=ro.data; rmw=ro.matrix_world
gi=[i for i,m in enumerate(rm.materials) if m and m.name=='Kasser_window_glass_cj']
cg=bpy.data.materials.get('es_deck_door_glass_clear') or bpy.data.materials.new('es_deck_door_glass_clear'); cg.use_nodes=True
gb=cg.node_tree.nodes['Principled BSDF']; gb.inputs['Base Color'].default_value=(0.86,0.90,0.90,1); gb.inputs['Roughness'].default_value=0.02
gb.inputs['Transmission Weight'].default_value=1.0; gb.inputs['IOR'].default_value=1.45   # parallel 2-face slab: offsets cancel, keeps Fresnel reflection
if cg.name not in [m.name for m in rm.materials if m]: rm.materials.append(cg)
ci=[i for i,m in enumerate(rm.materials) if m and m.name==cg.name][0]; ng=0
for f in rm.polygons:
    if f.material_index in gi:
        c=rmw@f.center; s_,u_=su(c)
        if 1.7<s_<2.05 and U0<u_<U1 and Z0<c.z<ZH: f.material_index=ci; ng+=1
print('es lobby: door glass faces -> clear', ng, flush=True)
for nm in ('Kasser_arcade_deck_lobby_es','Kasser_arcade_deck_lobby_light_es'):
    o=bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)
def mat(name,col,rough,emit=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=rough
    if emit: b.inputs['Emission Color'].default_value=(1.0,0.95,0.86,1); b.inputs['Emission Strength'].default_value=emit
    return m
mw_=mat('es_lobby_wall_white',(0.62,0.61,0.58,1),0.8); mbk=mat('es_lobby_back_wall_grey',(0.36,0.36,0.35,1),0.7); mcb=mat('es_lobby_cove_base_dark',(0.04,0.04,0.04,1),0.6); mf=mat('es_lobby_floor_sealed_concrete',(0.32,0.31,0.29,1),0.35)
mc=mat('es_lobby_ceiling',(0.70,0.70,0.68,1),0.9); ml=mat('es_lobby_led_fixture',(1,1,1,1),0.5,emit=7.0)
SB,SF=-2.2,1.78; UA,UB=-0.4,3.2; ZF,ZC=Z0+0.005,Z0+3.0
bm=bmesh.new()
def P(s,u,z): return bm.verts.new((*xy(s,u),z))
def quad(pts,mi):
    f=bm.faces.new([P(*p) for p in pts]); f.material_index=mi
quad([(SB,UA,ZF),(SF,UA,ZF),(SF,UB,ZF),(SB,UB,ZF)],1)                     # floor
quad([(SB,UA,ZC),(SB,UB,ZC),(SF,UB,ZC),(SF,UA,ZC)],2)                     # ceiling
quad([(SB,UA,ZF),(SB,UB,ZF),(SB,UB,ZC),(SB,UA,ZC)],4)                     # back wall (painted block, darker; UNVERIFIED)
for (pa,pb) in (((SB+0.01,UA),(SB+0.01,UB)),((SB,UA+0.01),(SF,UA+0.01)),((SB,UB-0.01),(SF,UB-0.01))):
    quad([(pa[0],pa[1],ZF+0.002),(pb[0],pb[1],ZF+0.002),(pb[0],pb[1],ZF+0.10),(pa[0],pa[1],ZF+0.10)],5)   # 10 cm cove base
quad([(SB,UA,ZF),(SB,UA,ZC),(SF,UA,ZC),(SF,UA,ZF)],0)                     # side walls
quad([(SB,UB,ZF),(SF,UB,ZF),(SF,UB,ZC),(SB,UB,ZC)],0)
# front wall around the opening (inside face, 2 cm behind the deleted wall plane) so the box is closed
for (ua,ub,za,zb) in ((UA,U0,ZF,ZC),(U1,UB,ZF,ZC),(U0,U1,ZH,ZC)):
    quad([(SF,ua,za),(SF,ub,za),(SF,ub,zb),(SF,ua,zb)],0)
for uc in (0.6,2.2):                                                       # two linear fixtures running front-to-back
    quad([(SB+0.5,uc-0.08,ZC-0.01),(SF-0.5,uc-0.08,ZC-0.01),(SF-0.5,uc+0.08,ZC-0.01),(SB+0.5,uc+0.08,ZC-0.01)],3)
me2=bpy.data.meshes.new('Kasser_arcade_deck_lobby_es'); bm.to_mesh(me2); bm.free()
for m in (mw_,mf,mc,ml,mbk,mcb): me2.materials.append(m)
ob=bpy.data.objects.new('Kasser_arcade_deck_lobby_es',me2); wo.users_collection[0].objects.link(ob)
ob['es']='lit lobby behind the arcade deck door (Joe photo shows a bright interior); layout/finishes UNVERIFIED'
ld=bpy.data.lights.new('Kasser_arcade_deck_lobby_light_es','AREA'); ld.shape='RECTANGLE'; ld.size=2.5; ld.size_y=1.2; ld.energy=45; ld.color=(1.0,0.95,0.87)
lo=bpy.data.objects.new('Kasser_arcade_deck_lobby_light_es',ld); lo.location=(*xy(-0.2,1.4),ZC-0.05); wo.users_collection[0].objects.link(lo)
print('es lobby: built', len(me2.polygons), 'faces', flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('es lobby main: SAVED', flush=True)
