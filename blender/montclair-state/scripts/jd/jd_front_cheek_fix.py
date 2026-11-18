# Session jd (2026-10-26 ~1:35 AM ET): real geometry fix for jc's leftover wedge facet where the front-row (bottom) aisle
# step meets the left aisle cheek of the front row (Kasser_amphitheater_bowl_hl, MAIN; visible in jc's close-up WIP).
# Cause: one 5-gon (riser material, iy_wedge=1, n=(0.65,-0.38,0.66), 344 cm2) ran diagonally from the aisle-step tread
# (z 134.08) up to the cheek's top-back corner (z 134.303), plus a riser triangle, because the tread/cheek/riser corner
# vertex at (x -168.20, y 12.263, z 134.08) never existed. Fix: delete those 2 faces, add that corner vertex, snap the
# tread back vertex (z 134.093 -> 134.08), and rebuild 4 faces: flat tread quad, vertical cheek triangle, vertical
# aisle-riser quad, and the 1.8 cm chamfer sliver; materials/attrs copied from the neighbouring face of each kind.
# Then re-runs jc_corner_cleanup with MAXA=MAXH=0 (no collapses) = iy_wedge_normals -> iz_block_jitter -> jc_riser_uv
# -> jc flat normals (jc_flatn), keeping the established chain. Vertices found by coordinates (3 mm tolerance).
# Env DRY=1, SAVE=1, OUTB=copy. Revert = backup montclair_state_pre_20261026jd.blend.
import bpy, bmesh, os, runpy, mathutils
from mathutils import Vector as V
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
if me.has_custom_normals:
    try: me.free_normals_split()
    except Exception: pass
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); bm.verts.ensure_lookup_table()
kd=mathutils.kdtree.KDTree(len(bm.verts))
for v in bm.verts: kd.insert(v.co,v.index)
kd.balance()
def fv(x,y,z):
    co,i,d=kd.find((x,y,z)); assert d<0.003,(x,y,z,d); return bm.verts[i]
A=fv(-168.185,12.054,134.08); B=fv(-168.09,12.055,134.08); C=fv(-168.093,12.266,134.093)
D=fv(-168.199,12.259,134.303); E=fv(-168.203,12.066,134.094); G=fv(-168.091,12.266,134.295)
def face_with(vs):
    s=set(vs)
    for f in vs[0].link_faces:
        if s<=set(f.verts): return f
def other(e_verts,excl):
    a,b=e_verts
    for f in a.link_faces:
        if b in f.verts and f not in excl: return f
def stats():
    bm.normal_update(); return sum(1 for f in bm.faces if f.normal.z<-0.05), sum(1 for e in bm.edges if len(e.link_faces)!=2 and not e.is_boundary), sum(1 for e in bm.edges if len(e.link_faces)>2)
d0,_,nm0=stats(); bd0=sum(1 for e in bm.edges if e.is_boundary)
W=face_with([E,A,B,C,D]); R=face_with([D,C,G]); assert W and R and len(W.verts)==5 and len(R.verts)==3,(W,R)
ex_tread=other((A,B),{W}); ex_sliv=other((E,A),{W}); ex_cheek=other((D,E),{W}); ex_riser=other((C,G),{R})
print('JD wedge n',[round(x,2) for x in W.normal],'area cm2',round(W.calc_area()*1e4,1),'examples',ex_tread.index,ex_sliv.index,ex_cheek.index,ex_riser.index)
exs={k:f.copy(verts=False,edges=False) for k,f in (('t',ex_tread),('s',ex_sliv),('c',ex_cheek),('r',ex_riser))}  # detached copies as attr templates
bmesh.ops.delete(bm,geom=[W,R],context='FACES_ONLY')
C.co.z=134.08
N=bm.verts.new(V((-168.200,12.263,134.08)))
want={'t':V((0,0,1)),'s':V((0.7,-0.2,0.7)),'c':V((1,0,0)),'r':V((0,-1,0))}
new=[]
for k,vs in (('t',[A,B,C,N]),('s',[E,A,N]),('c',[E,N,D]),('r',[N,C,G,D])):
    f=bm.faces.new(vs,exs[k]); f.normal_update()
    if f.normal.dot(want[k])<0: f.normal_flip()
    new.append(f)
for f in exs.values(): bm.faces.remove(f)
wl=bm.faces.layers.int.get('iy_wedge')
for f in new:
    if wl: f[wl]=0
bm.normal_update()
for f,k in zip(new,'tscr'): print('JD new',k,f.index,'n',[round(x,2) for x in f.normal],'A cm2',round(f.calc_area()*1e4,1))
d1,_,nm1=stats(); bd1=sum(1 for e in bm.edges if e.is_boundary)
print('JD down-facing',d0,'->',d1,'edges>2 faces',nm0,'->',nm1,'boundary',bd0,'->',bd1,'faces',len(bm.faces))
if os.environ.get('DRY')=='1': bm.free(); raise SystemExit
bm.to_mesh(me); bm.free(); me.update()
sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
os.environ['MAXA']='0'; os.environ['MAXH']='0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/jc/jc_corner_cleanup.py',run_name='__main__')
for k,v in sv.items():
    if v is not None: os.environ[k]=v
ob['jd_front_cheek_fix']='2026-10-26 session jd: front-row left aisle-cheek wedge 5-gon + riser tri rebuilt as tread/cheek/riser/chamfer (new corner vert); chain re-run'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JD WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JD SAVED')
