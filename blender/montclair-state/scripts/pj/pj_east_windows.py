# pj (Nov 1 2026): Feliciano east-facing walls: replace the flat shader windows (Wall_stucco_mission grid: U centre = win_u0 + 3.6(k+.5),
# 2.2 m wide; rows V = 0.9 + 4.4 r, 2.45 m high, V = z - zref of the facade UV) with real window units in the style of the ported
# photo windows (white stucco surround 10 cm proud = reveal, maroon frame + centre mullion + transom, dark glass 8 cm behind the
# surround face, tan cast sill). The east-facing shader faces then use the pg plain-stucco slot. ALL UNVERIFIED (no east photo).
# REVERT=1 deletes the object and restores the face material indices from prop pj_prev_mi.
import bpy,bmesh,os,sys,math,json,collections
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; D=os.environ.get('PJDIR','E')   # E (default, original pj), N, W
SUF={'E':'','N':'_N','W':'_W'}[D]; DW={'E':'east','N':'north','W':'west'}[D]
ON='PJ_Feliciano_%s_windows_UNVERIFIED'%DW; PK='pj_prev_mi'+SUF; UK='UNVERIFIED_pj'+SUF
w=bpy.data.objects['Feliciano School of Business walls']; me=w.data; mw=w.matrix_world; R=mw.to_3x3()
DN='PJ_Feliciano_%s_sill_drips_UNVERIFIED'%DW
for nm in ((DN,'PJ_CAM_closeup_feliciano_east_windows') if D=='E' else (DN,)):
    if nm in bpy.data.objects:
        o=bpy.data.objects[nm]; d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: (bpy.data.meshes if hasattr(d,'polygons') else bpy.data.cameras).remove(d)
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m)
if PK in w.keys():
    for i,mi in json.loads(w[PK]): me.polygons[i].material_index=mi
    del w[PK]
    if UK in w.keys(): del w[UK]
MDN='PJ_sill_drip_grime_light_UNVERIFIED'
if REV:
    mm=bpy.data.materials.get(MDN)
    if mm and mm.users==0: bpy.data.materials.remove(mm)
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
    print('PJ_REVERTED',len(bpy.data.objects)); raise SystemExit(0)
P=float(w['win_pitch']); W=float(w['win_w']); FH=float(w['floor_h']); WH=float(w['win_h']); WB=float(w['win_bottom']); WT=float(w['win_top']); U0=float(w.get('win_u0',0.0))
fa=me.attributes['facade'].data; s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); Z=Vector((0,0,1))
ws=[mw@v.co for v in me.vertices]; C=Vector(((min(v.x for v in ws)+max(v.x for v in ws))/2,(min(v.y for v in ws)+max(v.y for v in ws))/2,0))
faces=[]
for p in me.polygons:
    if p.material_index!=0 or len(p.vertices)!=4: continue
    n=(R@p.normal).normalized(); pc=mw@p.center
    if abs(n.z)>0.2: continue
    if Vector((n.x,n.y,0)).dot(Vector((pc.x-C.x,pc.y-C.y,0)))<0: n=-n
    if (D=='E' and n.x<0.5) or (D=='N' and n.y<0.5) or (D=='W' and n.x>-0.5): continue
    cs=[(mw@me.vertices[me.loops[li].vertex_index].co, fa[li].vector[0], fa[li].vector[1]) for li in p.loop_indices]
    cs.sort(key=lambda c:c[1]); a=sorted(cs[:2],key=lambda c:c[0].z); b=sorted(cs[2:],key=lambda c:c[0].z)
    Ua,Ub=a[0][1],b[0][1]; L=(Vector((b[0][0].x,b[0][0].y,0))-Vector((a[0][0].x,a[0][0].y,0))).length
    if L<0.05 or abs((Ub-Ua)-L)>0.15: print('SKIPFACE',p.index,round(Ua,2),round(Ub,2),round(L,2)); continue
    zref=sum(c[0].z-c[2] for c in cs)/4
    faces.append(dict(i=p.index,n=Vector((n.x,n.y,0)).normalized(),Ua=Ua,Ub=Ub,A=a,B=b,zref=zref))
