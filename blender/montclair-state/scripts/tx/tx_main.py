"""Session tx (Nov 5 2026 ~8:40 AM ET, MAIN, day 9): School of Nursing / Graduate School (historic Partridge Hall, OSM 313026395)
was MISSING from MAIN (bare ground patch). Build: OSM footprint (ODbL) + 2017 NJ LiDAR DSM levels (data/tx/nursing_levels.json):
roof deck 155.51 (DSM p60 low cells, MEASURED), perimeter parapet/top band to 158.0 (DSM ring, MEASURED +-0.4), two roof bulkheads (DSM).
Facade after Digital Commons slides #260/#860 (1970) and #1340 (1972): concrete pier+spandrel frame, dark ribbon glazing on the
long E/W faces, brown brick infill with punched windows on the N/S ends. Storey count 4 (slides), floor heights / bay widths UNVERIFIED.
ALL UNVERIFIED (form from 1970s slides; any renovation not checked). REVERT=1 removes everything tagged tx_obj."""
import bpy, bmesh, os, json, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE=os.environ.get('SAVE')=='1'
D='/workspace/nj-scenes/montclair-state/'
COLN='TX_Nursing_Partridge_Hall_massing_UNVERIFIED'
def revert():
    for o in [o for o in list(bpy.data.objects) if o.get('tx_obj')]:
        me=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if me is not None and me.users==0:
            (bpy.data.meshes if isinstance(me,bpy.types.Mesh) else bpy.data.cameras).remove(me)
    c=bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    for m in [m for m in bpy.data.materials if m.name.startswith('TX_') and m.users==0]: bpy.data.materials.remove(m)
    print('TX REVERTED')
revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
FP=[tuple(p) for p in json.load(open(D+'data/tx/nursing_geom.json'))['footprint']]
LV=json.load(open(D+'data/tx/nursing_levels.json'))
G0=138.60            # wall base, below lowest ring DTM 139.65 (MEASURED) so no gap
GR=140.06            # ring DTM median (MEASURED)
ROOF=LV['lo_top']    # 155.51 MEASURED
TOP=158.0            # parapet top, DSM ring p60 ~157.8-158.1 MEASURED
FL=[GR+0.0, GR+3.85, GR+7.70, GR+11.55]   # 4 storeys (slides); heights UNVERIFIED
col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)

def mat(name, rgb, rough=0.8, metal=0.0, noise=0.0, brick=False, spec=0.5):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    try: b.inputs['Specular IOR Level'].default_value=spec
    except Exception: pass
    if brick:
        t=nt.nodes.new('ShaderNodeTexBrick'); t.inputs['Scale'].default_value=1.0
        t.inputs['Color1'].default_value=(*rgb,1); t.inputs['Color2'].default_value=(rgb[0]*0.82,rgb[1]*0.8,rgb[2]*0.78,1)
        t.inputs['Mortar'].default_value=(0.12,0.10,0.085,1); t.inputs['Brick Width'].default_value=0.20; t.inputs['Row Height'].default_value=0.068
        t.inputs['Mortar Size'].default_value=0.010
        tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping')
        nt.links.new(tc.outputs['Object'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],t.inputs['Vector'])
        # brick runs along whichever horizontal axis: use x+y as u
        sep=nt.nodes.new('ShaderNodeSeparateXYZ'); cmb=nt.nodes.new('ShaderNodeCombineXYZ'); add=nt.nodes.new('ShaderNodeMath')
        nt.links.new(tc.outputs['Object'],sep.inputs[0]); nt.links.new(sep.outputs[0],add.inputs[0]); nt.links.new(sep.outputs[1],add.inputs[1])
        nt.links.new(add.outputs[0],cmb.inputs[0]); nt.links.new(sep.outputs[2],cmb.inputs[1]); nt.links.new(cmb.outputs[0],t.inputs['Vector'])
        nt.links.new(t.outputs['Color'],b.inputs['Base Color'])
    elif noise:
        n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=1.8; n.inputs['Detail'].default_value=6
        r=nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(rgb[0]*(1-noise),rgb[1]*(1-noise),rgb[2]*(1-noise),1)
        r.color_ramp.elements[1].color=(*rgb,1)
        nt.links.new(n.outputs['Fac'],r.inputs['Fac']); nt.links.new(r.outputs['Color'],b.inputs['Base Color'])
    else: b.inputs['Base Color'].default_value=(*rgb,1)
    return m
M=dict(conc=mat('TX_Partridge_precast_concrete_UNVERIFIED',(0.30,0.28,0.24),0.86,noise=0.14),
       glass=mat('TX_Partridge_dark_ribbon_glass_UNVERIFIED',(0.020,0.024,0.028),0.06,0.0,spec=0.6),
       brick=mat('TX_Partridge_brown_brick_UNVERIFIED',(0.075,0.027,0.013),0.9,brick=True),
       mull=mat('TX_Partridge_bronze_mullion_UNVERIFIED',(0.07,0.06,0.05),0.4,0.8),
       roof=mat('TX_Partridge_roof_membrane_UNVERIFIED',(0.27,0.27,0.265),0.9,noise=0.18),
       base=mat('TX_Partridge_base_grime_UNVERIFIED',(0.43,0.40,0.36),0.92,noise=0.2))

