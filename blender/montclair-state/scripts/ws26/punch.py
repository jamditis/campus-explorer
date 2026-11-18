"""ws26: Partridge Hall large glazed curtain bays -> stucco infill with single punched windows
(white frames, transom, sill) per Joe's Nov 8 photo (his photos override older data). Saves main."""
import bpy, bmesh, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
CN='WS26_Partridge_punched_windows_JoePhoto_20261110ws26'
sc=bpy.context.scene
col=bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
if col.name not in sc.collection.children: sc.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o)
fr=[o for o in bpy.data.objects if o.name.startswith('TX Partridge precast frame')][0]
core=[o for o in bpy.data.objects if o.name.startswith('TX Partridge core')][0]
ent=[o for o in bpy.data.objects if o.name.startswith('TX Partridge entrances')][0]
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); mats=[f.material_index for f in bm.faces]
    t=BVHTree.FromBMesh(bm); bm.free(); return t,mats
FT,FM=bvh(fr); ET,_=bvh(ent)
MULL=[i for i,s in enumerate(fr.material_slots) if s.material and 'window_frame_white' in s.material.name]
print('MULL slots',MULL)
ST=bpy.data.materials['WS25_Partridge_stucco_cream_JoePhoto']
WF=bpy.data.materials['WS25_Partridge_window_frame_white_JoePhoto']
GL=bpy.data.materials.get('WS26_Partridge_window_glass') or bpy.data.materials.new('WS26_Partridge_window_glass')
GL.use_nodes=True; b=GL.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.03,0.04,0.05,1); b.inputs['Roughness'].default_value=0.06; b.inputs['Metallic'].default_value=0.3
WWIN,HWIN=1.15,1.55   # photo-estimated, UNVERIFIED
STEP=0.1
bmP=bmesh.new(); bmF=bmesh.new(); bmG=bmesh.new()
def quad(bm,pts):
    vs=[bm.verts.new(p) for p in pts]; return bm.faces.new(vs)
def box(bm,c,t,n,w,h,d):
    # axis box centred c, along t (w), up z (h), out n (d)
    u=Vector((0,0,1)); P=[]
    for dx in(-w/2,w/2):
        for dz in(-h/2,h/2):
            for dn in(0,d): P.append(c+t*dx+u*dz+n*dn)
    vs=[bm.verts.new(p) for p in P]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f])
        except ValueError: pass
