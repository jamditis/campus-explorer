# ws122: Chapin window rebuild layout. Storey datums from the WS117 entrance FFE (124.77, LiDAR2023 terrace) ;
# columns on a shared 3.2 m grid per facade plane; rows kept only where they clear FINISHED grade (evaluated ground).
import bpy, bmesh, json, math, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=os.environ.get('OUT','/workspace/nj-scenes/montclair-state/scripts/ws122/layout122.json')
MODE=os.environ.get('MODE','layout')   # layout | check
FFE=124.77; F2F=3.5; SILL_ABOVE_FFE=0.9; GW=1.0; GH=1.6; FR=0.10; SP=3.2
CLEAR=0.45   # min frame/sill bottom above finished grade
GROUND_PRE=('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch','Footpaths_OSM','Roads_OSM','WS102_','WS103_','WS106_','WS112_','WS115_','WS116_','WS27_CollegeAve_carriageway','WS27_CollegeAve_curb')
GROUND_WS=('WS105_Chapin_E_bank_planting','WS105_Chapin_E_bank_retaining','WS105_Chapin_E_bank_stair_cheek','WS105_Chapin_E_bank_stairs','WS105_PanzerE',
 'WS117_Chapin_W_entrance_cheek','WS117_Chapin_W_entrance_landing','WS117_Chapin_W_entrance_stair_11R','WS119_','WS120_Chapin_W_N_plaza','WS120_Chapin_W_S_wing','WS120_Chapin_W_entrance_stair_S','WS120_Chapin_W_round_planter_D','WS120_Chapin_W_round_planter_mulch','WS121_')
def isground(n): return n.startswith(GROUND_PRE+GROUND_WS)
keep=lambda n: isground(n) or n.startswith(('WS107_Chapin_','WS108_Chapin_windows','WS122_Chapin_windows','WS117_Chapin_W_entrance_doors','WS117_Chapin_W_entrance_frame'))
for o in list(bpy.data.objects):
    if o.type=='MESH' and not keep(o.name): bpy.data.objects.remove(o)
    elif o.type not in ('MESH',) and o.type!='EMPTY': bpy.data.objects.remove(o)
dg=bpy.context.evaluated_depsgraph_get()
gb=bmesh.new(); ng=0
for o in bpy.data.objects:
    if o.type=='MESH' and isground(o.name) and o.visible_get() is not None:
        if o.name.startswith('WS113_paving_tops_proxy'): continue
        oe=o.evaluated_get(dg); me=oe.to_mesh()
        tmp=bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world)
        # crop to Chapin area
        dele=[v for v in tmp.verts if not (-250<v.co.x<-140 and -250<v.co.y<-135)]
        bmesh.ops.delete(tmp,geom=dele,context='VERTS')
        m2=bpy.data.meshes.new('tmp'); tmp.to_mesh(m2); tmp.free(); gb.from_mesh(m2); bpy.data.meshes.remove(m2); oe.to_mesh_clear(); ng+=1
GB=BVHTree.FromBMesh(gb); print('L ground objs',ng,'faces',len(gb.faces))
def ground(p):
    h=GB.ray_cast(Vector((p.x,p.y,160.0)),Vector((0,0,-1)))
    return None if h[0] is None else h[0].z
vols=[]; vbm=[]
for o in bpy.data.objects:
    if o.name.startswith('WS107_Chapin_') and o.type=='MESH':
        bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]); bm.normal_update()
        vols.append(BVHTree.FromBMesh(bm)); vbm.append((o.name,bm))
def inside(p):
    for t in vols:
        n=0; q=p.copy()
        for _ in range(40):
            loc,nr,i,d=t.ray_cast(q,Vector((0,0,1)))
            if loc is None: break
            n+=1; q=loc+Vector((0,0,1e-4))
        if n%2==1: return True
    return False
def blocked(p,nh):
    for t in vols:
        h=t.ray_cast(p+nh*0.05,nh,1.2)
        if h[0] is not None: return True
    return False
def gmax(c,u,nh,hw):
    zs=[]
    for a in (-hw-0.1,-hw/2,0,hw/2,hw+0.1):
        for d in (0.12,0.5,0.9):
            z=ground(c+u*a+nh*d)
            if z is not None: zs.append(z)
    return max(zs) if zs else None
