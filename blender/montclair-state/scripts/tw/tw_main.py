"""Session tw (Nov 5 2026 ~7:30 AM ET, MAIN, day 9 College Hall). ALL UNVERIFIED, reversible (REVERT=1).

Refine Oct 16 bq Cole Hall (= Susan A. Cole Hall / historic College Hall):
1) Rebuild the three roof cupolas / central bell tower to bk LiDAR centres+tops and Commons
   proportions (Daniel Case CC BY-SA 3.0): oxblood open belfry with 4 corner posts, projecting
   intermediate eave, smaller upper lantern, verdigris ogee dome, taller needle finial. Keep
   south belvederes. Hide (do not delete) the bq towers mesh.
2) Wall tone: cream Mission stucco material TW_Cole_stucco_cream_UNVERIFIED on S/W photo faces
   (slides #311/#259 show light walls; 2020s renovation may differ — flagged UNVERIFIED).
3) Window rhythm: hide bq S+W windows; rebuild west-wing + south punched openings using bm JSON
   metres ×0.70 (identity correction: wall was over-scaled). No AC units, no street furniture.

Sources: day9_college_hall_cupola_dims_20261016bk.json, cupola_xy bj, window_rhythm bm,
cole_hall_identity bq, refs/day9 slides, refs/Cupola_and_bell_tower_….jpg.
"""
import bpy, bmesh, os, math, json
from mathutils import Vector, Matrix

REV=os.environ.get('REVERT')=='1'
SAVE=os.environ.get('SAVE')=='1'
DRY=os.environ.get('DRY')=='1'
D='/workspace/nj-scenes/montclair-state/'
CN='TW_Cole_Hall_refine_UNVERIFIED'
TOWERS_BQ='Cole Hall roof towers (LiDAR xy/top MEASURED; forms UNVERIFIED)'  # 63-char Blender truncate
WINS_BQ='Cole Hall windows S+W faces (rhythm UNVERIFIED; photos 2023/PD)'  # 63-char Blender truncate
WALLS='Susan A. Cole Hall walls'
TW_TOWERS='TW_Cole_roof_towers_UNVERIFIED'
TW_WINS='TW_Cole_windows_SW_UNVERIFIED'
TW_STUCCO='TW_Cole_stucco_cream_UNVERIFIED'
TAG='tw_obj'

def mat(name,col,rough=0.6,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*col,1)
    b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal
    return m

