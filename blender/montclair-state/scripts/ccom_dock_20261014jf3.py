"""2026-10-14 ~8:05 PM ET, tag 20261014jf3. Joe 7:56 PM: loading dock off LEFT (south) end of CCOM back.
Evidence: NJ ortho 2020 shows 4 painted truck lanes (white stripes ~2.7 m apart) on paved yard against CCOM south wall,
x~2..12 / y~-24..-28 (scene m) = s -21..-10 on south wall t=-13.8; yard LiDAR ground 136.0-136.5 (flat, no depressed well);
OSM service road (Roads_OSM) meets yard at t~-28. Dock floor = G 137.55 => dock face ~1.1-1.2 m above apron.
UNVERIFIED: door count (=1 per painted lane), door size/colour, bumper layout. No canopy (none visible in ortho). No signage."""
import bpy,sys
from mathutils import Vector
src=open(bpy.path.abspath('//scripts/ccom_joefix_20261014jf.py')).read().split('# 1) hide superseded')[0]
sys.argv=['x']; exec(src)
camsrc=open(bpy.path.abspath('//scripts/ccom_joefix_20261014jf.py')).read().split('# 6) cameras')[1].split("cam('CAM_eye")[0]
exec(camsrc)
T3='20261014jf3'; WALL=-13.8; DOCK=137.55; S0,S1=-21.4,-9.6
tr=bpy.data.objects['Terrain_LiDAR_DTM_1m']; inv=tr.matrix_world.inverted()
def gz(t,s):
    p=W(t,s,300); ok,loc,n,i=tr.ray_cast(inv@p,(inv.to_3x3()@Vector((0,0,-1))).normalized())
    return (tr.matrix_world@loc).z if ok else 136.3
def az(t,s=None):  # apron from raw LiDAR class-2 medians along t (136.3 at wall -> 135.7 at t-26)
    return 136.30+(t-WALL)*0.05
# lower terrain mesh under apron (DTM 1 m ramps up to the wall; raw ground points do not)
mw=tr.matrix_world; k=0
for v in tr.data.vertices:
    p=mw@v.co; t,s_=ts(p)
    if -30<t<WALL+0.5 and -24<s_<-7 and p.z>az(t)-0.08:
        v.co=inv@Vector((p.x,p.y,az(t)-0.08)); k+=1
tr.data.update(); print('terrain lowered',k)
col=colnew('CCOM_loading_dock_'+T3)
m_asph=mat('CCOM_dock_asphalt_'+T3,(0.17,0.17,0.17,1),0.85)
m_conc=mat('CCOM_dock_concrete_'+T3,(0.62,0.61,0.58,1),0.85)
m_door=mat('CCOM_dock_door_'+T3,(0.70,0.71,0.72,1),0.45)
m_slat=mat('CCOM_dock_door_slat_'+T3,(0.55,0.56,0.57,1),0.5)
m_rub=mat('CCOM_dock_bumper_'+T3,(0.03,0.03,0.03,1),0.9)
m_str=mat('CCOM_dock_stripe_'+T3,(0.85,0.85,0.82,1),0.6)
m_stl=mat('CCOM_dock_steel_'+T3,(0.35,0.36,0.37,1),0.4)
# apron: draped grid mesh on LiDAR terrain
import bmesh
TA,TB,SA,SB=-28.5,WALL+0.3,-23.0,-8.0
nt,ns=int((TB-TA)/0.5)+1,int((SB-SA)/0.5)+1
me=bpy.data.meshes.new('CCOM_dock_apron_'+T3); bm=bmesh.new(); V=[]
for i in range(nt):
    row=[]
    for j in range(ns):
        t=TA+(TB-TA)*i/(nt-1); s=SA+(SB-SA)*j/(ns-1)
        row.append(bm.verts.new(W(t,s,max(az(t),gz(t,s)+0.04) if t<-27 else az(t))))
    V.append(row)
for i in range(nt-1):
    for j in range(ns-1): bm.faces.new((V[i][j],V[i+1][j],V[i+1][j+1],V[i][j+1]))
bm.to_mesh(me); bm.free(); me.materials.append(m_asph)
ap=bpy.data.objects.new(me.name,me); col.objects.link(ap)
za=az(WALL-0.4); print('apron z at wall',round(za,2),'dock height',round(DOCK-za,2))
# Joe 8:05 PM: NOT a truck dock - equipment entrance to the equipment cage. Small projecting concrete platform,
# ONE roll-up equipment door (count UNVERIFIED), hinged personnel door on the RIGHT (+s as seen from yard).
RU0,RU1=-18.6,-15.6; PD0,PD1=-14.4,-13.4; PL0,PL1=-19.2,-12.6; PDEP=2.0
box('CCOM_equip_platform_'+T3,col,m_conc,WALL-PDEP,WALL+0.05,PL0,PL1,za-0.3,DOCK)
box('CCOM_equip_platform_nosing_'+T3,col,m_stl,WALL-PDEP-0.02,WALL-PDEP+0.04,PL0,PL1,DOCK-0.05,DOCK)
nst=7; rise=(DOCK-za)/nst
for i in range(nst):  # steps down toward apron in front of personnel door (UNVERIFIED steps vs ramp)
    zt=DOCK-rise*(i+1); t1=WALL-PDEP-0.28*i; t0=t1-0.28
    box(f'CCOM_equip_step{i}_'+T3,col,m_conc,t0,t1,PD0-0.6,PL1,za-0.3,zt)
