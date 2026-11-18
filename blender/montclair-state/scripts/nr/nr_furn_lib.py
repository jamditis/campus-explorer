# nr furniture library (Oct 30 2026, session nr): bmesh builders shared by the main build and assets/furniture_kit_nr.blend
# Local frame: floor at z=0, sitter faces -X, chair back on +X side. All generic, UNVERIFIED models (no photo of CCOM furniture).
import bmesh, mathutils, math
V=mathutils.Vector
def _box(bm,c,s,mi=0):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=V((c[0]+v.co.x*s[0],c[1]+v.co.y*s[1],c[2]+v.co.z*s[2]))
    for f in {f for v in r['verts'] for f in v.link_faces}: f.material_index=mi
    return r['verts']
def _rbox(bm,c,s,rad,mi=0,seg=3):
    # box with rounded vertical + horizontal edges (bmesh bevel on all edges)
    vs=_box(bm,c,s,mi)
    es=list({e for v in vs for e in v.link_edges})
    bmesh.ops.bevel(bm,geom=vs+es,offset=min(rad,min(s)*0.45),segments=seg,profile=0.5,affect='EDGES',clamp_overlap=True)
def _tube(bm,p0,p1,r,mi=0,seg=10):
    p0=V(p0);p1=V(p1);d=p1-p0;L=d.length
    res=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=L)
    q=V((0,0,1)).rotation_difference(d.normalized()); M=mathutils.Matrix.Translation((p0+p1)/2)@q.to_matrix().to_4x4()
    bmesh.ops.transform(bm,matrix=M,verts=res['verts'])
    for f in {f for v in res['verts'] for f in v.link_faces}: f.material_index=mi
def _smooth(bm):
    for f in bm.faces: f.smooth=True
def cafe_chair(bm):
    """mi0 = shell (seat/back colour), mi1 = charcoal powder-coat tube, mi2 = black glide"""
    H=0.45
    _rbox(bm,(0,0,H-0.018),(0.44,0.44,0.036),0.016,0)               # seat pan
    _rbox(bm,(0.205,0,H+0.27),(0.035,0.42,0.24),0.014,0)             # back panel
    for y in (-0.17,0.17):
        _tube(bm,(0.20,y,H-0.03),(0.215,y,H+0.17),0.010,1)          # back posts
    for x in (-0.17,0.17):
        for y in (-0.17,0.17):
            b=(x*1.12,y*1.12,0.012)
            _tube(bm,(x,y,H-0.036),b,0.011,1)                      # splayed legs
            _tube(bm,(b[0],b[1],0.0),(b[0],b[1],0.013),0.013,2,8)   # glides
    _tube(bm,(-0.17,-0.17,0.20),(-0.17,0.17,0.20),0.008,1); _tube(bm,(0.17,-0.17,0.20),(0.17,0.17,0.20),0.008,1)  # side rails
def pedestal_table(bm,w=0.80,d=0.80,h=0.75):
    """mi0 = top laminate, mi1 = dark metal, mi2 = glides, mi3 = edge band"""
    _rbox(bm,(0,0,h-0.014),(w,d,0.028),0.006,0,2)
    _rbox(bm,(0,0,h-0.031),(w-0.006,d-0.006,0.006),0.003,3,1)          # dark edge/underside band
    _tube(bm,(0,0,0.04),(0,0,h-0.034),0.038,1,16)                    # column
    _box(bm,(0,0,h-0.045),(0.42,0.05,0.02),1); _box(bm,(0,0,h-0.045),(0.05,0.42,0.02),1)   # spider
    _rbox(bm,(0,0,0.035),(0.62,0.06,0.04),0.008,1,2); _rbox(bm,(0,0,0.035),(0.06,0.62,0.04),0.008,1,2)   # cross foot
    for a in range(4):
        t=a*math.pi/2; x,y=0.29*math.cos(t),0.29*math.sin(t)
        _tube(bm,(x,y,0.0),(x,y,0.016),0.016,2,10)
def task_chair(bm):
    """mi0 = upholstery, mi1 = black nylon base/frame, mi2 = chrome gas lift, mi3 = caster wheel"""
    H=0.47
    _rbox(bm,(0,0,H-0.035),(0.49,0.48,0.07),0.03,0,3)                 # seat cushion
    bk=V((0.25,0,H+0.31))
    vs_before=set(bm.verts)
    _rbox(bm,(0,0,0),(0.06,0.46,0.48),0.03,0,3)
    new=[v for v in bm.verts if v not in vs_before]
    M=mathutils.Matrix.Translation(bk)@mathutils.Matrix.Rotation(math.radians(-8),4,'Y')
    bmesh.ops.transform(bm,matrix=M,verts=new)                        # backrest, reclined 8 deg
    _box(bm,(0.20,0,H+0.02),(0.10,0.06,0.03),1); _tube(bm,(0.24,0,H+0.02),(0.255,0,H+0.12),0.022,1,8)  # back spine
    _box(bm,(0,0,H-0.085),(0.24,0.20,0.03),1)                        # seat plate / mechanism
    _tube(bm,(0,0,0.11),(0,0,H-0.10),0.026,2,16)                      # gas lift
    _tube(bm,(0,0,0.085),(0,0,0.15),0.040,1,16)                       # hub
    for i in range(5):
        t=i*2*math.pi/5+math.pi/10; c,s=math.cos(t),math.sin(t)
        e=V((0.31*c,0.31*s,0.075))
        _tube(bm,(0.03*c,0.03*s,0.115),e,0.017,1,8)                   # star leg
        _tube(bm,(e.x,e.y,0.075),(e.x,e.y,0.05),0.009,1,6)            # caster stem
        p=V((e.x+0.02*c,e.y+0.02*s,0.026)); ax=V((-s,c,0))*0.011
        _tube(bm,p-ax,p+ax,0.026,3,12)                                # caster wheel (touches floor at z=0)
        _box(bm,(e.x+0.01*c,e.y+0.01*s,0.048),(0.035,0.035,0.012),1)  # caster fork top
    for y in (-0.26,0.26):                                           # T-arms
        _tube(bm,(0.02,y*0.95,H-0.06),(0.04,y,H+0.18),0.012,1,8)
        _rbox(bm,(0.0,y,H+0.195),(0.24,0.06,0.025),0.01,1,2)
