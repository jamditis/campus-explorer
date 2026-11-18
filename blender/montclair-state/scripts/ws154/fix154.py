# ws154: UNIFY #59 Freeman Hall — blank brick S/N end walls (1965 slide186 + 1971 slide1114), ~1 m roof overhang ring
# (1965/1971 slides + 2019 Montclarion: roof slab projects ~0.9-1.3 m), paler curtained glass (1971 slide1096 + 2019 photo).
import bpy, bmesh, resource, os
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())   # W_N,W_S,E_N,E_S, Z_GRID_TOP, PIER_OUT, brick_mat()
C=(W_N+W_S+E_N+E_S)/4
def frame(A,B):
    u=(B-A).normalized(); n=Vector((u.y,-u.x))
    if ((A+B)/2-C).dot(n)<0: n=-n
    return A,u,n,(B-A).length
ENDS={'N':frame(W_N,E_N),'S':frame(W_S,E_S)}
KEEP=('WS152','WS154','Freeman Hall walls','roof','Roof','parapet','RTU','Balance','dining','forecourt','concrete','curb','Lot9',
      'ground_patch','WALK','CAM','entrance','rail','globe','step','letter','Letter')
def bbd(o,A,u,n):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [(p.xy-A).dot(n) for p in bb],[(p.xy-A).dot(u) for p in bb],[p.z for p in bb]
# z cut per end: S = Balance Kitchen roof (attached 2-storey dining wing), N = top of the entrance canopy
zc={'N':127.0,'S':127.0}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    for k,(A,u,n,L) in ENDS.items():
        d,s,z=bbd(o,A,u,n)
        if (k=='S' and 'Balance_Kitchen' in o.name or k=='N' and 'N_entrance_soffit' in o.name) and min(d)<0.5 and max(s)>0 and min(s)<L:
            zc[k]=max(zc[k],max(z)+0.02)
dg0=bpy.context.evaluated_depsgraph_get(); sc0=bpy.context.scene
A,u,n,L=ENDS['S']; hz=[]
for f in [0.15,0.3,0.45,0.6,0.75,0.9]:
    q=A+u*(L*f)+n*1.2; ok,loc,nor,idx,ob,_=sc0.ray_cast(dg0,Vector((q.x,q.y,160)),Vector((0,0,-1)))
    print('FIX154 S ray',round(f,2),ok and ob.name[:50],ok and round(loc.z,2))
    if ok and ('Balance' in ob.name or 'dining' in ob.name.lower()) and loc.z<zc['S']: hz.append(loc.z)
