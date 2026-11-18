"""2026-10-14 ~7:50 PM ET, tag 20261014jf2. Joe 7:47 PM markup: raised box + lab one bay RIGHT (+t),
in front of the recessed bay (wall plane s=+3.33, old windows 037/038/040/041). Box = raised structure,
flat top at lab floor, vertical face to LiDAR ground 134.7 (resolves conflict). Old lab bay -> wall w/ punched r1 windows."""
import bpy,sys
from mathutils import Vector
SAVE='--save' in sys.argv
src=open(bpy.path.abspath('//scripts/ccom_joefix_20261014jf.py')).read().split('# 1) hide superseded')[0]
sys.argv=['x']; exec(src)
TAG2='20261014jf2'; SAVE=True
# --- hide old lab glazing, old grade box, old lab instances stay hidden
for ob in bpy.data.objects:
    if TAG2 in ob.name: continue
    if ob.name.startswith(('CCOM_lab_ftc_','CCOM_lab_jamb_N_','CCOM_lab_floor_edge_')) and ob.name.endswith('_20261014jf'):
        ob.hide_render=True; ob.hide_viewport=True
c=bpy.data.collections.get('CCOM_east_grade_20261014jf_UNVERIFIED_height')
if c:
    c.hide_render=True; c.hide_viewport=True
    for o in c.objects: o.hide_render=True
# --- restore old bay: plain wall with punched r1 windows like neighbors
cw=colnew('CCOM_east_oldbay_wall_'+TAG2)
m_w=bpy.data.materials.get('CCOM_east_pier_20261014jf')
z0,z1=FLOOR-0.02,CEIL+0.02; wz0,wz1=139.97,139.97+2.6
cents=[-3.47,-0.07,3.33,6.72]; edges=[-4.6]
segs=[]; prev=-4.6
for cc in cents:
    segs.append((prev,cc-1.3)); prev=cc+1.3
segs.append((prev,8.2))
for i,(a,b) in enumerate(segs):
    if b>a: box(f'CCOM_oldbay_pier{i}_'+TAG2,cw,m_w,a,b,-0.15,0.15,z0,z1)
for i,cc in enumerate(cents):
    box(f'CCOM_oldbay_spandrel{i}_'+TAG2,cw,m_w,cc-1.3,cc+1.3,-0.15,0.15,z0,wz0)
    box(f'CCOM_oldbay_head{i}_'+TAG2,cw,m_w,cc-1.3,cc+1.3,-0.15,0.15,wz1,z1)
for n in ('CCOM_win_044_r1','CCOM_win_047_r1','CCOM_win_050_r1','CCOM_win_053_r1'):
    o=bpy.data.objects.get(n)
    if o: o.hide_render=False; o.hide_viewport=False
# --- shift frame to recessed bay plane
S2=3.33; P0.x+=N.x*S2; P0.y+=N.y*S2
T0,T1=9.8,18.6
for n in ('CCOM_win_037_r0','CCOM_win_038_r1','CCOM_win_040_r0','CCOM_win_041_r1'):
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True; o.hide_viewport=True
for o in bpy.data.objects:
    if o.name.startswith(('CCOM_east_clear_CCOM_win_038','CCOM_east_clear_CCOM_win_041')): o.hide_render=True
LAB2=(T0,T1,-0.8,0.9,FLOOR+0.02,CEIL-0.02)
print('carve lab2',carve_all(LAB2,('atrium glass',)))
col=colnew('CCOM_east_glazing_'+TAG2)
m_glass=bpy.data.materials['CCOM_clear_glass_20261014jf']; m_mar=bpy.data.materials['CCOM_maroon_frame_20261014jf']
m_shade=bpy.data.materials['CCOM_shade_gray_20261014jf']; m_dark=bpy.data.materials['CCOM_shade_bar_20261014jf']
def gl(p,t0,t1,z0,z1,bay,shade_to):
    box(p+'glass',col,m_glass,t0,t1,-0.01,0.01,z0,z1)
    n=max(1,round((t1-t0)/bay))
    for i in range(n+1):
        t=t0+(t1-t0)*i/n; box(f'{p}mull{i}',col,m_mar,t-0.035,t+0.035,-0.08,0.08,z0,z1)
    box(p+'sill',col,m_mar,t0,t1,-0.1,0.1,z0,z0+0.07); box(p+'head',col,m_mar,t0,t1,-0.1,0.1,z1-0.07,z1)
    for i in range(n):
        a=t0+(t1-t0)*i/n+0.05; b=t0+(t1-t0)*(i+1)/n-0.05; zb=shade_to+(0.12 if i%2 else 0)
        box(f'{p}shade{i}',col,m_shade,a,b,-0.14,-0.13,zb,z1-0.05); box(f'{p}bar{i}',col,m_dark,a,b,-0.15,-0.12,zb-0.03,zb)
    box(p+'pocket',col,m_dark,t0,t1,-0.3,-0.1,z1-0.12,z1)