box('CCOM_equip_rolldoor_'+T3,col,m_door,WALL-0.06,WALL-0.03,RU0,RU1,DOCK,DOCK+3.0)
for q in range(1,15):
    z=DOCK+q*0.2; box(f'CCOM_equip_rolldoor_slat{q}_'+T3,col,m_slat,WALL-0.075,WALL-0.06,RU0,RU1,z-0.012,z)
box('CCOM_equip_rolldoor_hood_'+T3,col,m_stl,WALL-0.35,WALL-0.03,RU0-0.1,RU1+0.1,DOCK+3.0,DOCK+3.45)
for e,sd in ((RU0-0.12,'L'),(RU1+0.04,'R')):
    box('CCOM_equip_rolldoor_jamb'+sd+'_'+T3,col,m_stl,WALL-0.1,WALL-0.02,e,e+0.08,DOCK,DOCK+3.0)
m_pd=mat('CCOM_equip_persdoor_'+T3,(0.32,0.07,0.08,1),0.4)  # maroon to match CCOM frames (UNVERIFIED colour)
box('CCOM_equip_persdoor_'+T3,col,m_pd,WALL-0.05,WALL-0.02,PD0,PD1,DOCK,DOCK+2.13)
box('CCOM_equip_persdoor_frame_'+T3,col,m_stl,WALL-0.08,WALL-0.02,PD0-0.06,PD1+0.06,DOCK+2.13,DOCK+2.2)
for e in (PD0-0.06,PD1):
    box(f'CCOM_equip_persdoor_jamb{e:.1f}_'+T3,col,m_stl,WALL-0.08,WALL-0.02,e,e+0.06,DOCK,DOCK+2.2)
box('CCOM_equip_persdoor_lever_'+T3,col,m_stl,WALL-0.12,WALL-0.05,PD0+0.08,PD0+0.22,DOCK+0.98,DOCK+1.02)
S0,S1=PL0,PL1
# hide ground-level punched windows where the dock face/doors are
for ob in bpy.data.objects:
    if ob.type=='EMPTY' and ob.instance_type=='COLLECTION' and 'CCOM_win' in ob.name:
        t,s=ts(ob.location)
        if abs(t-WALL)<1.5 and S0-1.3<s<S1+1.3 and ob.location.z<140.5:
            ob.hide_render=True; print("hid",ob.name)  # keep viewport on: check_alignment reads matrix_world
    if ob.name.startswith('CCOM_east_clear_') and abs(ts(ob.location)[0]-WALL)<1.5 and S0-1.5<ts(ob.location)[1]<S1+1.5 and ob.location.z<140.5:
        ob.hide_render=True
print('equip entrance built'); cam('CAM_eye_CCOM_loading_dock',W(-27.0,-12.0,az(-27)+1.65),W(WALL,-16.0,DOCK+0.6),20)
bpy.ops.wm.save_mainfile(); print('SAVED')
# --- patch wall openings left by hidden ground-floor windows (outside door spans)
m_wp=bpy.data.materials.get('CCOM_east_pier_20261014jf')
spans=sorted([(RU0-0.15,RU1+0.15),(PD0-0.1,PD1+0.1)])
for ob in bpy.data.objects:
    if ob.type=='EMPTY' and ob.instance_type=='COLLECTION' and ob.name.startswith('CCOM_win_') and ob.hide_render:
        t,s=ts(ob.location)
        if abs(t-WALL)<1.5 and S0-1.3<s<S1+1.3 and ob.location.z<140.5:
            a,b=s-1.45,s+1.45; z0=ob.location.z-1.0; z1=ob.location.z+2.75
            cur=a; segs=[]
            for x0,x1 in spans:
                if x1<a or x0>b: continue
                if x0>cur: segs.append((cur,x0))
                cur=max(cur,x1)
            if cur<b: segs.append((cur,b))
            for i,(u,v) in enumerate(segs):
                box(f'CCOM_equip_wallpatch_{ob.name}_{i}_'+T3,col,m_wp,WALL-0.02,WALL+0.4,u,v,z0,z1)
            for x0,x1 in spans:  # head above doors within this opening
                u,v=max(a,x0),min(b,x1)
                if u<v:
                    top=DOCK+(3.45 if x1-x0>2 else 2.2)
                    if top<z1: box(f'CCOM_equip_wallhead_{ob.name}_{x0:.1f}_'+T3,col,m_wp,WALL-0.02,WALL+0.4,u,v,top,z1)
                    box(f'CCOM_equip_wallback_{ob.name}_{x0:.1f}_'+T3,col,m_wp,WALL+0.3,WALL+0.4,u,v,z0,z1)
print('patched')
bpy.ops.wm.save_mainfile(); print('SAVED2')
