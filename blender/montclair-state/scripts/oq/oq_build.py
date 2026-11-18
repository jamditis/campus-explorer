# oq (Oct 31 2026): (A) lower-storey punched windows on the oo stucco skirts (CCIS/CELS/Speech/Calcia; Memorial skirt <2.6 m -> none),
# 2x2-lite dark glass in a frame + cast sill, ~3 m bays, rows only where the exposed skirt fits a full window above the local DTM.
# Era/style matched to the upper-storey windows (dark glass, light frame). ALL UNVERIFIED (no photo of these lower storeys).
# (B) east-edge walk tone: Footpaths_OSM slot 0 gets an object-level copy of Paving_concrete darkened x>=96 (world) -> ×0.78.
# OSM/LiDAR/oo meshes NOT edited. REVERT=1 removes all of it.
import bpy, bmesh, os, sys, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OQ_context_skirt_lower_windows_20261031oq'; MATN='OQ_Paving_concrete_east_tone_UNVERIFIED'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
fp=bpy.data.objects['Footpaths_OSM']
if fp.material_slots[0].link=='OBJECT':
    fp.material_slots[0].material=None; fp.material_slots[0].link='DATA'
m=bpy.data.materials.get(MATN)
if m: bpy.data.materials.remove(m)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# ---------- (A) windows
FR=bpy.data.materials['Window_frame_brown'] if os.environ.get('FRAME','brown')=='brown' else None
GL=bpy.data.materials['Dark_glass']; SL=bpy.data.materials['OK_Schmitt_cast_stone_sill_UNVERIFIED']
if FR is None:
    FR=bpy.data.materials.get('OQ_skirt_window_frame_light_UNVERIFIED') or bpy.data.materials.new('OQ_skirt_window_frame_light_UNVERIFIED')
    FR.use_nodes=True; p=FR.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.62,0.61,0.58,1); p.inputs['Roughness'].default_value=0.45
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
dg=bpy.context.evaluated_depsgraph_get(); scn=bpy.context.scene
W,H,BAY=1.45,1.9,3.1; SW,SD=0.14,0.13  # stucco surround width/depth -> ~10 cm reveal
B=['Center for Computing and Information Science walls','Center for Environmental and Life Sciences walls','Speech Building walls','Calcia Hall walls']
def box(bm,o,u,n,z,u0,u1,n0,n1,z0,z1,mi):
    vs=[bm.verts.new(o+u*a+n*b+z*c) for a in (u0,u1) for b in (n0,n1) for c in (z0,z1)]
    idx=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    for q in idx:
        f=bm.faces.new([vs[i] for i in q]); f.material_index=mi