class MB:
    def __init__(s,name,mats):
        s.bm=bmesh.new(); s.name=name; s.mats=mats
    def box(s,c,u,n,w,dep,z0,z1,mi=0):
        """box centred at c (xy) along unit u, width w (along u), depth dep along n (from c-n*dep/2..c+n*dep/2)"""
        u=Vector((u[0],u[1],0)); n=Vector((n[0],n[1],0)); c=Vector((c[0],c[1],0))
        vs=[]
        for z in (z0,z1):
            for a,b_ in ((-1,-1),(1,-1),(1,1),(-1,1)):
                p=c+u*(a*w/2)+n*(b_*dep/2); vs.append(s.bm.verts.new((p.x,p.y,z)))
        F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        for f in F:
            try: s.bm.faces.new([vs[i] for i in f]).material_index=mi
            except ValueError: pass
    def prism(s,pts,z0,z1,mi=0,top=True,bottom=False):
        b=[s.bm.verts.new((x,y,z0)) for x,y in pts]; t=[s.bm.verts.new((x,y,z1)) for x,y in pts]; k=len(pts)
        for i in range(k):
            s.bm.faces.new((b[i],b[(i+1)%k],t[(i+1)%k],t[i])).material_index=mi
        if top: s.bm.faces.new(t).material_index=mi
        if bottom: s.bm.faces.new(list(reversed(b))).material_index=mi
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm,faces=s.bm.faces)
        me=bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o=bpy.data.objects.new(s.name,me); col.objects.link(o); o['tx_obj']=1
        for p in me.polygons: p.use_smooth=False
        return o

# orientation
A=sum(FP[i][0]*FP[(i+1)%len(FP)][1]-FP[(i+1)%len(FP)][0]*FP[i][1] for i in range(len(FP)))/2
ccw=A>0
PRE=json.load(open(D+'data/tx/nursing_pre.json'))   # shapely-precomputed (system python): 0.32 m inset core + DSM bulkheads
core=[tuple(p) for p in PRE['core']]
# 1) glazed core (recessed 0.32 m) + roof deck
mb=MB('TX Partridge core: dark glazing behind frame (UNVERIFIED)',[M['glass'],M['roof']])
mb.prism(core,G0,ROOF,0,top=False)
cp=[(x,y) for x,y in core]
tv=[mb.bm.verts.new((x,y,ROOF)) for x,y in cp]; f=mb.bm.faces.new(tv); f.material_index=1
oc=mb.done()
# 2) frame
fr=MB('TX Partridge precast frame: piers, spandrels, top band, plinth (UNVERIFIED)',[M['conc'],M['base'],M['brick'],M['mull']])
stats=dict(piers=0,spandrels=0,brick=0,mull=0,punched=0)
n=len(FP)
for i in range(n):
    p=Vector((*FP[i],0)); q=Vector((*FP[(i+1)%n],0)); e=q-p; L=e.length; u=e/L
    nrm=Vector((u.y,-u.x,0)) if ccw else Vector((-u.y,u.x,0))   # outward
    mid=(p+q)/2
    D_=0.42  # frame depth: from -0.32 (glass) to +0.10 proud
    cc=mid+nrm*(0.10-D_/2)
    # top band (parapet) full length, plinth
    fr.box(cc,u,nrm,L+0.02,D_,155.0,TOP,0); 
    fr.box(mid+nrm*(0.14-0.25),u,nrm,L+0.04,0.50,G0,GR+0.45,1)
    # coping lip
    fr.box(mid+nrm*0.0,u,nrm,L+0.06,0.40,TOP,TOP+0.06,0)
    if L<4.0:
        fr.box(cc,u,nrm,L+0.02,D_,GR+0.45,155.0,0); continue
    longface = abs(u.y)>abs(u.x)   # E/W faces run N-S
    nb=max(1,round(L/7.0)); bw=L/nb
    for k in range(nb+1):
        c=p+u*(k*bw); c=c+u*(0.35 if k==0 else (-0.35 if k==nb else 0))
        fr.box(c+nrm*(0.10-D_/2-0.02),u,nrm,0.70,D_+0.04,GR+0.45,155.0,0); stats['piers']+=1
    for z in FL[1:]+[GR+0.45]:
        z0=z-0.55 if z>GR+1 else GR+0.45; z1=z+0.45 if z>GR+1 else GR+1.15
        fr.box(cc,u,nrm,L,D_-0.04,z0,z1,0); stats['spandrels']+=1
    tops=[f_-0.55 for f_ in FL[1:]]+[155.0]; bots=[GR+1.15]+[f_+0.45 for f_ in FL[1:]]
    for k in range(nb):
        b0=p+u*(k*bw); b1=b0+u*bw
        inner0=b0+u*(0.70 if k==0 else 0.35); inner1=b1-u*(0.70 if k==nb-1 else 0.35); iw=(inner1-inner0).length; ic=(inner0+inner1)/2
        for zb,zt in zip(bots,tops):
            if longface:
                m_=max(2,round(iw/1.5))
                for j in range(1,m_):
                    fr.box(inner0+u*(j*iw/m_)+nrm*(-0.32+0.06),u,nrm,0.07,0.12,zb,zt,3); stats['mull']+=1
                fr.box(ic+nrm*(-0.32+0.06),u,nrm,iw,0.12,zb+(zt-zb)*0.62,zb+(zt-zb)*0.62+0.06,3)  # transom
            else:
                # brown brick infill, punched window ~1.3 m wide centred (slide #860 ends)
                ww=min(1.3,iw*0.3); side=(iw-ww)/2
                for sgn in (-1,1):
                    fr.box(ic+u*(sgn*(ww/2+side/2))+nrm*(-0.12),u,nrm,side,0.36,zb,zt,2); stats['brick']+=1
                h=zt-zb
                fr.box(ic+nrm*(-0.12),u,nrm,ww,0.36,zb,zb+h*0.18,2)
                fr.box(ic+nrm*(-0.12),u,nrm,ww,0.36,zt-h*0.10,zt,2); stats['punched']+=1