def revert():
    # remove tw-tagged objects
    for o in [o for o in list(bpy.data.objects) if o.get(TAG)]:
        me=o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users==0:
            if hasattr(me,'vertices'): bpy.data.meshes.remove(me)
            elif hasattr(me,'lens'): bpy.data.cameras.remove(me)
    c=bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    # unhide bq towers / windows
    for nm in (TOWERS_BQ, WINS_BQ):
        o=bpy.data.objects.get(nm)
        if o:
            o.hide_set(False); o.hide_render=False
            if 'tw_hidden' in o: del o['tw_hidden']
    # restore wall material slot assignments
    w=bpy.data.objects.get(WALLS)
    if w and 'tw_wall_slots' in w:
        slots=list(w['tw_wall_slots'])
        for i,poly in enumerate(w.data.polygons):
            if i < len(slots): poly.material_index=int(slots[i])
        del w['tw_wall_slots']
        if 'tw_stucco_si' in w: del w['tw_stucco_si']
    # remove TW materials we created (orphan after mesh removal / wall slot restore)
    for m in list(bpy.data.materials):
        if m.name.startswith('TW_Cole_') or m.name==TW_STUCCO:
            if m.users==0:
                bpy.data.materials.remove(m)
            else:
                # still slotted on walls but unused on faces — clear slot refs then remove
                for ob in bpy.data.objects:
                    if ob.type!='MESH': continue
                    for i,s in enumerate(ob.material_slots):
                        if s.material==m:
                            ob.material_slots[i].material=None
                # also strip from mesh materials lists
                for me in bpy.data.meshes:
                    for i,mm in enumerate(list(me.materials)):
                        if mm==m: me.materials[i]=None
                if m.users==0:
                    bpy.data.materials.remove(m)
    # strip empty trailing material slots left after cream removal
    w=bpy.data.objects.get(WALLS)
    if w:
        while w.data.materials and w.data.materials[-1] is None:
            w.data.materials.pop(index=len(w.data.materials)-1)
        # also drop any remaining None holes by compacting if safe (no faces use higher indices)
        mats=list(w.data.materials)
        if any(m is None for m in mats):
            # only compact trailing Nones already handled; leave mid-list alone
            pass
    print('TW REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# ---- materials (UNVERIFIED tones from Commons + 1965/66 slides) ----
# oxblood darker/desaturated vs terracotta tile (Commons note)
M_ox=mat('TW_Cole_oxblood_wood_UNVERIFIED',(0.22,0.055,0.04),0.68)
M_cu=mat('TW_Cole_copper_verdigris_UNVERIFIED',(0.28,0.50,0.42),0.48,0.25)
M_dk=mat('TW_Cole_loggia_shadow_UNVERIFIED',(0.018,0.016,0.014),0.92)
M_tile=mat('TW_Cole_tower_tile_UNVERIFIED',(0.42,0.14,0.07),0.72)  # terracotta hip on belvederes
M_st=mat(TW_STUCCO,(0.86,0.835,0.78),0.88)  # cream Mission from slides #311/#259
M_fr=mat('TW_Cole_win_frame_UNVERIFIED',(0.92,0.90,0.86),0.55)  # white trim
M_gl=mat('TW_Cole_win_glass_UNVERIFIED',(0.04,0.05,0.055),0.25)
M_br=mat('TW_Cole_dark_wood_UNVERIFIED',(0.09,0.045,0.03),0.6)

sc=bpy.context.scene
col=bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
if CN not in [c.name for c in sc.collection.children]:
    sc.collection.children.link(col)

def new_obj(name,mats):
    me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me); col.objects.link(o)
    for m in mats: me.materials.append(m)
    o[TAG]=1; o['tw_source']='20261105tw'; return o