def locate(U):
    for f in faces:
        if f['Ua']-1e-4<=U<=f['Ub']+1e-4:
            t=(U-f['Ua'])/(f['Ub']-f['Ua']); A=f['A'];B=f['B']
            base=A[0][0].lerp(B[0][0],t); top=A[1][0].lerp(B[1][0],t)
            return f,Vector((base.x,base.y,0)),base.z,top.z
    return None
sills=[]; bm=bmesh.new(); used=set(); n_win=0; skipped=collections.Counter(); log=[]
def box(o,u,n,u0,u1,n0,n1,z0,z1,mi):
    vs=[bm.verts.new(o+u*a+n*b+Z*c) for a in (u0,u1) for b in (n0,n1) for c in (z0,z1)]
    for q in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        f=bm.faces.new([vs[i] for i in q]); f.material_index=mi
# level floors: one zref per contiguous U run (median), not the shader's per-face stepped rows
fs=sorted(faces,key=lambda f:f['Ua']); runs=[[fs[0]]]
for f in fs[1:]:
    (runs[-1].append(f) if abs(f['Ua']-runs[-1][-1]['Ub'])<0.05 else runs.append([f]))
for rn in runs:
    zs=sorted(f['zref'] for f in rn); zm=zs[len(zs)//2]
    for f in rn: f['zref']=zm
print('PJ runs',[(round(rn[0]['Ua'],1),round(rn[-1]['Ub'],1),round(rn[0]['zref'],2)) for rn in runs])
Umin=min(f['Ua'] for f in faces); Umax=max(f['Ub'] for f in faces)
k=math.floor((Umin-U0)/P)
SW=0.12; fw=0.07
while U0+P*(k+0.5)<=Umax+P:
    Uc=U0+P*(k+0.5); k+=1
    ends=[locate(Uc-W/2-SW),locate(Uc+W/2+SW),locate(Uc)]
    if None in ends: skipped['span']+=1; continue
    f,o,zb,zt=ends[2]
    if abs(ends[0][0]['n'].dot(ends[1][0]['n']))<0.97: skipped['corner']+=1; continue
    n=f['n']; u=Vector((-n.y,n.x,0))
    pa=ends[0][1]; pb=ends[1][1]
    if (pb-pa).dot(u)<0: u=-u
    ztop=min(e[3] for e in ends); zbot=max(e[2] for e in ends); zref=f['zref']
    r=0
    while True:
        V0=WB+FH*r; r+=1
        if V0+WH>WT+1e-3: break
        z0=zref+V0; z1=z0+WH
        if z1+0.35>ztop: break
        hit=s.ray_cast(dg,o+Z*(z0-0.6)+n*0.6,-Z,distance=6)
        g=hit[1].z if hit[0] else zbot
        if z0<g+0.45 or z0<zbot+0.3: skipped['low']+=1; continue
        bad=False
        for du in (-W/2+0.15,0,W/2-0.15):
            for dz in (0.15,WH/2,WH-0.15):
                h=s.ray_cast(dg,o+u*du+Z*(z0+dz)+n*1.5,-n,distance=1.7)
                if h[0] and h[4].name!=w.name and h[4].name!=ON: bad=True
                if not h[0]: bad=True
        if bad: skipped['occluded']+=1; continue
        h2=W/2
        box(o,u,n,-h2-SW,h2+SW,-0.02,0.10,z1,z1+SW,0); box(o,u,n,-h2-SW,-h2,-0.02,0.10,z0,z1,0); box(o,u,n,h2,h2+SW,-0.02,0.10,z0,z1,0)
        box(o,u,n,-h2-SW-0.05,h2+SW+0.05,-0.03,0.16,z0-0.09,z0+0.01,3)
        gq=bm.faces.new([bm.verts.new(o+u*a+n*0.02+Z*c) for a,c in ((-h2,z0),(h2,z0),(h2,z1),(-h2,z1))]); gq.material_index=2
        box(o,u,n,-h2,h2,-0.01,0.05,z0+0.01,z0+fw,1); box(o,u,n,-h2,h2,-0.01,0.05,z1-fw,z1,1)
        box(o,u,n,-h2,-h2+fw,-0.01,0.05,z0,z1,1); box(o,u,n,h2-fw,h2,-0.01,0.05,z0,z1,1)
        box(o,u,n,-0.045,0.045,-0.01,0.055,z0+fw,z1-fw,1)
        zt_=z0+WH*0.70; box(o,u,n,-h2+fw,h2-fw,-0.01,0.05,zt_-0.035,zt_+0.035,1)
        for fu in (-0.5,0.5):
            box(o,u,n,W/4*fu*2-0.014,W/4*fu*2+0.014,0.0,0.045,zt_+0.035,z1-fw,1)
        sills.append((o.copy(),u.copy(),n.copy(),z0)); n_win+=1; log.append((round(Uc,2),r-1,round(z0,2)))
        for e in ends: used.add(e[0]['i'])
# every east shader face goes plain (windows on faces where none fit are dropped, logged)
prev=[]
for f in faces:
    prev.append([f['i'],me.polygons[f['i']].material_index]); me.polygons[f['i']].material_index=1
w[PK]=json.dumps(prev); w[UK]=DW+'-facing shader windows replaced by PJ window units (no east photo)'
m=bpy.data.meshes.new(ON); bm.to_mesh(m); bm.free()
for mn in ('North_Feliciano_stucco_white','North_Feliciano_frame_maroon','North_Feliciano_glass_dark','North_Feliciano_sill_tan'): m.materials.append(bpy.data.materials[mn])
ob=bpy.data.objects.new(ON,m); w.users_collection[0].objects.link(ob)
ob['UNVERIFIED']='east windows: grid from the wall shader, style from the south photo windows; no east photo'
# subtle drip/grime streaks under each sill (reuses the OM sill-drip decal material; shadows off)
bd=bmesh.new(); uvs=[]
for k,(o,u,n,z0) in enumerate(sills):
    half=(W/2+0.12)*0.95; base=o+n*0.004+Z*(z0-0.09); dh=0.30+0.22*((k*37)%11)/10
    pts=[base-u*half,base+u*half,base+u*half*0.88-Z*dh,base-u*half*0.88-Z*dh]
    bd.faces.new([bd.verts.new(q) for q in pts]); uvs.append(((0,1),(1,1),(1,0),(0,0)))
md=bpy.data.meshes.new(DN); bd.to_mesh(md); bd.free(); ul=md.uv_layers.new(name='UVMap')
for pi_,poly in enumerate(md.polygons):
    for j,li in enumerate(poly.loop_indices): ul.data[li].uv=uvs[pi_][j]
mm=bpy.data.materials.get(MDN)
if not mm:
    mm=bpy.data.materials['OM_Schmitt_sill_drip_grime_UNVERIFIED'].copy(); mm.name=MDN
    pass   # alpha 1.2 -> 0.5: lighter than the Schmitt drips
mm.node_tree.nodes['Math.002'].inputs[1].default_value=0.5   # alpha scale 1.2 -> 0.5 (lighter than Schmitt)
md.materials.append(mm)
od=bpy.data.objects.new(DN,md); w.users_collection[0].objects.link(od); od.visible_shadow=False
od['UNVERIFIED']='typical sill drip grime under the PJ east windows, no photo'
print('PJ drips',len(md.polygons))
print('PJ faces',len(faces),'wins',n_win,'skipped',dict(skipped),'polys',len(m.polygons))
print('PJ log',log[:60])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PJ_DONE',len(bpy.data.objects))