DOOR=(-213.2,-208.4,-201.9,-195.9,131.0)
def in_door(p): return DOOR[0]<p.x<DOOR[1] and DOOR[2]<p.y<DOOR[3] and p.z<DOOR[4]
if MODE=='check':
    # per-window bottom vs ground, from the WS122 (or WS108) window object: windows = connected islands
    name=os.environ.get('WIN','WS122_Chapin_windows_storey_datum_FFE124p77_UNVERIFIED')
    o=bpy.data.objects[name]; bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    import collections
    islands=[]; seen=set()
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; isl=[]; seen.add(v.index)
        while st:
            x=st.pop(); isl.append(x.co.copy())
            for e in x.link_edges:
                y=e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        islands.append(isl)
    if name.startswith('WS108'):  # ws108 frame+glass quads are separate islands: merge by centre xy
        grp={}
        for isl in islands:
            c=sum(isl,Vector())/len(isl); k=(round(c.x,1),round(c.y,1),round(c.z-0.0,0))
            grp.setdefault((round(c.x,0),round(c.y,0),round(c.z,0)),[]).extend(isl)
        islands=list(grp.values())
    if name.startswith('WS122'):
        LJ=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws122/layout122.json'))['wins']
        grp={}
        for isl in islands:
            c=sum(isl,Vector())/len(isl)
            k=min(range(len(LJ)),key=lambda i:(LJ[i]['c'][0]-c.x)**2+(LJ[i]['c'][1]-c.y)**2+(LJ[i]['c'][2]-c.z)**2)
            grp.setdefault(k,[]).extend(isl)
        islands=list(grp.values())
    res=[]; below=0; lt30=0; mins=[]
    for isl in islands:
        zb=min(p.z for p in isl); xs=[p.x for p in isl]; ys=[p.y for p in isl]
        g=-1e9
        for p in isl:
            z=ground(p)
            if z is not None: g=max(g,z)
        # also sample 0.5 m around the window centre footprint
        c=sum(isl,Vector())/len(isl)
        for dx in (-0.6,0,0.6):
            for dy in (-0.6,0,0.6):
                z=ground(c+Vector((dx,dy,0)))
                if z is not None: g=max(g,z)
        cl=zb-g; mins.append(cl); res.append((round(c.x,2),round(c.y,2),round(zb,3),round(g,3),round(cl,3)))
        if cl<0: below+=1
        if cl<0.30: lt30+=1
    mins.sort()
    print('CHECK',name,'windows',len(res),'below_grade',below,'clear<0.30',lt30,'min_clear',round(mins[0],3) if mins else None,'p05',round(mins[len(mins)//20],3) if mins else None)
    json.dump(res,open(OUT,'w'))
    sys.exit(0)
faces=[]
for vn,bm in vbm:
    for f in bm.faces:
        if abs(f.normal.z)>0.08 or f.calc_area()<4: continue
        nh=Vector((f.normal.x,f.normal.y,0)).normalized(); u=Vector((-nh.y,nh.x,0))
        P=[v.co.copy() for v in f.verts]; d=sum((p.dot(nh) for p in P))/len(P)
        faces.append(dict(vol=vn,nh=nh,u=u,d=d,P=P))
# group coplanar faces
groups=[]
for F in faces:
    ang=math.degrees(math.atan2(F['nh'].y,F['nh'].x))
    for g in groups:
        da=abs((ang-g['ang']+180)%360-180)
        if da<2.0 and abs(F['d']-g['d'])<0.3: g['F'].append(F); break
    else: groups.append(dict(ang=ang,d=F['d'],nh=F['nh'],u=F['u'],F=[F]))
def ztop_at(P,u,t):
    zs=[]
    n=len(P)
    for i in range(n):
        a,b=P[i],P[(i+1)%n]; ta,tb=a.dot(u),b.dot(u)
        if (ta-t)*(tb-t)<=0 and abs(tb-ta)>1e-6:
            s=(t-ta)/(tb-ta); zs.append(a.z+s*(b.z-a.z))
        elif abs(tb-ta)<=1e-6 and abs(ta-t)<1e-3: zs+= [a.z,b.z]
    return (min(zs),max(zs)) if zs else (None,None)
wins=[]; stats=dict(groups=len(groups),faces=len(faces),cand=0,skip_inside=0,skip_block=0,skip_door=0,skip_grade=0,skip_top=0)
hw=GW/2+FR
for g in groups:
    u=g['u']; nh=g['nh']
    T=[(p.dot(u)) for F in g['F'] for p in F['P']]; tmin,tmax=min(T),max(T); W=tmax-tmin
    if W<2.6: continue
    n=int((W-2.4)/SP)+1; T0=tmin+(W-(n-1)*SP)/2
    for k in range(n):
        t=T0+k*SP
        # face hosting the column (window edges ≥0.25 m inside face)
        host=None
        for F in g['F']:
            ts=[p.dot(u) for p in F['P']]
            if min(ts)+hw+0.25<=t<=max(ts)-hw-0.25: host=F; break
        if host is None: continue
        zl=[ztop_at(host['P'],u,tt) for tt in (t-hw,t,t+hw)]
        if any(z[0] is None for z in zl): continue
        top=min(z[1] for z in zl); bot=max(z[0] for z in zl)
        base=nh*host['d']+u*t   # point on facade plane at z=0
        cxy=Vector((base.x,base.y,0))
        g0=gmax(cxy,u,nh,hw)
        for r in range(-2,8):
            sill=FFE+SILL_ABOVE_FFE+r*F2F; gh=GH
            stats['cand']+=1
            if r==0 and sill+GH+FR>top-0.45 and sill+1.2+FR<=top-0.30: gh=1.2; stats.setdefault('short',0); stats['short']+=1
            head=sill+gh
            if sill-0.16<bot+0.05 or head+FR>top-(0.30 if gh<GH else 0.45): stats['skip_top']+=1; continue
            if g0 is None or sill-0.16<g0+CLEAR: stats['skip_grade']+=1; continue
            c=cxy+Vector((0,0,sill+gh/2))
            pts=[c+u*a+Vector((0,0,b)) for a in (-hw,hw) for b in (-gh/2-FR,gh/2+FR)]+[c]
            if any(in_door(p) for p in pts): stats['skip_door']+=1; continue
            if any(inside(p+nh*0.12) for p in pts): stats['skip_inside']+=1; continue
            if blocked(c,nh): stats['skip_block']+=1; continue
            wins.append(dict(c=[c.x,c.y,c.z],nh=[nh.x,nh.y],sill=sill,gh=gh,g=g0,clear=sill-0.16-g0,row=r,grp=groups.index(g),vol=host['vol']))
print('L stats',stats,'windows',len(wins))
from collections import Counter
print('L rows',sorted(Counter(w['row'] for w in wins).items()))
print('L minclear',round(min(w['clear'] for w in wins),3))
json.dump(dict(FFE=FFE,F2F=F2F,GW=GW,GH=GH,FR=FR,wins=wins,stats=stats),open(OUT,'w'))
