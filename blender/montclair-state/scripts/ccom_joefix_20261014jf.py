"""2026-10-14 ~7:15 PM ET. Tag 20261014jf. Joe 7:09/7:11 PM corrections.
- No overhang on CCOM east: trim roof/eave plates beyond the east wall line (LiDAR class-6 edge ~x27).
- Lab (2nd fl, east): floor-to-ceiling clear glass, thin maroon mullions, light-gray shades partly down.
- Grade area outside lab: solid flat ground at lab floor with yellow rails, nothing overhead (UNVERIFIED height: LiDAR ground 134.7).
- Lounge moved to EAST facade beside lab, first floor, double height, coplanar glazing (position UNVERIFIED). West lounge hidden.
RERUNNABLE. --save to write."""
import bpy, bmesh, math, sys
from mathutils import Vector
SAVE='--save' in sys.argv; TAG='20261014jf'
P0=Vector((26.30,-13.53,0)); D=Vector((0.2442,0.9697,0)); N=Vector((0.9697,-0.2442,0))
def W(t,s,z): return Vector((P0.x+D.x*t+N.x*s, P0.y+D.y*t+N.y*s, z))
def ts(p): q=Vector((p.x,p.y,0))-P0; return q.dot(D), q.dot(N)
ANG=math.atan2(D.y,D.x)  # local X along wall, local Y = -N? we build in local (t,s) frame via matrix
FLOOR=139.067; CEIL=142.62
LNG_T=(-11.6,-5.4)  # position UNVERIFIED
LNG_Z0=134.85; LNG_Z1=142.62

