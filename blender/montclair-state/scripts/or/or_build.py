# or (Oct 31 2026): (A) re-site the oq lower-storey skirt windows onto the upper-storey window columns (wall shader grid:
# centre at facade-U = win_u0 + win_pitch*(k+0.5), win_w wide) on CCIS/CELS/Speech/Calcia, same oq frame style, width = win_w;
# overhead check relaxed so windows can sit under a canopy that clears the head (Calcia west).  Replaces collection
# OQ_context_skirt_lower_windows_20261031oq by OR_context_skirt_windows_aligned_20261031or.
# (B) grey cast base course + grade-line dirt band at the bottom of all OO stucco skirts (incl. Memorial).
# ALL UNVERIFIED. OSM/LiDAR/oo meshes NOT edited. REVERT=1 removes or's objects and re-runs scripts/oq/oq_build.py (restores oq exactly).
import bpy, bmesh, os, sys, math, collections
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
ROOT='/workspace/nj-scenes/montclair-state'
CN='OR_context_skirt_windows_aligned_20261031or'; CB='OR_skirt_base_course_20261031or'; OQN='OQ_context_skirt_lower_windows_20261031oq'
BMAT='OR_skirt_base_course_grey_dirt_UNVERIFIED'
def kill_col(n):
    c=bpy.data.collections.get(n)
    if not c: return
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
kill_col(CN); kill_col(CB)
m=bpy.data.materials.get(BMAT)
if m: bpy.data.materials.remove(m)
if REV:
    if not bpy.data.collections.get(OQN):
        sys.argv=[a for a in sys.argv if a!='--save']; cwd=os.getcwd(); os.makedirs('/tmp/or_rev/data/oq',exist_ok=True); os.chdir('/tmp/or_rev')
        os.environ['REVERT']='0'
        try: exec(open(ROOT+'/scripts/oq/oq_build.py').read(),{'__name__':'oqb'})
        except SystemExit: pass
        os.chdir(cwd); os.environ['REVERT']='1'; print('OQ_REBUILT')
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
kill_col(OQN)
FR=bpy.data.materials['Window_frame_brown']; GL=bpy.data.materials['Dark_glass']; SL=bpy.data.materials['OK_Schmitt_cast_stone_sill_UNVERIFIED']
dg=bpy.context.evaluated_depsgraph_get(); scn=bpy.context.scene; Z=Vector((0,0,1))
H=1.9; SW,SD=0.14,0.13
def box(bm,o,u,n,z,u0,u1,n0,n1,z0,z1,mi,hv=None):
    vs=[bm.verts.new(o+u*a+n*b+z*c) for a in (u0,u1) for b in (n0,n1) for c in (z0,z1)]
    if hv is not None:
        lay=bm.verts.layers.float.get('or_h')
        for i,v in enumerate(vs): v[lay]=hv[i]
    for q in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        f=bm.faces.new([vs[i] for i in q]); f.material_index=mi
def segs_of(sk):
    out=[]
    for p in sk.data.polygons:
        vs=[sk.matrix_world@sk.data.vertices[i].co for i in p.vertices]; pts={}
        for v in vs: pts.setdefault((round(v.x,2),round(v.y,2)),[]).append(v.z)
        if len(pts)!=2: continue
        (k1,z1),(k2,z2)=pts.items(); out.append([k1,k2,(max(z1),min(z1)+0.3),(max(z2),min(z2)+0.3)])
    return out
def wall_U(wall):
    me=wall.data; fa=me.attributes['facade'].data; d={}
    for p in me.polygons:
        kv={}
        for li in p.loop_indices:
            v=wall.matrix_world@me.vertices[me.loops[li].vertex_index].co; k=(round(v.x,2),round(v.y,2))
            if k not in kv or v.z<kv[k][0]: kv[k]=(v.z,fa[li].vector[0])
        if len(kv)==2: d[frozenset(kv)]={k:x[1] for k,x in kv.items()}
    return d