def add_box(bm,cx,cy,z0,z1,hx,hy,rot,mi):
    R=Matrix.Rotation(rot,4,'Z')
    vs=[bm.verts.new(Vector((cx,cy,0))+(R@Vector((sx*hx,sy*hy,0))).to_3d()+Vector((0,0,z)))
        for z in (z0,z1) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    for f in ((0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
        bm.faces.new([vs[i] for i in f]).material_index=mi

def add_pyr(bm,cx,cy,z0,z1,h,rot,mi):
    R=Matrix.Rotation(rot,4,'Z')
    b=[bm.verts.new(Vector((cx,cy,z0))+(R@Vector((sx*h,sy*h,0))).to_3d()) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    a=bm.verts.new((cx,cy,z1))
    for i in range(4): bm.faces.new([b[i],b[(i+1)%4],a]).material_index=mi
    bm.faces.new(b[::-1]).material_index=mi

def add_dome(bm,cx,cy,z0,z1,r,mi,seg=12,rings=6):
    prev=None
    for k in range(rings+1):
        t=k/rings; zz=z0+(z1-z0)*t
        # ogee/bell: swell then taper
        rr=r*(1.0-t**1.55)*(1.0+0.20*math.sin(math.pi*t))
        cur=[bm.verts.new((cx+rr*math.cos(2*math.pi*j/seg),cy+rr*math.sin(2*math.pi*j/seg),zz)) for j in range(seg)]
        if prev:
            for j in range(seg):
                bm.faces.new([prev[j],prev[(j+1)%seg],cur[(j+1)%seg],cur[j]]).material_index=mi
        prev=cur

def corner_posts(bm,cx,cy,z0,z1,h,rot,mi,pw=0.28):
    """Four corner posts only (Commons: open belfry on 4 pillars)."""
    R=Matrix.Rotation(rot,4,'Z')
    for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
        p=R@Vector((sx*(h-pw*0.15),sy*(h-pw*0.15),0))
        add_box(bm,cx+p.x,cy+p.y,z0,z1,pw/2,pw/2,rot,mi)

def balustrade(bm,cx,cy,z0,z1,h,rot,mi,nslat=5,sw=0.06):
    """Panelled/slat balustrade band between corner posts."""
    R=Matrix.Rotation(rot,4,'Z')
    # solid rail top + bottom rails as thin boxes on each side
    add_box(bm,cx,cy,z0,z0+0.08,h*0.98,h*0.98,rot,mi)
    add_box(bm,cx,cy,z1-0.08,z1,h*0.98,h*0.98,rot,mi)
    for s in range(4):
        for k in range(1,nslat):
            u=-1+2*k/nslat
            loc=[(u*h*0.85,-h),(h,u*h*0.85),(-u*h*0.85,h),(-h,-u*h*0.85)][s]
            p=R@Vector((loc[0],loc[1],0))
            add_box(bm,cx+p.x,cy+p.y,z0+0.08,z1-0.08,sw/2,sw/2,rot,mi)

def build_central_cupola(bm,cx,cy,rot,top=157.96):
    """Stages from bk JSON (UNVERIFIED splits; tip MEASURED). Commons proportions."""
    # mats indices: 0 stucco, 1 tile, 2 oxblood, 3 copper, 4 shadow, 5 frame, 6 dark wood
    # red base box from roof deck ~149
    z_deck=149.0
    add_box(bm,cx,cy,z_deck,150.6,1.50,1.50,rot,2)          # oxblood clapboard base
    add_box(bm,cx,cy,150.6,150.78,1.62,1.62,rot,2)           # sill lip
    # open lower belfry (tallest stage): dark core + 4 corner posts + balustrade
    z_b0,z_b1=150.78,153.85
    add_box(bm,cx,cy,z_b0,z_b1,1.05,1.05,rot,4)             # shadow core
    corner_posts(bm,cx,cy,z_b0,z_b1,1.40,rot,2,pw=0.30)
    balustrade(bm,cx,cy,z_b0,z_b0+0.85,1.38,rot,2,nslat=5)
    # deep bracketed cornice / intermediate flat roof with projecting eave (Commons)
    add_box(bm,cx,cy,z_b1,154.05,1.72,1.72,rot,2)           # cornice body
    add_box(bm,cx,cy,154.05,154.22,1.85,1.85,rot,2)          # projecting eave lip
    # upper lantern (smaller ~0.72×)
    z_u0,z_u1=154.22,156.15
    add_box(bm,cx,cy,z_u0,z_u1,0.78,0.78,rot,4)
    corner_posts(bm,cx,cy,z_u0,z_u1,1.00,rot,2,pw=0.22)
    balustrade(bm,cx,cy,z_u0,z_u0+0.55,0.98,rot,2,nslat=4)
    add_box(bm,cx,cy,z_u1,156.35,1.15,1.15,rot,2)           # upper cornice
    # copper ogee dome + corner ball finials
    add_dome(bm,cx,cy,156.35,157.40,0.95,3)
    for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
        p=Matrix.Rotation(rot,4,'Z')@Vector((sx*1.05,sy*1.05,0))
        add_box(bm,cx+p.x,cy+p.y,156.35,156.58,0.10,0.10,rot,3)
    # taller needle finial (Commons: nearly as tall as dome) pinned to MEASURED tip
    add_box(bm,cx,cy,157.35,top,0.04,0.04,rot,3)
    add_box(bm,cx,cy,top-0.12,top,0.07,0.07,rot,3)         # tip knob

def build_flank_cupola(bm,bx,by,rot,top):
    """Scaled oxblood belfry + verdigris dome; splits UNVERIFIED, tip MEASURED."""
    k=(top-149.0)/(157.96-149.0)
    def Z(z): return 149.0+(z-149.0)*k
    add_box(bm,bx,by,148.6,Z(150.6),1.30,1.30,rot,2)
    add_box(bm,bx,by,Z(150.6),Z(150.75),1.42,1.42,rot,2)
    z0,z1=Z(150.75),Z(153.9)
    add_box(bm,bx,by,z0,z1,0.95,0.95,rot,4)
    corner_posts(bm,bx,by,z0,z1,1.20,rot,2,pw=0.24)
    balustrade(bm,bx,by,z0,z0+0.7,1.18,rot,2,nslat=4)
    add_box(bm,bx,by,z1,Z(154.25),1.55,1.55,rot,2)
    add_dome(bm,bx,by,Z(154.25),top-0.45,0.95,3)
    add_box(bm,bx,by,top-0.45,top,0.04,0.04,rot,3)

def build_belvedere(bm,bx,by,rot,top=150.0):
    """South belvederes flanking gable (LiDAR pads MEASURED; form UNVERIFIED)."""
    h=2.15
    add_box(bm,bx,by,141.0,146.55,h,h,rot,0)
    add_box(bm,bx,by,146.55,146.72,h+0.08,h+0.08,rot,0)
    add_box(bm,bx,by,146.72,149.05,h-0.40,h-0.40,rot,4)
    corner_posts(bm,bx,by,146.72,149.05,h-0.12,rot,6,pw=0.24)
    balustrade(bm,bx,by,146.72,147.45,h-0.08,rot,0,nslat=4)
    add_box(bm,bx,by,149.05,149.30,h+0.50,h+0.50,rot,6)
    add_pyr(bm,bx,by,149.30,top,h+0.50,rot,1)

# building rotation from long wall (same as bq)
rot=math.atan2(-104.247+98.217,-126.347+151.955)

if not DRY:
    # hide bq towers (keep for revert)
    bq=bpy.data.objects.get(TOWERS_BQ)
    if bq:
        bq.hide_set(True); bq.hide_render=True; bq['tw_hidden']=1
    tw=new_obj(TW_TOWERS,[M_st,M_tile,M_ox,M_cu,M_dk,M_fr,M_br])
    bm=bmesh.new()
    build_central_cupola(bm,-113.21,-95.5,rot,157.96)
    build_flank_cupola(bm,-137.0,-89.4,rot,155.72)
    build_flank_cupola(bm,-89.1,-101.6,rot,155.76)
    build_belvedere(bm,-124.0,-106.5,rot,150.0)
    build_belvedere(bm,-108.5,-108.5,rot,150.0)
    bm.to_mesh(tw.data); bm.free()
    print('TW towers verts',len(tw.data.vertices),'top_ok',max(v.co.z for v in tw.data.vertices))

# ---- wall tone (S/W photo faces -> cream Mission) ----
w=bpy.data.objects.get(WALLS)
if w and not DRY:
    me=w.data
    # backup slot indices
    w['tw_wall_slots']=[p.material_index for p in me.polygons]
    if TW_STUCCO not in [m.name if m else '' for m in me.materials]:
        me.materials.append(M_st)
    names=[m.name if m else '' for m in me.materials]
    si=names.index(TW_STUCCO)
    # also keep plain_bq index if present
    nfix=0
    for poly in me.polygons:
        nw=-(w.matrix_world.to_3x3()@poly.normal).normalized()
        cw=w.matrix_world@poly.center
        if abs(nw.z)>0.5: continue
        # south front + west wing west face (same rule as bq) + more of south
        if nw.y<-0.55 or (nw.x<-0.55 and cw.x<-140):
            poly.material_index=si; nfix+=1
    print('TW wall cream faces',nfix,'si',si)

# ---- windows: corrected rhythm (bm × 0.70) ----
# grade / wall from identity: DTM ~131.61, wall ~11.2 m -> eave ~142.8
GRADE=131.61
SCALE=0.70
# bm metres ×0.70
pitch=2.11*SCALE          # ~1.48
ww=1.39*SCALE             # ~0.97
wh_r1=2.72*SCALE          # ~1.90
wh_r2=3.27*SCALE
wh_r3=3.05*SCALE
# sill heights above grade ×0.70
sill=[1.58*SCALE, 6.29*SCALE, 11.64*SCALE]
# ring from levels prep
ring=json.load(open(D+'north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
P=[Vector((x,y)) for x,y in ring]
if P[0]==P[-1]: P=P[:-1]
area=sum(P[i].x*P[(i+1)%len(P)].y-P[(i+1)%len(P)].x*P[i].y for i in range(len(P)))/2

def add_win(bm,cx,cy,z0,z1,hx,hy,rot,out_n):
    """Frame box proud of wall + glass inset. out_n = outward unit normal (xy)."""
    # push centre slightly out so it sits on the wall face
    ox,oy=out_n.x*0.08, out_n.y*0.08
    # orient half-extents: width along tangent, depth along normal
    # use rot for box; depth thin
    add_box(bm,cx+ox,cy+oy,z0,z1,hx,0.06,rot,0)  # white frame outer
    add_box(bm,cx+ox*1.4,cy+oy*1.4,z0+0.06,z1-0.06,hx*0.78,0.04,rot,1)  # glass

if not DRY:
    bqw=bpy.data.objects.get(WINS_BQ)
    if bqw:
        bqw.hide_set(True); bqw.hide_render=True; bqw['tw_hidden']=1
    win=new_obj(TW_WINS,[M_fr,M_gl,M_st])
    bm=bmesh.new(); nwin=0
    # process edges: south (n.y<-0.55) and west of west wing (n.x<-0.55, mid x)
    for i in range(len(P)):
        a,b=P[i],P[(i+1)%len(P)]; d=b-a; L=d.length
        if L<5.0: continue
        t=d/L
        n=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x))
        # outward for this CCW/CW ring
        is_south=n.y<-0.55
        is_west=n.x<-0.55 and ((a.x+b.x)/2)<-140
        if not (is_south or is_west): continue
        # skip very short / gable pavilion edges (approx: near south gable centre)
        mid=((a+b)/2)
        if is_south and -122 < mid.x < -110 and mid.y < -105:
            # gable face — fewer tall arched openings handled lightly: 3 rows of 2
            pass
        edge_rot=math.atan2(t.y,t.x)
        # bay centres along edge, inset 1.2 m from ends
        margin=1.2
        usable=L-2*margin
        if usable < pitch: continue
        nb=max(1, int(round(usable/pitch)))
        # west face: r1 every OTHER bay (bm note); r2/r3 denser
        for row,(sz,wh) in enumerate(zip(sill,(wh_r1,wh_r2,wh_r3))):
            z0=GRADE+sz; z1=z0+wh
            if z1 > 142.6: z1=142.55  # under eave
            for k in range(nb):
                if row==0 and (k%2)==1 and is_west:
                    continue  # blank alternate ground bays on west
                # r2/r3: skip one bay near end of dense group (bm: group of 5 then skip)
                if row>=1 and is_west and k==5:
                    continue
                u=margin + (k+0.5)*(usable/nb)
                cx=a.x+t.x*u; cy=a.y+t.y*u
                # half-width along tangent; thin depth — use hx along local x of rotated box
                # rotate box so its local X aligns with tangent: edge_rot
                add_box(bm, cx+n.x*0.10, cy+n.y*0.10, z0, z1, ww/2, 0.07, edge_rot, 0)
                add_box(bm, cx+n.x*0.16, cy+n.y*0.16, z0+0.05, z1-0.05, ww/2*0.78, 0.04, edge_rot, 1)
                nwin+=1
    bm.to_mesh(win.data); bm.free()
    print('TW windows',nwin)

if SAVE and not DRY:
    bpy.ops.wm.save_mainfile(); print('SAVED')
print('TW DONE')
