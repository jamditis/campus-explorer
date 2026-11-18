# ws169b: Sprague Field E light standard (new find, prepped in ws169 from LiDAR; not yet in the model per script grep).
# Evidence: 2023 NJ LiDAR (prep/ws163_lot3S/las163.npy) class-1 returns: a thin vertical trace at (-305.5,-204.8) from 4 to 9 m, and a dense
# flat-topped head 24-28 m above Sprague level (115.7) spanning x -306.9..-304.9, y -208.0..-201.4 (about 2 m x 6.5 m) = a sports-lighting
# pole with a crossarm/luminaire head, standing at the top of the Lot 3 W bank (walk outer edge) and lighting Sprague Field to the W.
# Build (UNVERIFIED detail, typical Musco-type design): concrete pier 0.9 m dia 0.6 m proud; galvanised tapered pole 0.56->0.30 m to 26.4 m;
# head = 3 crossarms (6.4 m along y) x 5 luminaires each (0.55 x 0.45 x 0.35 m boxes, aimed W and tilted 25 deg down), back frame.
# No depsgraph evaluation. Idempotent (removes WS169_light_ first).
import bpy, bmesh, math, numpy as np
from mathutils import Matrix, Vector
OB=bpy.data.objects
ZS=np.load('/workspace/nj-scenes/montclair-state/scripts/ws162/dtm162.npy')[1]; X0,Y1,R=-330.0,-165.0,0.5
def dz(x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
for o in [o for o in OB if o.name.startswith('WS169_light_')]: OB.remove(o)
col=bpy.data.collections.get('WS167_Sprague_E_bank_lane_bleachers') or bpy.context.scene.collection
def mat(n,rgb,rough,metal=0.0,emit=None):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal; return m
galv=mat('WS169_galvanised_steel',(0.55,0.56,0.57),0.45,0.8); conc=mat('WS27_curb_concrete_UNVERIFIED',(0.55,0.54,0.51),0.85)
lens=mat('WS169_luminaire_lens_off',(0.75,0.77,0.78),0.15,0.0); hous=mat('WS169_luminaire_housing_dark',(0.12,0.12,0.13),0.5,0.6)
PX,PY=-305.5,-204.8; zg=min(dz(PX+a,PY+b) for a in (-0.45,0,0.45) for b in (-0.45,0,0.45))
def mk(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m_ in mats: me.materials.append(m_)
    for p in me.polygons: p.use_smooth=True
    o=OB.new(name,me); col.objects.link(o); return o
bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=24,radius1=0.45,radius2=0.45,depth=0.6+(dz(PX,PY)-zg)+0.3)
bmesh.ops.translate(bm,verts=bm.verts,vec=Vector((PX,PY,zg-0.3+(0.6+(dz(PX,PY)-zg)+0.3)/2)))
mk('WS169_light_Sprague_E_pier_concrete_UNVERIFIED',bm,[conc])
ztop=dz(PX,PY)+0.6; H=26.4
bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=20,radius1=0.28,radius2=0.15,depth=H)
bmesh.ops.translate(bm,verts=bm.verts,vec=Vector((PX,PY,ztop+H/2)))
mk('WS169_light_Sprague_E_pole_LiDAR2023_h27m',bm,[galv])
# head: frame + crossarms + luminaires facing -X (W, toward Sprague Field)
bm=bmesh.new(); zH=115.7+26.6
def box(c,s,rot=None):
    r=bmesh.ops.create_cube(bm,size=1.0); vs=r['verts']
    bmesh.ops.scale(bm,vec=Vector(s),verts=vs)
    if rot is not None: bmesh.ops.rotate(bm,verts=vs,cent=Vector((0,0,0)),matrix=rot)
    bmesh.ops.translate(bm,verts=vs,vec=Vector(c)); return vs
box((PX,PY,zH-1.0),(0.12,0.12,2.4))                    # pole stub into head
box((PX-0.05,PY-1.3,zH-1.0),(0.10,0.10,2.6)); box((PX-0.05,PY+1.3,zH-1.0),(0.10,0.10,2.6))   # frame verticals (UNVERIFIED)
for k in range(3):
    box((PX-0.15,PY,zH-0.1-k*0.85),(0.12,6.4,0.12))   # crossarms along y
hb=mk('WS169_light_Sprague_E_head_frame_UNVERIFIEDlayout',bm,[galv])
bm=bmesh.new(); tilt=Matrix.Rotation(math.radians(-25),3,'Y')
for k in range(3):
    for m_ in range(5):
        y=PY-2.6+m_*1.3; z=zH-0.1-k*0.85-0.05
        vs=box((PX-0.55,y,z),(0.35,0.55,0.45),tilt)
lm=mk('WS169_light_Sprague_E_luminaires_15_UNVERIFIEDcount',bm,[hous])
print('LIGHT169 pier zg %.2f pole base %.2f top %.2f head %.2f (LiDAR head top ~%.1f)'%(zg,ztop,ztop+H,zH,115.7+27.8),flush=True)
# diagnostic: other pole/light objects whose bbox centre lies within 6 m (generic poles from early sessions) -> review/remove if duplicate
for o in OB:
    n=o.name.lower()
    if o.name.startswith('WS169_') or not ('pole' in n or 'light' in n or 'lamp' in n): continue
    try:
        from mathutils import Vector as _V
        bb=[o.matrix_world@_V(c) for c in o.bound_box]; cx=sum(c.x for c in bb)/8; cy=sum(c.y for c in bb)/8
        if math.hypot(cx-PX,cy-PY)<6: print('LIGHT169 nearby existing',o.name,round(cx,1),round(cy,1),flush=True)
    except Exception: pass