# ---------- (A) aligned windows
col=bpy.data.collections.new(CN); scn.collection.children.link(col)
B=['Center for Computing and Information Science walls','Center for Environmental and Life Sciences walls','Speech Building walls','Calcia Hall walls']
log=[]; stats={}; nshort=[0]
for name in B:
    sk=bpy.data.objects.get(('OO_skirt_'+name)[:60]); wall=bpy.data.objects[name]
    P=float(wall.get('win_pitch',3.6)); W=min(2.2,float(wall.get('win_w',2.2))); U0=float(wall.get('win_u0',0.0))
    UD=wall_U(wall)
    cen=sum((wall.matrix_world@v.co for v in wall.data.vertices),Vector())/len(wall.data.vertices)
    segs=segs_of(sk)
    adj=collections.defaultdict(list)
    for i,sg in enumerate(segs): adj[sg[0]].append(i); adj[sg[1]].append(i)
    used=set(); runs=[]
    def dirv(sg): d=Vector((sg[1][0]-sg[0][0],sg[1][1]-sg[0][1])); return d.normalized() if d.length>1e-6 else d
    for i in range(len(segs)):
        if i in used: continue
        used.add(i); pts=[(segs[i][0],segs[i][2]),(segs[i][1],segs[i][3])]; d0=dirv(segs[i]); sl=[i]
        for end in (1,0):
            while True:
                k=pts[-1][0] if end==1 else pts[0][0]; nxt=None
                for j in adj[k]:
                    if j in used: continue
                    if abs(abs(dirv(segs[j]).dot(d0))-1)<0.004: nxt=j; break
                if nxt is None: break
                used.add(nxt); sg=segs[nxt]; other=(sg[1],sg[3]) if sg[0]==k else (sg[0],sg[2])
                if end==1: pts.append(other)
                else: pts.insert(0,other)
        runs.append(pts)
    bm=bmesh.new(); n_win=0; n_skip=0
    for pts in runs:
        A=Vector((pts[0][0][0],pts[0][0][1],0)); Bv=Vector((pts[-1][0][0],pts[-1][0][1],0)); L=(Bv-A).length
        if L<W+0.6: continue
        CAL=name.startswith('Calcia')
        if max(q[1][0]-q[1][1] for q in pts)<(1.7 if CAL else 2.6): continue
        u=(Bv-A)/L; ss=[(Vector((q[0][0],q[0][1],0))-A).dot(u) for q in pts]
        def at(s,k):
            for a in range(len(ss)-1):
                if ss[a]<=s<=ss[a+1]:
                    t=(s-ss[a])/max(1e-6,ss[a+1]-ss[a]); return pts[a][1][k]+(pts[a+1][1][k]-pts[a][1][k])*t
            return pts[0][1][k] if s<ss[0] else pts[-1][1][k]
        n=Vector((u.y,-u.x,0)); mid=(A+Bv)/2
        if n.dot(mid-Vector((cen.x,cen.y,0)))<0: n=-n
        # column centres from the facade U of each wall segment above this run
        cs=set()
        for a in range(len(pts)-1):
            ka,kb=pts[a][0],pts[a+1][0]; e=UD.get(frozenset((ka,kb)))
            if not e: continue
            Ua,Ub=e[ka],e[kb]
            if abs(Ub-Ua)<1e-4 or abs(Ub-Ua)>5: continue   # seam wrap
            lo,hi=min(Ua,Ub),max(Ua,Ub)
            k=math.ceil((lo-U0)/P-0.5)
            while U0+P*(k+0.5)<=hi:
                Uc=U0+P*(k+0.5); s=ss[a]+(Uc-Ua)/(Ub-Ua)*(ss[a+1]-ss[a]); cs.add(round(s,3)); k+=1
        for uc in sorted(cs):
            if uc-W/2-0.3<0 or uc+W/2+0.3>L: continue
            gmax=max(at(uc+d,1) for d in (-W/2-0.15,0,W/2+0.15)); tmin=min(at(uc+d,0) for d in (-W/2,0,W/2))
            for r in range(3):
                H=1.9; sill=gmax+0.85+r*3.6
                if sill+H>tmin-0.35:
                    # (C) Calcia: low skirt -> short high-set lower-storey window (areaway/hopper type), UNVERIFIED
                    if not(CAL and r==0): break
                    H=0.95; sill=tmin-0.35-H
                    if sill<gmax+0.35: break
                o=A+u*uc; o=Vector((o.x,o.y,0)); hit=False
                for du,dz in ((0,H/2),(-W/2-0.2,-0.15),(W/2+0.2,-0.15),(-W/2-0.2,H*0.7),(W/2+0.2,H*0.7)):
                    if scn.ray_cast(dg,o+u*du+n*0.2+Z*(sill+dz),n,distance=2.5)[0]: hit=True; break
                    if scn.ray_cast(dg,o+u*du+n*1.0+Z*(sill+dz),-n,distance=0.7)[0]: hit=True; break
                for du in (-W/2-0.15,0,W/2+0.15):   # overhead: only a slab lower than the window head + 0.3 m blocks
                    if hit: break
                    if scn.ray_cast(dg,o+u*du+n*0.35+Z*(sill+0.2),Z,distance=H+0.3-0.2+0.15)[0]: hit=True
                if hit: n_skip+=1; continue
                if H<1.0: nshort[0]+=1
                h2=W/2; fw=0.07
                f=bm.faces.new([bm.verts.new(o+u*a+n*0.035+Z*c) for a,c in ((-h2,sill),(h2,sill),(h2,sill+H),(-h2,sill+H))]); f.material_index=1
                box(bm,o,u,n,Z,-h2,h2,-0.02,0.075,sill,sill+fw,0); box(bm,o,u,n,Z,-h2,h2,-0.02,0.075,sill+H-fw,sill+H,0)
                box(bm,o,u,n,Z,-h2,-h2+fw,-0.02,0.075,sill+fw,sill+H-fw,0); box(bm,o,u,n,Z,h2-fw,h2,-0.02,0.075,sill+fw,sill+H-fw,0)
                box(bm,o,u,n,Z,-0.05,0.05,-0.02,0.075,sill+fw,sill+H-fw,0)   # centre mullion (upper windows have mull_w 0.1)
                for fu in (-1/4,1/4): box(bm,o,u,n,Z,W*fu-0.018,W*fu+0.018,0.0,0.06,sill+fw,sill+H-fw,0)
                for fz in ((1/3,2/3) if H>1.2 else (0.5,)): box(bm,o,u,n,Z,-h2+fw,h2-fw,0.0,0.06,sill+H*fz-0.018,sill+H*fz+0.018,0)
                box(bm,o,u,n,Z,-h2-SW,h2+SW,-0.03,SD,sill+H,sill+H+SW,3); box(bm,o,u,n,Z,-h2-SW,-h2,-0.03,SD,sill,sill+H,3); box(bm,o,u,n,Z,h2,h2+SW,-0.03,SD,sill,sill+H,3)
                box(bm,o,u,n,Z,-h2-SW-0.04,h2+SW+0.04,-0.03,SD+0.05,sill-0.08,sill+0.005,2)
                n_win+=1; log.append((name[:12],round(H,2),round(o.x,2),round(o.y,2),round(sill,2),round(n.x,3),round(n.y,3)))
    stats[name[:12]]=(n_win,n_skip)
    if n_win==0: print('NOWIN',name); bm.free(); continue
    me=bpy.data.meshes.new('OR_skirt_win_'+name[:30]); bm.to_mesh(me)
    for mm in (FR,GL,SL,sk.material_slots[0].material): me.materials.append(mm)
    ob=bpy.data.objects.new(('OR_skirt_win_'+name)[:60],me); col.objects.link(ob)
    ob['UNVERIFIED']='or: lower-storey windows on the oo skirt, centred on the upper-storey shader window columns; existence/size/style guessed'
    print('WIN',name,n_win,'skipped',n_skip)