def colnew(name):
    c=bpy.data.collections.get(name)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
    else:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def mat(name,rgba,rough=0.5,alpha=1.0,trans=0.0,emit=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    o=nt.nodes.new('ShaderNodeOutputMaterial'); b=nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value=rgba; b.inputs['Roughness'].default_value=rough
    b.inputs['Alpha'].default_value=alpha; b.inputs['Transmission Weight'].default_value=trans
    if emit: b.inputs['Emission Color'].default_value=rgba; b.inputs['Emission Strength'].default_value=emit
    nt.links.new(b.outputs[0],o.inputs[0]); m.blend_method='HASHED'
    return m
def box(name,col,m,t0,t1,s0,s1,z0,z1):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    vs=[bm.verts.new(W(t,s,z)) for z in (z0,z1) for (t,s) in ((t0,s0),(t1,s0),(t1,s1),(t0,s1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
    bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o

# ---- carve: bisect + delete faces whose centroid is inside a (t,s,z) box
def carve(ob,t0,t1,s0,s1,z0,z1):
    mw=ob.matrix_world; inv=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(ob.data)
    planes=[(W(t0,0,0),D),(W(t1,0,0),D),(W(0,s0,0),N),(W(0,s1,0),N),(Vector((0,0,z0)),Vector((0,0,1))),(Vector((0,0,z1)),Vector((0,0,1)))]
    nm=inv.to_3x3().transposed()
    for co,no in planes:
        geom=bm.verts[:]+bm.edges[:]+bm.faces[:]
        bmesh.ops.bisect_plane(bm,geom=geom,plane_co=inv@co,plane_no=(nm@no).normalized(),dist=1e-4)
    kill=[]
    for f in bm.faces:
        c=mw@f.calc_center_median(); t,s=ts(c)
        if t0<t<t1 and s0<s<s1 and z0<c.z<z1: kill.append(f)
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    bm.to_mesh(ob.data); bm.free(); ob.data.update(); return len(kill)
def bbox_hit(ob,t0,t1,s0,s1,z0,z1):
    pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    T=[ts(p)[0] for p in pts]; S=[ts(p)[1] for p in pts]; Z=[p.z for p in pts]
    return max(T)>t0 and min(T)<t1 and max(S)>s0 and min(S)<s1 and max(Z)>z0 and min(Z)<z1
NEW=('_'+TAG,)
SKIP_COL={'CCOM_computer_lab_20261014y','CCOM_computer_lab_20261014x'}
def carve_all(box_,excl=()):
    n=0
    for ob in list(bpy.data.objects):
        if ob.type!='MESH' or ob.hide_render or TAG in ob.name or 'Terrain' in ob.name or 'Context_ground' in ob.name: continue
        if any(c.name in SKIP_COL for c in ob.users_collection): continue
        if any(e in ob.name for e in excl): continue
        if ob.data.users>1: continue
        if bbox_hit(ob,*box_):
            k=carve(ob,*box_); 
            if k: print('carved',ob.name,k); n+=k
    return n
def hide_instances(box_):
    for ob in bpy.data.objects:
        if ob.type=='EMPTY' and ob.instance_type=='COLLECTION' and not ob.hide_render:
            t,s=ts(ob.location); t0,t1,s0,s1,z0,z1=box_
            if t0-1<t<t1+1 and s0-2<s<s1+2 and z0-2<ob.location.z<z1+1:
                ob.hide_render=True; ob.hide_viewport=True; print('hid inst',ob.name)

# 1) hide superseded
for cn in ('CCOM_east_terrace_20261014y','CCOM_east_lab_20261014y','CCOM_lounge_20261014z','CCOM_east_terrace_20261014x_UNVERIFIED','CCOM_east_lab_20261014x'):
    c=bpy.data.collections.get(cn)
    if c: c.hide_render=True; c.hide_viewport=True; print('hide col',cn)

# 2) trim roof overhang east of wall (s>0.6) for t in [-12,18.2]
for nm in ['CCOM_east_flat_roof_clean_20261014z','CCOM_east_roof_plate_z2_20261014z','CCOM_east_junction_fill_z2_20261014z',
           'CCOM_east_face_plug_z2_20261014z','CCOM_east_eave_soffit_20261014z','CCOM_east_eave_band_20261014z',
           'School of Communication and Media eave soffit + fascia + rafter','School of Communication and Media roof (LiDAR)']:
    ob=bpy.data.objects.get(nm)
    if ob and ob.modifiers:
        me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        ob.modifiers.clear(); ob.data=me; print('applied mods',nm)
    if ob and len(ob.data.polygons)<=12:
        mw=ob.matrix_world; inv=mw.inverted(); k=0
        for v in ob.data.vertices:
            q=mw@v.co; t,s_=ts(q)
            if s_>0.6: v.co=inv@(q-N*(s_-0.6)); k+=1
        ob.data.update(); print('clamped',nm,k); continue
    if ob: print('trim',nm,carve(ob,-25,18.2,0.6,40,100,200))

# 2b) hide old lab lining piers/sill (photo: thin mullions only)
for ob in bpy.data.objects:
    if ob.name.startswith('CCOM_lab_lining_pier_') or ob.name.startswith('CCOM_lab_lining_sill_'):
        ob.hide_render=True; ob.hide_viewport=True
# 2c) lower terrain inside lounge footprint below floor
tr=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
if tr:
    mw=tr.matrix_world; inv=mw.inverted(); k=0
    for v in tr.data.vertices:
        p=mw@v.co; t,s_=ts(p)
        if LNG_T[0]-0.5<t<LNG_T[1]+0.5 and -8.0<s_<0.2 and p.z>LNG_Z0-0.35:
            v.co=inv@Vector((p.x,p.y,LNG_Z0-0.35)); k+=1
    tr.data.update(); print('terrain lowered',k)
# 3) openings
LAB=(-4.6,7.8,-0.7,0.9,FLOOR+0.02,CEIL-0.02)
LNG=(LNG_T[0],LNG_T[1],-7.6,0.9,LNG_Z0+0.02,LNG_Z1-0.02)
hide_instances(LAB); hide_instances(LNG)
print('carve lab',carve_all(LAB,('atrium glass',)))
print('carve lounge',carve_all(LNG,('atrium glass',)))

col=colnew('CCOM_east_glazing_'+TAG)
m_glass=mat('CCOM_clear_glass_'+TAG,(0.85,0.92,0.95,1),rough=0.02,alpha=0.10,trans=1.0)
m_mar=mat('CCOM_maroon_frame_'+TAG,(0.30,0.06,0.07,1),rough=0.35)
m_shade=mat('CCOM_shade_gray_'+TAG,(0.78,0.78,0.76,1),rough=0.8,alpha=0.72,trans=0.35)
m_dark=mat('CCOM_shade_bar_'+TAG,(0.12,0.12,0.12,1),rough=0.4)
def glazing(prefix,t0,t1,z0,z1,bay,shade_to=None,rows=()):
    box(prefix+'glass_'+TAG,col,m_glass,t0,t1,-0.01,0.01,z0,z1)
    n=max(1,round((t1-t0)/bay)); 
    for i in range(n+1):
        t=t0+(t1-t0)*i/n; box(f'{prefix}mull{i}_{TAG}',col,m_mar,t-0.035,t+0.035,-0.08,0.08,z0,z1)
    box(prefix+'sill_'+TAG,col,m_mar,t0,t1,-0.1,0.1,z0,z0+0.07)
    box(prefix+'head_'+TAG,col,m_mar,t0,t1,-0.1,0.1,z1-0.07,z1)
    for j,z in enumerate(rows): box(f'{prefix}row{j}_{TAG}',col,m_mar,t0,t1,-0.06,0.06,z-0.03,z+0.03)
    if shade_to:
        for i in range(n):
            a=t0+(t1-t0)*i/n+0.05; b=t0+(t1-t0)*(i+1)/n-0.05
            zb=shade_to+(0.12 if i%2 else 0.0)  # pulled to slightly different heights (photo)
            box(f'{prefix}shade{i}_{TAG}',col,m_shade,a,b,-0.14,-0.13,zb,z1-0.05)
            box(f'{prefix}shadebar{i}_{TAG}',col,m_dark,a,b,-0.15,-0.12,zb-0.03,zb)
        box(prefix+'shade_pocket_'+TAG,col,m_dark,t0,t1,-0.3,-0.1,z1-0.12,z1)
glazing('CCOM_lab_ftc_',-4.6,7.8,FLOOR,CEIL,1.55,shade_to=141.05)
# jambs/pier between lab and lounge so openings read as framed
m_wall=mat('CCOM_east_pier_'+TAG,(0.88,0.86,0.80,1),rough=0.6)
box('CCOM_lab_lounge_pier_'+TAG,col,m_wall,-5.4,-4.6,-0.3,0.15,LNG_Z0-0.3,CEIL+0.3)
box('CCOM_lab_jamb_N_'+TAG,col,m_wall,7.8,8.2,-0.3,0.15,FLOOR-0.2,CEIL+0.3)
box('CCOM_lounge_jamb_S_'+TAG,col,m_wall,-12.0,-11.6,-0.3,0.15,LNG_Z0-0.3,CEIL+0.3)
# lab floor edge lining beneath glazing (floor slab visible through glass)
box('CCOM_lab_floor_edge_'+TAG,col,m_wall,-4.6,7.8,-0.3,0.1,FLOOR-0.35,FLOOR)

# 4) grade area outside lab (solid ground, nothing overhead)
cg=colnew('CCOM_east_grade_'+TAG+'_UNVERIFIED_height')
m_conc=mat('CCOM_grade_concrete_'+TAG,(0.70,0.69,0.66,1),rough=0.85)
m_asph=mat('CCOM_grade_strip_'+TAG,(0.42,0.42,0.42,1),rough=0.9)
m_yel=mat('CCOM_rail_yellow_'+TAG,(0.95,0.75,0.05,1),rough=0.45)
m_hatch=mat('CCOM_hatch_'+TAG,(0.30,0.30,0.30,1),rough=0.5)
GT=(-4.6,8.0); GS=(0.05,8.0); GZ=FLOOR-0.03
box('CCOM_grade_fill_'+TAG,cg,m_conc,GT[0],GT[1],GS[0],GS[1],133.6,GZ)
box('CCOM_grade_strip_'+TAG,cg,m_asph,GT[0],GT[1],2.6,5.0,GZ,GZ+0.004)
for i,(t,s) in enumerate(((-2.5,1.5),(1.0,1.6),(4.5,1.4),(2.0,5.8),(-1.0,6.2))):
    box(f'CCOM_grade_hatch{i}_'+TAG,cg,m_hatch,t-0.3,t+0.3,s-0.25,s+0.25,GZ,GZ+0.01)
def rail(t0,s0,t1,s1,name):
    a=Vector((t0,s0)); b=Vector((t1,s1)); L=(b-a).length; n=max(1,int(L/1.8))
    for i in range(n+1):
        p=a+(b-a)*i/n; box(f'{name}_post{i}',cg,m_yel,p.x-0.03,p.x+0.03,p.y-0.03,p.y+0.03,GZ,GZ+1.07)
    for zz,nm in ((1.04,'top'),(0.55,'mid')):
        if abs(t1-t0)>abs(s1-s0): box(f'{name}_{nm}',cg,m_yel,min(t0,t1),max(t0,t1),s0-0.025,s0+0.025,GZ+zz-0.025,GZ+zz+0.025)
        else: box(f'{name}_{nm}',cg,m_yel,t0-0.025,t0+0.025,min(s0,s1),max(s0,s1),GZ+zz-0.025,GZ+zz+0.025)
rail(GT[0]+0.1,7.85,GT[1]-0.1,7.85,'CCOM_rail_E_'+TAG)
rail(GT[0]+0.1,0.6,GT[0]+0.1,7.85,'CCOM_rail_S_'+TAG)
rail(GT[1]-0.1,0.6,GT[1]-0.1,7.85,'CCOM_rail_N_'+TAG)

# 5) east lounge: double height, coplanar glazing, first floor at grade
cl=colnew('CCOM_lounge_east_'+TAG)
glazing('CCOM_lounge_east_',LNG_T[0],LNG_T[1],LNG_Z0,LNG_Z1,1.4,rows=(136.75,138.65,140.55,141.95))
terr=bpy.data.materials.get('CCOM_lounge_terrazzo_20261014z') or mat('CCOM_terrazzo_'+TAG,(0.88,0.88,0.86,1),0.2)
m_w=mat('CCOM_lounge_wall_'+TAG,(0.93,0.93,0.91,1),0.65)
m_blue=bpy.data.materials.get('CCOM_lounge_chair_blue_20261014z') or mat('blue_'+TAG,(0.08,0.35,0.72,1))
m_tab=mat('CCOM_lounge_table_'+TAG,(0.95,0.95,0.93,1),0.25)
m_glow=mat('CCOM_lounge_ceil_light_'+TAG,(1,0.97,0.92,1),0.5,emit=6.0)
t0,t1=LNG_T
box('CCOM_lounge_east_floor_'+TAG,cl,terr,t0,t1,-7.6,0.0,LNG_Z0-0.3,LNG_Z0)
box('CCOM_lounge_east_ceil_'+TAG,cl,m_w,t0,t1,-7.6,0.0,LNG_Z1,LNG_Z1+0.25)
box('CCOM_lounge_east_wallS_'+TAG,cl,m_w,t0-0.2,t0,-7.6,0.0,LNG_Z0,LNG_Z1)
box('CCOM_lounge_east_wallN_'+TAG,cl,m_w,t1,t1+0.2,-7.6,0.0,LNG_Z0,LNG_Z1)
box('CCOM_lounge_east_wallW_'+TAG,cl,m_w,t0,t1,-7.8,-7.6,LNG_Z0,LNG_Z1)
for i,(tt,ss) in enumerate(((-10.4,-1.4),(-10.2,-3.8),(-6.8,-1.6),(-6.6,-4.0))):
    for j in range(2):
        tc=tt+(-0.55 if j==0 else 0.55)
        box(f'CCOM_lounge_east_chair{i}{j}_seat_'+TAG,cl,m_blue,tc-0.32,tc+0.32,ss-0.32,ss+0.32,LNG_Z0+0.40,LNG_Z0+0.48)
        box(f'CCOM_lounge_east_chair{i}{j}_back_'+TAG,cl,m_blue,tc-0.32,tc+0.32,ss-0.36,ss-0.28,LNG_Z0+0.48,LNG_Z0+1.15)
        box(f'CCOM_lounge_east_chair{i}{j}_leg_'+TAG,cl,m_tab,tc-0.03,tc+0.03,ss-0.03,ss+0.03,LNG_Z0,LNG_Z0+0.40)
    box(f'CCOM_lounge_east_table{i}_'+TAG,cl,m_tab,tt-0.35,tt+0.35,ss+0.15,ss+0.75,LNG_Z0+0.72,LNG_Z0+0.76)
    box(f'CCOM_lounge_east_tleg{i}_'+TAG,cl,m_tab,tt-0.03,tt+0.03,ss+0.42,ss+0.48,LNG_Z0,LNG_Z0+0.72)
for i,tt in enumerate((-10.0,-8.5,-7.0)):
    box(f'CCOM_lounge_east_light{i}_'+TAG,cl,m_glow,tt-0.6,tt+0.6,-5.5,-1.5,LNG_Z1-0.02,LNG_Z1)

# 6) cameras
def cam(name,loc,tgt,lens=24):
    o=bpy.data.objects.get(name)
    if not o: o=bpy.data.objects.new(name,bpy.data.cameras.new(name)); bpy.context.scene.collection.objects.link(o)
    o.location=loc; o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens; o.data.clip_start=0.05; o.data.clip_end=60000
cam('CAM_eye_CCOM_grade_lab',W(2.5,6.9,GZ+1.6),W(3.5,0,GZ+1.3),20)
cam('CAM_eye_CCOM_lab_east',W(1.6,-5.6,FLOOR+1.45),W(1.6,30,FLOOR+0.6),20)
cam('CAM_eye_CCOM_lab_backwindow',W(0.4,-2.4,FLOOR+1.3),W(1.4,10,FLOOR+0.4),17)
cam('CAM_eye_CCOM_lounge_east',W(-8.5,-7.2,LNG_Z0+1.5),W(-8.5,20,LNG_Z0+3.0),18)
cam('CAM_oblique_CCOM_east_jf',W(6,45,156),W(5,0,139),30)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