boxes=[]; dead=set(); nopen=0; nwin=0; skipped=0
for p in core.data.polygons:
    if abs(p.normal.z)>0.1: continue
    vs=[core.matrix_world@core.data.vertices[k].co for k in p.vertices]
    n=(core.matrix_world.to_3x3()@p.normal); n.z=0; n.normalize()
    zs=[v.z for v in vs]; a=[v for v in vs if abs(v.z-min(zs))<0.01]
    if len(a)<2: continue
    A,B=a[0],a[1]; t=B-A; t.z=0; W=t.length; t.normalize()
    if W<2.5: continue
    cols=int(W/STEP); rows=int((155.4-139.0)/STEP)
    grid=[[0]*cols for _ in range(rows)]
    for r in range(rows):
        z=139.0+r*STEP+STEP/2
        for c in range(cols):
            o=A+t*(c*STEP+STEP/2); o.z=z
            h=FT.ray_cast(o+n*2.0,-n,2.6)
            grid[r][c]= 1 if (h[0] is None or FM[h[2]] in MULL) else 0
    seen=set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]!=1 or (r,c) in seen: continue
            st=[(r,c)]; cells=[]
            while st:
                x=st.pop()
                if x in seen: continue
                rr,cc=x
                if not(0<=rr<rows and 0<=cc<cols) or grid[rr][cc]!=1: continue
                seen.add(x); cells.append(x); st+=[(rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1)]
            r0=min(x[0] for x in cells); r1=max(x[0] for x in cells)+1; c0=min(x[1] for x in cells); c1=max(x[1] for x in cells)+1
            ow=(c1-c0)*STEP; oh=(r1-r0)*STEP
            if ow<2.5 or oh<1.6: continue
            s0,s1=c0*STEP,c1*STEP; z0,z1=139.0+r0*STEP,139.0+r1*STEP
            # skip openings containing entrance geometry
            hit_e=False
            for k in range(12):
                o=A+t*(s0+(s1-s0)*(k+0.5)/12); o.z=z0+0.8
                if ET.ray_cast(o+n*2.0,-n,2.6)[0] is not None: hit_e=True; break
            if hit_e: skipped+=1; continue
            nopen+=1; boxes.append((A.copy(),t.copy(),n.copy(),s0,s1,z0,z1))
            # frame face depth at the pier just outside the opening (for reveal)
            D=0.07  # infill plane offset from core glass
            base=A+n*D
            # mullion faces in this opening -> hide (delete later)
            for fi,fp in enumerate(fr.data.polygons):
                if fp.material_index not in MULL: continue
                cw=fr.matrix_world@fp.center; rel=cw-A
                s=rel.dot(t); dn=rel.dot(n)
                if s0-0.05<s<s1+0.05 and z0-0.05<cw.z<z1+0.05 and -0.3<dn<1.2: dead.add(fi)
            # windows
            nw=max(1,round(ow/2.6)); pitch=ow/nw
            wz0=z0+max(0.35,(oh-HWIN)*0.45); wz1=wz0+HWIN
            xs=[s0+pitch*(k+0.5) for k in range(nw)]
            # panel: horizontal strips + vertical pieces between windows (overlap 6 cm into frame)
            ov=0.06; S0,S1,Z0,Z1=s0-ov,s1+ov,z0-ov,z1+ov
            def P(s,z): q=base+t*s; return Vector((q.x,q.y,z))
            quad(bmP,[P(S0,Z0),P(S1,Z0),P(S1,wz0),P(S0,wz0)])
            quad(bmP,[P(S0,wz1),P(S1,wz1),P(S1,Z1),P(S0,Z1)])
            edges=[S0]+[e for x in xs for e in (x-WWIN/2,x+WWIN/2)]+[S1]
            for k in range(0,len(edges),2):
                quad(bmP,[P(edges[k],wz0),P(edges[k+1],wz0),P(edges[k+1],wz1),P(edges[k],wz1)])
            for x in xs:
                nwin+=1
                c=base+t*x; 
                fw=0.075; fd=0.06
                # glass recessed 4 cm behind panel
                g=base-n*0.04+t*x
                quad(bmG,[P(x-WWIN/2,wz0)-n*0.04,P(x+WWIN/2,wz0)-n*0.04,P(x+WWIN/2,wz1)-n*0.04,P(x-WWIN/2,wz1)-n*0.04])
                # reveal (stucco) sides
                for (sa,za,sb,zb) in [(x-WWIN/2,wz0,x+WWIN/2,wz0),(x+WWIN/2,wz1,x-WWIN/2,wz1),(x-WWIN/2,wz1,x-WWIN/2,wz0),(x+WWIN/2,wz0,x+WWIN/2,wz1)]:
                    quad(bmP,[P(sa,za)-n*0.045,P(sb,zb)-n*0.045,P(sb,zb),P(sa,za)])
                cc=lambda s,z: P(s,z)-n*0.04
                cz=(wz0+wz1)/2
                box(bmF,cc(x,wz0+fw/2),t,n,WWIN,fw,fd)
                box(bmF,cc(x,wz1-fw/2),t,n,WWIN,fw,fd)
                box(bmF,cc(x-WWIN/2+fw/2,cz),t,n,fw,HWIN,fd)
                box(bmF,cc(x+WWIN/2-fw/2,cz),t,n,fw,HWIN,fd)
                box(bmF,cc(x,wz0+HWIN*0.62),t,n,WWIN,0.05,fd*0.8)   # transom
                box(bmF,P(x,wz0-0.04),t,n,WWIN+0.12,0.06,0.07)       # sill
def mk(bm,name,m):
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0005)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
op=mk(bmP,'WS26_Partridge_infill_stucco_JoePhoto',ST)
for pp in op.data.polygons: pp.use_smooth=False
mk(bmF,'WS26_Partridge_window_frames_white_UNVERIFIED_size',WF)
mk(bmG,'WS26_Partridge_window_glass',GL)
# delete mullion faces inside converted bays
bm=bmesh.new(); bm.from_mesh(fr.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in dead],context='FACES'); bm.to_mesh(fr.data); bm.free()
stk=[o for o in bpy.data.objects if o.name.startswith('TY Partridge E/W spandrel weathering')][0]
sd=[]
for fi,fp in enumerate(stk.data.polygons):
    pts=[stk.matrix_world@stk.data.vertices[k].co for k in fp.vertices]
    hit=False
    for (A,t,n,s0,s1,z0,z1) in boxes:
        for cw in pts:
            rel=cw-A; s=rel.dot(t); dn=rel.dot(n)
            if s0-0.02<s<s1+0.02 and z0-0.02<cw.z<z1+0.02 and -0.3<dn<1.5: hit=True; break
        if hit: sd.append(fi); break
bm=bmesh.new(); bm.from_mesh(stk.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in sd],context='FACES'); bm.to_mesh(stk.data); bm.free()
print('STREAK_FACES_DEL',len(sd))
print('OPENINGS',nopen,'WINDOWS',nwin,'SKIPPED_ENTR',skipped,'MULL_FACES_DEL',len(dead))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