os.makedirs(ROOT+'/data/or',exist_ok=True); open(ROOT+'/data/or/skirt_windows_aligned.txt','w').write('\n'.join(str(x) for x in log))
# ---------- (B) base course + grade dirt
bmat=bpy.data.materials.new(BMAT); bmat.use_nodes=True; nt=bmat.node_tree; bs=nt.nodes['Principled BSDF']
at_=nt.nodes.new('ShaderNodeAttribute'); at_.attribute_name='or_h'
cr=nt.nodes.new('ShaderNodeValToRGB'); e=cr.color_ramp; e.elements[0].position=0.0; e.elements[0].color=(0.13,0.115,0.095,1); e.elements[1].position=0.62; e.elements[1].color=(0.33,0.325,0.31,1); e.elements.new(0.38).color=(0.17,0.155,0.13,1)
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=9.0
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=0.25
nt.links.new(at_.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],mx.inputs[6]); nt.links.new(nz.outputs['Color'],mx.inputs[7]); nt.links.new(mx.outputs[2],bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value=0.88
colb=bpy.data.collections.new(CB); scn.collection.children.link(colb); nb=0
GB,GT,PR=-0.22,0.42,0.035   # below/above local grade, projection
for sk in [o for o in bpy.data.objects if o.name.startswith('OO_skirt_') and o.type=='MESH']:
    wn=sk.name[9:]; wall=bpy.data.objects.get(wn)
    cobj=wall or sk; cen=sum((cobj.matrix_world@v.co for v in cobj.data.vertices),Vector())/len(cobj.data.vertices)
    bm=bmesh.new(); bm.verts.layers.float.new('or_h'); k=0
    for sg in segs_of(sk):
        A=Vector((sg[0][0],sg[0][1],0)); Bv=Vector((sg[1][0],sg[1][1],0)); L=(Bv-A).length
        if L<0.05: continue
        u=(Bv-A)/L; n=Vector((u.y,-u.x,0))
        if n.dot((A+Bv)/2-Vector((cen.x,cen.y,0)))<0: n=-n
        ga,gb=sg[2][1],sg[3][1]; g=max(ga,gb); gl=min(ga,gb)
        # doorway / steps check: something right in front at knee height -> skip
        o=A+u*(L/2)
        if scn.ray_cast(dg,o+n*0.08+Z*(g+0.25),n,distance=0.25)[0]: continue
        ex=0.04
        vs=[bm.verts.new(A+u*a+n*b+Z*((ga if a<=0 else gb)+c)) for a in (-ex,L+ex) for b in (-0.03,PR) for c in (GB,GT)]
        lay=bm.verts.layers.float['or_h']
        for j,v in enumerate(vs): v[lay]=float(j%2)
        for q in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]: bm.faces.new([vs[j] for j in q])
        k+=1
    if k:
        me=bpy.data.meshes.new('OR_base_'+wn[:40]); bm.to_mesh(me); me.materials.append(bmat)
        ob=bpy.data.objects.new(('OR_base_course_'+wn)[:60],me); colb.objects.link(ob); ob['UNVERIFIED']='or: grey base course + grade dirt band under the oo skirt; no photo'
        nb+=1; print('BASE',wn,k)
    else: bm.free()
print('STATS',stats,'short',nshort[0],'BASEOBJ',nb)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
