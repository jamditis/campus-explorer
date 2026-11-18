# tl (Nov 4 2026 ~9:40 PM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Bohn Hall upper levels L1..PH rebuilt as RECTILINEAR masses (data/tl/bohn_levels_rect.json: same 2017 DSM thresholds/tops as tk,
# sampled on a grid aligned to the OSM walls and orthogonalised) -> replaces tk's faceted/rounded raster outlines.
# Blank-wall rule: wall runs < 4.5 m stay blank (stair/end walls), instead of tk's < 8 m. tk masses are hidden (not deleted) for exact revert.
import bpy, bmesh, os, json, math
REV=os.environ.get('REVERT')=='1'
def revert():
    for o in [o for o in bpy.data.objects if 'tl_obj' in o]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0: bpy.data.meshes.remove(me)
    for o in bpy.data.objects:
        if 'tl_hidden' in o:
            o.hide_render=bool(o['tl_hidden'][0]); o.hide_viewport=bool(o['tl_hidden'][1]); del o['tl_hidden']
    print('TL reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
col=bpy.data.collections['TK_Bohn_Hall_UNVERIFIED']
BM=bpy.data.materials['TK_Bohn_wall_eggcrate_UNVERIFIED']; RM=bpy.data.materials['TI_roof_membrane_UNVERIFIED']
base=bpy.data.objects['TK_Bohn_Hall_232853538_base_UNVERIFIED']; z0g=float(base.data.attributes['ti_z0'].data[0].value)
FL=float(base.data.attributes['ti_floor'].data[0].value)
hid=0
for o in list(col.objects):
    if o.type=='MESH' and o.name.startswith('TK_Bohn_Hall_') and o is not base:
        o['tl_hidden']=[int(o.hide_render),int(o.hide_viewport)]; o.hide_render=True; o.hide_viewport=True; hid+=1
print('TL hid',hid,'tk level masses; z0g',round(z0g,2),'floor',FL)
def ccw(p):
    a=sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
    return p if a>0 else p[::-1]
def mass(name,poly,zb,z1,par=0.5,blank=4.5):
    poly=ccw([tuple(p[:2]) for p in poly]); bm=bmesh.new()
    vs=[bm.verts.new((x,y,zb)) for x,y in poly]; f=bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=[f]); top=[g for g in r['geom'] if isinstance(g,bmesh.types.BMFace)][0]
    for v in top.verts: v.co.z=z1
    bmesh.ops.reverse_faces(bm,faces=[f])
    bmesh.ops.inset_region(bm,faces=[top],thickness=0.3,depth=0)
    for v in top.verts: v.co.z=z1-par
    bm.normal_update(); me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(BM); me.materials.append(RM)
    for k,t in (('ti_dir','FLOAT_VECTOR'),('ti_floor','FLOAT'),('ti_z0','FLOAT'),('ti_z1','FLOAT')): me.attributes.new(k,t,'FACE')
    V=me.vertices; DIRS=[]; MI=[]; Z1=[]; ne=len(poly); ED=[]
    for i in range(ne):
        a=poly[i]; b=poly[(i+1)%ne]; ED.append((math.atan2(b[1]-a[1],b[0]-a[0]),math.hypot(b[0]-a[0],b[1]-a[1]),((a[0]+b[0])/2,(a[1]+b[1])/2)))
    rid=[0]*ne
    for i in range(1,ne):
        dd=abs((ED[i][0]-ED[i-1][0]+math.pi)%(2*math.pi)-math.pi); rid[i]=rid[i-1]+(1 if dd>math.radians(20) else 0)
    if ne>1 and abs((ED[0][0]-ED[-1][0]+math.pi)%(2*math.pi)-math.pi)<=math.radians(20):
        last=rid[-1]; rid=[0 if r==last else r for r in rid]
    RL={}
    for i in range(ne): RL[rid[i]]=RL.get(rid[i],0)+ED[i][1]
    def runlen(cx,cy):
        i=min(range(ne),key=lambda k:(ED[k][2][0]-cx)**2+(ED[k][2][1]-cy)**2); return RL[rid[i]]
    nb=0
    for p in me.polygons:
        best=(0,(1,0))
        for i in range(len(p.vertices)):
            a=V[p.vertices[i]].co; c=V[p.vertices[(i+1)%len(p.vertices)]].co; dx,dy=c.x-a.x,c.y-a.y; l=math.hypot(dx,dy)
            if l>best[0]: best=(l,(dx/l,dy/l))
        bl=abs(p.normal.z)<0.5 and runlen(p.center.x,p.center.y)<blank; nb+=bl
        Z1.append(z0g if bl else z1)
        DIRS.extend((best[1][0],best[1][1],0)); MI.append(1 if (p.normal.z>0.9 and p.center.z<z1-0.3) else 0)
    n=len(me.polygons)
    me.attributes['ti_dir'].data.foreach_set('vector',DIRS); me.attributes['ti_floor'].data.foreach_set('value',[FL]*n)
    me.attributes['ti_z0'].data.foreach_set('value',[z0g]*n); me.attributes['ti_z1'].data.foreach_set('value',Z1)
    me.polygons.foreach_set('material_index',MI)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['tl_obj']=1
    o['UNVERIFIED']='OSM 232853538 + 2017 NJ LiDAR DSM levels, orthogonalised to the OSM wall axes (tl); windows/blank walls approximated'
    print('TL mass',name,'verts',ne,'walls',sum(1 for p in me.polygons if abs(p.normal.z)<0.5),'blank',nb)
    return o
E=json.load(open('data/tl/bohn_levels_rect.json'))
prev_top=E['base_top']; made=0
for L in E['levels']:
    for i,(pp,top) in enumerate(zip(L['polys'],L['tops'])):
        par=1.1 if L['name']=='PH' else 0.5
        mass('TL_Bohn_Hall_%s_%d_rect_UNVERIFIED'%(L['name'],i),pp,prev_top-0.6,top,par,blank=(999 if L['name']=='PH' else 4.5)); made+=1
    prev_top=max(L['tops'])
print('TL applied',made,'masses; objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