gl('CCOM_lab2_ftc_'+TAG2+'_',T0,T1,FLOOR,CEIL,1.47,141.05)
# --- move lab interior: delta t +12.8, s +3.33; clamp to bay
lab=bpy.data.collections['CCOM_computer_lab_20261014y']
dv=D*12.8+N*S2
for o in lab.objects:
    if o.parent is None: o.location+=dv
bpy.context.view_layer.update()
for o in lab.objects:
    if o.type!='MESH' or o.hide_render: continue
    T=[ts(o.matrix_world@Vector(v))[0] for v in o.bound_box]
    if min(T)>=T0-0.05 and max(T)<=T1+0.05: continue
    big=any(k in o.name.lower() for k in ('wall','floor','ceil','carpet','back'))
    if big:
        mw=o.matrix_world; inv=mw.inverted()
        for v in o.data.vertices:
            q=mw@v.co; t,s_=ts(q); tc=min(max(t,T0),T1)
            if tc!=t: v.co=inv@(q+D*(tc-t))
        o.data.update()
    else: o.hide_render=True; o.hide_viewport=True; print('hid lab obj',o.name)
# --- raised box in front of bay
cg=colnew('CCOM_east_raised_box_'+TAG2)
m_conc=bpy.data.materials['CCOM_grade_concrete_20261014jf']; m_asph=bpy.data.materials['CCOM_grade_strip_20261014jf']
m_yel=bpy.data.materials['CCOM_rail_yellow_20261014jf']; m_h=bpy.data.materials['CCOM_hatch_20261014jf']
GZ=FLOOR-0.03; BT=(T0-0.2,T1+0.2); BS=(0.05,8.0)
box('CCOM_raisedbox_'+TAG2,cg,m_conc,BT[0],BT[1],BS[0],BS[1],133.6,GZ)
box('CCOM_raisedbox_strip_'+TAG2,cg,m_asph,BT[0],BT[1],2.6,5.0,GZ,GZ+0.004)
for i,(t,s) in enumerate(((11.0,1.5),(14.5,1.6),(17.5,1.4),(13.0,5.8),(16.0,6.2))):
    box(f'CCOM_raisedbox_hatch{i}_'+TAG2,cg,m_h,t-0.3,t+0.3,s-0.25,s+0.25,GZ,GZ+0.01)
def rail(t0,s0,t1,s1,name):
    a=Vector((t0,s0)); b=Vector((t1,s1)); L=(b-a).length; n=max(1,int(L/1.8))
    for i in range(n+1):
        p=a+(b-a)*i/n; box(f'{name}_post{i}',cg,m_yel,p.x-0.03,p.x+0.03,p.y-0.03,p.y+0.03,GZ,GZ+1.07)
    for zz,nm in ((1.04,'top'),(0.55,'mid')):
        if abs(t1-t0)>abs(s1-s0): box(f'{name}_{nm}',cg,m_yel,min(t0,t1),max(t0,t1),s0-0.025,s0+0.025,GZ+zz-0.025,GZ+zz+0.025)
        else: box(f'{name}_{nm}',cg,m_yel,t0-0.025,t0+0.025,min(s0,s1),max(s0,s1),GZ+zz-0.025,GZ+zz+0.025)
rail(BT[0]+0.1,7.85,BT[1]-0.1,7.85,'CCOM_rb_rail_E_'+TAG2)
rail(BT[0]+0.1,0.6,BT[0]+0.1,7.85,'CCOM_rb_rail_S_'+TAG2)
rail(BT[1]-0.1,0.6,BT[1]-0.1,7.85,'CCOM_rb_rail_N_'+TAG2)
# --- cams

def cam(name,loc,tgt,lens=24):
    o=bpy.data.objects.get(name)
    if not o: o=bpy.data.objects.new(name,bpy.data.cameras.new(name)); bpy.context.scene.collection.objects.link(o)
    o.location=loc; o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens; o.data.clip_start=0.05; o.data.clip_end=60000
cam('CAM_eye_CCOM_grade_lab',W(15.0,6.9,GZ+1.6),W(14.0,0,GZ+1.3),20)
cam('CAM_eye_CCOM_lab_east',W(14.2,-5.0,FLOOR+1.45),W(14.2,30,FLOOR+0.6),20)
cam('CAM_eye_CCOM_lab_backwindow',W(13.2,-2.4,FLOOR+1.3),W(14.2,10,FLOOR+0.4),17)
# overhead check
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; hits=set()
for t in (10,12,14,16,18):
    for s in (1,4,7):
        h,loc,n,i,ob,_=sc.ray_cast(dg,W(t,s,GZ+0.2),Vector((0,0,1)))
        if h: hits.add(ob.name)
print('OVERHEAD',hits)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