log=[]
for name in B:
    sk=bpy.data.objects.get(('OO_skirt_'+name)[:60]); wall=bpy.data.objects[name]
    if not sk: print('NOSKIRT',name); continue
    cen=sum((wall.matrix_world@v.co for v in wall.data.vertices),Vector())/len(wall.data.vertices)
    bm=bmesh.new(); n_win=0; Z=Vector((0,0,1))
    segs=[]
    for p in sk.data.polygons:
        vs=[sk.matrix_world@sk.data.vertices[i].co for i in p.vertices]
        pts={}
        for v in vs: pts.setdefault((round(v.x,2),round(v.y,2)),[]).append(v.z)
        if len(pts)!=2: continue
        (k1,z1),(k2,z2)=pts.items()
        segs.append([k1,k2,(max(z1),min(z1)+0.3),(max(z2),min(z2)+0.3)])
    # chain collinear segments sharing endpoints into runs
    import collections
    adj=collections.defaultdict(list)
    for i,sg in enumerate(segs): adj[sg[0]].append(i); adj[sg[1]].append(i)
    used=set(); runs=[]
    def dirv(sg): d=Vector((sg[1][0]-sg[0][0],sg[1][1]-sg[0][1])); return d.normalized() if d.length>1e-6 else d
    for i in range(len(segs)):
        if i in used: continue
        used.add(i); pts=[(segs[i][0],segs[i][2]),(segs[i][1],segs[i][3])]; d0=dirv(segs[i])
        for end in (1,0):
            while True:
                k=pts[-1][0] if end==1 else pts[0][0]; nxt=None
                for j in adj[k]:
                    if j in used: continue
                    sg=segs[j]; dj=dirv(sg)
                    if abs(abs(dj.dot(d0))-1)<0.004: nxt=j; break
                if nxt is None: break
                used.add(nxt); sg=segs[nxt]
                other=(sg[1],sg[3]) if sg[0]==k else (sg[0],sg[2])
                if end==1: pts.append(other)
                else: pts.insert(0,other)
        runs.append(pts)
    for pts in runs:
        A=Vector((pts[0][0][0],pts[0][0][1],0)); Bv=Vector((pts[-1][0][0],pts[-1][0][1],0))
        L=(Bv-A).length
        if L<2.4: continue
        u=(Bv-A)/L
        ss=[(Vector((q[0][0],q[0][1],0))-A).dot(u) for q in pts]
        def at(s,k):
            for a in range(len(ss)-1):
                if ss[a]<=s<=ss[a+1]:
                    t=(s-ss[a])/max(1e-6,ss[a+1]-ss[a]); return pts[a][1][k]+(pts[a+1][1][k]-pts[a][1][k])*t
            return pts[0][1][k] if s<ss[0] else pts[-1][1][k]
        if max(q[1][0]-q[1][1] for q in pts)<2.6: continue
        n=Vector((u.y,-u.x,0)); mid=(A+Bv)/2
        if n.dot(mid-Vector((cen.x,cen.y,0)))<0: n=-n
        nb=max(1,int((L-1.0)//BAY)); st=(L-(nb-1)*BAY)/2
        for i in range(nb):
            uc=st+i*BAY
            gmax=max(at(uc+d,1) for d in (-W/2-0.15,0,W/2+0.15)); tmin=min(at(uc+d,0) for d in (-W/2,0,W/2))
            for r in range(3):
                sill=gmax+0.85+r*3.6
                if sill+H>tmin-0.35: break
                o=A+u*uc; o=Vector((o.x,o.y,0))
                # clearance: nothing within 2.5 m in front of the window centre
                src=o+n*0.12+Z*(sill+H/2)
                hit=False
                for du,dz in ((0,H/2),(-W/2-0.2,-0.15),(W/2+0.2,-0.15),(-W/2-0.2,H+0.3),(W/2+0.2,H+0.3),(0,H+0.3)):
                    if scn.ray_cast(dg,o+u*du+n*0.2+Z*(sill+dz),n,distance=2.5)[0]: hit=True; break
                    if scn.ray_cast(dg,o+u*du+n*1.0+Z*(sill+dz),-n,distance=0.7)[0]: hit=True; break   # something already standing just in front
                for du in (-W/2-0.15,0,W/2+0.15):   # overhead canopy/slab just in front of the opening (Calcia west canopy)
                    if hit: break
                    if scn.ray_cast(dg,o+u*du+n*0.35+Z*(sill+0.2),Z,distance=H+0.6)[0]: hit=True
                if hit: continue
                h2=W/2
                f=bm.faces.new([bm.verts.new(o+u*a+n*0.035+Z*c) for a,c in ((-h2,sill),(h2,sill),(h2,sill+H),(-h2,sill+H))]); f.material_index=1
                fw=0.07
                box(bm,o,u,n,Z,-h2,h2,-0.02,0.075,sill,sill+fw,0); box(bm,o,u,n,Z,-h2,h2,-0.02,0.075,sill+H-fw,sill+H,0)
                box(bm,o,u,n,Z,-h2,-h2+fw,-0.02,0.075,sill+fw,sill+H-fw,0); box(bm,o,u,n,Z,h2-fw,h2,-0.02,0.075,sill+fw,sill+H-fw,0)
                for fu in (-1/6,1/6): box(bm,o,u,n,Z,W*fu-0.018,W*fu+0.018,0.0,0.06,sill+fw,sill+H-fw,0)   # 3x3 lites like the upper storeys
                for fz in (1/3,2/3): box(bm,o,u,n,Z,-h2+fw,h2-fw,0.0,0.06,sill+H*fz-0.018,sill+H*fz+0.018,0)
                # stucco surround (reveal) in the wall material, slightly wider than the frame
                box(bm,o,u,n,Z,-h2-SW,h2+SW,-0.03,SD,sill+H,sill+H+SW,3); box(bm,o,u,n,Z,-h2-SW,-h2,-0.03,SD,sill,sill+H,3); box(bm,o,u,n,Z,h2,h2+SW,-0.03,SD,sill,sill+H,3)
                box(bm,o,u,n,Z,-h2-SW-0.04,h2+SW+0.04,-0.03,SD+0.05,sill-0.08,sill+0.005,2)
                n_win+=1; log.append((name[:12],round(o.x,2),round(o.y,2),round(sill,2),round(n.x,3),round(n.y,3)))
    if n_win==0: print('NOWIN',name); continue
    me=bpy.data.meshes.new('OQ_skirt_win_'+name[:30]); bm.to_mesh(me)
    for mm in (FR,GL,SL,sk.material_slots[0].material): me.materials.append(mm)
    ob=bpy.data.objects.new(('OQ_skirt_win_'+name)[:60],me); col.objects.link(ob)
    ob['UNVERIFIED']='oq: lower-storey windows on the oo skirt; count/size/style guessed to match the upper storeys'
    print('WIN',name,n_win)
open('data/oq/skirt_windows.txt','w').write('\n'.join(str(x) for x in log))
# ---------- (B) east walk tone
base=fp.material_slots[0].material; m=base.copy(); m.name=MATN
nt=m.node_tree; bs=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; bc=bs.inputs['Base Color']
if bc.is_linked:
    src=bc.links[0].from_socket
    geo=nt.nodes.new('ShaderNodeNewGeometry'); sx=nt.nodes.new('ShaderNodeSeparateXYZ'); mr=nt.nodes.new('ShaderNodeMapRange')
    mr.interpolation_type='SMOOTHSTEP'; mr.inputs['From Min'].default_value=92; mr.inputs['From Max'].default_value=104
    mr.inputs['To Min'].default_value=1.0; mr.inputs['To Max'].default_value=float(os.environ.get('EAST',0.66))
    mul=nt.nodes.new('ShaderNodeMix'); mul.data_type='RGBA'; mul.blend_type='MULTIPLY'; mul.inputs['Factor'].default_value=1.0
    cc=nt.nodes.new('ShaderNodeCombineColor')
    nt.links.new(geo.outputs['Position'],sx.inputs[0]); nt.links.new(sx.outputs['X'],mr.inputs['Value'])
    for k in ('Red','Green','Blue'): nt.links.new(mr.outputs[0],cc.inputs[k])
    nt.links.new(src,mul.inputs[6]); nt.links.new(cc.outputs[0],mul.inputs[7]); nt.links.new(mul.outputs[2],bc)
    fp.material_slots[0].link='OBJECT'; fp.material_slots[0].material=m; print('EAST tone',base.name,'->',m.name)
else: print('EAST: base colour not linked, skipped')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