of=fr.done()
# 3) roof bulkheads from DSM 'hi' blocks that look like solid boxes (west-end stair/mech), set 1.5 m in from the edge
rb=MB('TX Partridge roof screens on DSM ridge lines (UNVERIFIED)',[M['conc'],M['roof']])
nbk=0
for bk in PRE['bulk']:
    x0,y0,x1,y1=bk['b']; rb.prism([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],ROOF-0.1,min(bk['top'],TOP+0.3),0); nbk+=1
for sc in PRE['screens']:
    rb.box(((sc['x0']+sc['x1'])/2,sc['y']),(1,0),(0,1),sc['x1']-sc['x0'],0.45,ROOF-0.1,TOP-0.2,0); nbk+=1
ob=rb.done() if nbk else None
if ob is None: print('TX no bulkheads kept')

# 4) entrances where OSM footways 313026399/403/404/405/406/407 meet the footprint (positions OSM; door form UNVERIFIED)
ENT=json.load(open(D+'data/tx/nursing_entr_nodes.json'))
OFF={3:(3,4,1.6),4:(3,4,-1.6),8:(8,8,0),12:(12,13,1.6),13:(13,13,0),14:(13,14,-1.6)}
dm=MB('TX Partridge entrances at OSM footway junctions (form UNVERIFIED)',[M['mull'],M['glass'],M['conc']])
def edge(i):
    p=Vector((*FP[i],0)); q=Vector((*FP[(i+1)%n],0)); e=q-p; return p,q,e.normalized()
nd=0
for en in ENT:
    i=en['i']; a,b,off=OFF[i]
    if a==b:   # mid-face node: use the longer adjacent edge direction
        pa,qa,ua=edge(i); pb,qb,ub=edge(i-1)
        u=ua if (qa-pa).length>(qb-pb).length else ub; c=Vector((*FP[i],0))
    else:
        p,q,u=edge(a); c=(p if i==a else q)+u*off if False else Vector((*FP[i],0))+u*off
    nr=Vector((u.y,-u.x,0)) if ccw else Vector((-u.y,u.x,0))
    W=2.6; H=2.9
    dm.box(c+nr*0.16,u,nr,W+0.30,0.10,GR-0.05,GR+H+0.25,0)          # bronze surround
    dm.box(c+nr*0.22,u,nr,W,0.04,GR+0.02,GR+H,1)                       # door glass
    for t in (-W/2,-0.02,0.02,W/2):
        dm.box(c+u*t+nr*0.25,u,nr,0.06,0.04,GR+0.02,GR+H,0)            # stiles
    dm.box(c+nr*0.25,u,nr,W,0.04,GR+2.25,GR+2.31,0)                    # transom bar
    dm.box(c+nr*0.75,u,nr,W+1.2,1.3,GR+H+0.25,GR+H+0.45,2)             # shallow concrete canopy
    dm.box(c+nr*1.30,u,nr,W+1.6,2.6,GR-1.80,GR+0.02,2)                 # landing slab (sinks into grade so no gap on the slope)
    nd+=1
od=dm.done(); print('TX doors',nd)
print('TX stats',stats,'bulkheads',nbk,'ccw',ccw,'core verts',len(core))
for o in (oc,of): print('TX OBJ',o.name,len(o.data.vertices))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