if hz: hz.sort(); zc['S']=hz[len(hz)//2]-0.05
else: zc['S']=Z_GRID_BOT   # open grade 1.2 m S of the end (LiDAR DTM 125.3): blank brick runs to the ground (1971 slide1114), UNVERIFIED
print('FIX154 BK roof hits',[round(z,2) for z in hz])
print('FIX154 zcut',{k:round(v,2) for k,v in zc.items()})
# 1) delete faces of old Freeman end-wall dressing in the band in front of each end plane, above the cut
cands=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or 'freeman' not in o.name.lower() or '_RETIRED' in o.name or any(k in o.name for k in KEEP): continue
    for k,(A,u,n,L) in ENDS.items():
        d,s,z=bbd(o,A,u,n)
        if max(d)>-0.2 and min(d)<0.6 and max(z)>zc[k] and max(s)>-0.5 and min(s)<L+0.5: cands.append(o); break
print('FIX154 candidates',len(cands),[o.name for o in cands][:60])
tot=0
for o in cands:
    me=o.data
    if me.users>1: o.data=me=me.copy()
    bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world; dl=[]
    for f in bm.faces:
        c=mw@f.calc_center_median()
        for k,(A,u,n,L) in ENDS.items():
            d=(c.xy-A).dot(n); s=(c.xy-A).dot(u)
            if -0.2<=d<=0.6 and -0.5<=s<=L+0.5 and c.z>zc[k]: dl.append(f); break
    nf=len(bm.faces); bmesh.ops.delete(bm,geom=dl,context='FACES'); left=len(bm.faces); bm.to_mesh(me); bm.free(); me.update(); tot+=len(dl)
    if dl: print('FIX154 faces',o.name,nf,'->',left)
    if left==0: o.hide_render=True; o.hide_viewport=True; o.name=o.name[:40]+'_RETIRED_ws154'
print('FIX154 deleted faces',tot)
# lettering on an end wall must stay in front of the new skin
for o in bpy.data.objects:
    if 'letter' in o.name.lower() and 'freeman' in o.name.lower() and not o.hide_render:
        for k,(A,u,n,L) in ENDS.items():
            d,s,z=bbd(o,A,u,n)
            if min(d)<PIER_OUT+0.01 and max(d)>-0.3 and max(s)>0 and min(s)<L and max(z)>zc[k]:
                print('FIX154 lettering near end (NOT moved)',o.name,k,'d',round(min(d),2),round(max(d),2),'z',round(min(z),2),round(max(z),2))
# 2) blank buff-brick end skins (same brick as the WS152 piers), wrapping 0.06 m around the long-façade pier corners
coll=bpy.data.collections.new('WS154_Freeman_end_walls_roof_overhang_slides1965_1971_UNVERIFIED'); bpy.context.scene.collection.children.link(coll)
cream=bpy.data.materials.get('WS154_Freeman_cream_brick_endwall_plane_UNVERIFIED')
if cream is None:
    cream=brick_mat().copy(); cream.name='WS154_Freeman_cream_brick_endwall_plane_UNVERIFIED'
    eu=ENDS['N'][1]
    for nd in cream.node_tree.nodes:
        if nd.type=='MATH' and nd.operation=='MULTIPLY': nd.inputs[1].default_value=eu.x
        if nd.type=='MATH' and nd.operation=='MULTIPLY_ADD': nd.inputs[1].default_value=eu.y
print('FIX154 brick mat',cream.name)
fasc=[m for m in bpy.data.materials if m.name.startswith('WS152_Freeman_fascia_white_metal')]
fasc=fasc[0] if fasc else mat('WS154_Freeman_fascia_white_metal_UNVERIFIED',(0.85,0.86,0.86),0.3,0.3)
soff=mat('WS154_Freeman_soffit_offwhite_UNVERIFIED',(0.72,0.72,0.70),0.6,0.0)
def boxobj(name,corners,z0,z1,mats_):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    v=[bm.verts.new((p.x,p.y,z0)) for p in corners]+[bm.verts.new((p.x,p.y,z1)) for p in corners]
    cen=sum((x.co for x in v),Vector())/8
    for f in [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
        fc=bm.faces.new([v[i] for i in f]); fc.normal_update()
        if fc.normal.dot(fc.calc_center_median()-cen)<0: fc.normal_flip()
        fc.material_index=1 if (len(mats_)>1 and abs(fc.normal.z)>0.9 and fc.normal.z<0) else 0
    bm.to_mesh(me); bm.free()
    for m_ in mats_: me.materials.append(m_)
    o=bpy.data.objects.new(name,me); coll.objects.link(o); return o
for k,(A,u,n,L) in ENDS.items():
    p=lambda s,d: A+u*s+n*d
    o=boxobj(f'WS154_Freeman_{k}_end_wall_blank_buff_brick_slide1114_186_UNVERIFIED',[p(-PIER_OUT-0.02,-0.03),p(L+PIER_OUT+0.02,-0.03),p(L+PIER_OUT+0.02,PIER_OUT),p(-PIER_OUT-0.02,PIER_OUT)],zc[k],Z_GRID_TOP,[cream])
    print('FIX154 end skin',k,'L',round(L,2),'z',round(zc[k],2),Z_GRID_TOP)
A,u,n,L=ENDS['N']; ent=[o for o in bpy.data.objects if o.name.startswith('VT_Freeman_N_entrance_landing')]
fr=None
if ent:
    e=ent[0].matrix_world@(sum((Vector(c) for c in ent[0].bound_box),Vector())/8); fr=(e.xy-A).dot(u)/L
    print('FIX154 N entrance frac from W corner',round(fr,3))
sc_=0.68   # 1965 slide186 read (strip ~0.55-0.85 of the N face from the NW corner); entrance frac only logged
W2=3.0; sa=L*sc_-W2/2; sb=L*sc_+W2/2
gl=bpy.data.materials.get('WS152_Freeman_ribbon_glass_blinds_var_UNVERIFIED'); alu=[m for m in bpy.data.materials if m.name.startswith('WS152') and 'alu' in m.name.lower()]
alu=alu[0] if alu else mat('WS154_Freeman_alu_UNVERIFIED',(0.55,0.56,0.57),0.35,0.8)
me=bpy.data.meshes.new('WS154_Freeman_N_end_glazed_strip'); bm=bmesh.new(); pv=bm.faces.layers.float.new('pane_var'); import random; rr=random.Random(154)
def P2(s_,z,d): q=A+u*s_+n*d; return bm.verts.new((q.x,q.y,z))
def bx(s0,s1,z0,z1,d0,d1,mi,var=0.0):
    v=[P2(s0,z0,d0),P2(s1,z0,d0),P2(s1,z1,d0),P2(s0,z1,d0),P2(s0,z0,d1),P2(s1,z0,d1),P2(s1,z1,d1),P2(s0,z1,d1)]
    cen=sum((x.co for x in v),Vector())/8
    for f in [(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:
        fc=bm.faces.new([v[i] for i in f]); fc.material_index=mi; fc[pv]=var; fc.normal_update()
        if fc.normal.dot(fc.calc_center_median()-cen)<0: fc.normal_flip()
z0g=zc['N']; zt_=Z_GRID_TOP; pitch=(zt_-Z_FLOOR0)/NFL
bx(sa,sb,z0g,zt_,PIER_OUT-0.01,PIER_OUT+0.005,0,0.3)                      # glass back (slightly recessed vs skin face)
zz=Z_FLOOR0
while zz<zt_-0.05:
    if zz>=z0g-0.01: bx(sa,sb,zz-0.04,zz+0.04,PIER_OUT,PIER_OUT+0.03,1)   # floor-line transoms
    zz+=pitch
for k_ in range(4): sm=sa+k_*(W2/3); bx(sm-0.035,sm+0.035,z0g,zt_,PIER_OUT,PIER_OUT+0.035,1)
for f in bm.faces:
    if f.material_index==0: f[pv]=rr.random()
bm.to_mesh(me); bm.free(); me.materials.append(gl); me.materials.append(alu)
og=bpy.data.objects.new(me.name+'_slide186_1965_UNVERIFIED',me); coll.objects.link(og)
print('FIX154 N glazed strip s',round(sa,2),round(sb,2),'frac',round(sc_,3))
# 3) roof overhang ring: soffit 146.2 flush with the top of the window grid, fascia to the parapet top 147.15, 1.0 m out, 0.4 m in
Au=(W_S-W_N).normalized(); An=Vector((Au.y,-Au.x))
if (C-(W_N+W_S)/2).dot(An)<0: An=-An        # An points W->E (inward from W)
ss=[(q-C).dot(Au) for q in (W_N,W_S,E_N,E_S)]; tt=[(q-C).dot(An) for q in (W_N,W_S,E_N,E_S)]
s0,s1,t0,t1=min(ss),max(ss),min(tt),max(tt)
def ring(off): return [C+Au*(s0-off)+An*(t0-off),C+Au*(s1+off)+An*(t0-off),C+Au*(s1+off)+An*(t1+off),C+Au*(s0-off)+An*(t1+off)]
OUT,IN=1.0,0.4
me=bpy.data.meshes.new('WS154_Freeman_roof_overhang_1m_soffit'); bm=bmesh.new()
ro=ring(OUT); ri=ring(-IN); z0,z1=Z_GRID_TOP,147.15
vo0=[bm.verts.new((p.x,p.y,z0)) for p in ro]; vo1=[bm.verts.new((p.x,p.y,z1)) for p in ro]
vi0=[bm.verts.new((p.x,p.y,z0)) for p in ri]; vi1=[bm.verts.new((p.x,p.y,z1)) for p in ri]
for i in range(4):
    j=(i+1)%4
    for q,mi in [((vo0[i],vo0[j],vo1[j],vo1[i]),0),((vi0[j],vi0[i],vi1[i],vi1[j]),0),((vo1[i],vo1[j],vi1[j],vi1[i]),0),((vo0[j],vo0[i],vi0[i],vi0[j]),1)]:
        f=bm.faces.new(q); f.material_index=mi
bm.normal_update()
for f in bm.faces:
    c=f.calc_center_median(); out=Vector((c.x-C.x,c.y-C.y,0))
    want=(-1 if f.material_index==1 else (1 if abs(f.normal.z)>0.9 else 0))
    if want and f.normal.z*want<0: f.normal_flip()
bm.to_mesh(me); bm.free(); me.materials.append(fasc); me.materials.append(soff)
oR=bpy.data.objects.new(me.name+'_slides_Montclarion2019_UNVERIFIED',me); coll.objects.link(oR)
print('FIX154 roof ring s',round(s0,2),round(s1,2),'t',round(t0,2),round(t1,2))
# old 0.32 m WS152 fascia boxes would poke through the soffit: drop their faces above the grid top
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('WS152_Freeman') and 'facade' in o.name.lower():
        me=o.data; bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world
        dl=[f for f in bm.faces if min((mw@v.co).z for v in f.verts)>=Z_GRID_TOP-0.01]
        bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(me); bm.free(); me.update(); print('FIX154 old fascia faces',o.name,len(dl))
# 4) paler curtained glass (1971 entrance slide: pale curtains; 2019: most panes light grey/white)
g=bpy.data.materials.get('WS152_Freeman_ribbon_glass_blinds_var_UNVERIFIED')
if g:
    for nd in g.node_tree.nodes:
        if nd.type=='VALTORGB':
            e=nd.color_ramp.elements; e[0].position=0.15; e[0].color=(0.075,0.08,0.085,1); e[1].position=0.85; e[1].color=(0.56,0.55,0.50,1)
    print('FIX154 glass paler')
# 5) close-up camera on today's detail: SW corner — S end wall + soffit from the W lawn
T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def gz(x,y,d):
    if not T: return d
    mi=T.matrix_world.inverted(); ok,loc,_,_=T.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else d
A,u,n,L=ENDS['S']; wn=-An   # W outward
pos2=W_S+Au*14+wn*16; pos=Vector((pos2.x,pos2.y,gz(pos2.x,pos2.y,127.3)+1.6)); tgt=Vector((W_S.x,W_S.y,141.0))
c=bpy.data.objects.get('WS154_CAM_closeup_Freeman_SW_corner_soffit') or bpy.data.objects.new('WS154_CAM_closeup_Freeman_SW_corner_soffit',bpy.data.cameras.new('WS154_CAM_closeup_Freeman_SW_corner_soffit'))
c.data.lens=24; c.location=pos; c.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
if c.name not in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.link(c)
print('FIX154 cam',tuple(round(x,2) for x in pos))
bpy.ops.wm.save_as_mainfile(filepath=os.environ.get('OUT154',M+'montclair_state_ws154a.blend'),copy=True)
print('SAVED_WS154A RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
