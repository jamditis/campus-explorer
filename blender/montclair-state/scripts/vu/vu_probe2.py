"""Deeper probe: block_base / spandrel / TI / surround geometry vs door glass spans."""
import bpy, bmesh, json
from mathutils import Vector

def wv(o):
    mw=o.matrix_world; return [mw@v.co for v in o.data.vertices]

def door_frame(k):
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
    gv=wv(G); gc=sum(gv,Vector())/len(gv)
    best=None
    for i in range(len(gv)):
        for j in range(i+1,len(gv)):
            d=gv[j]-gv[i]; d.z=0
            if best is None or d.length>best.length: best=d
    u=best.normalized(); n=Vector((-u.y,u.x,0))
    BC=Vector((141.6,450.4,0))
    if (gc-BC).to_2d().dot(n.to_2d())<0: n=-n
    half_w=max(abs((v-gc).dot(u)) for v in gv)
    zlo=min(v.z for v in gv); zhi=max(v.z for v in gv)
    return G,gc,u,n,half_w,zlo,zhi,gv

report={}
# list ALL Blanton mesh objects with vert counts and z ranges
blobs=[]
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    if o.type!='MESH' or 'Blanton' not in o.name and 'blanton' not in o.name: continue
    vs=wv(o)
    if not vs: continue
    blobs.append(dict(name=o.name, n=len(vs), z=[round(min(v.z for v in vs),2), round(max(v.z for v in vs),2)],
                      hide=o.hide_get(), hide_r=o.hide_render,
                      mats=[m.name if m else None for m in o.data.materials][:3]))
report['all_blanton']=blobs

for k in range(3):
    G,gc,u,n,half_w,zlo,zhi,gv=door_frame(k)
    entry=dict(k=k, gc=[round(x,3) for x in gc], half_w=round(half_w,3), z=[round(zlo,3),round(zhi,3)],
               glass_nverts=len(gv), objects={})
    # check specific objects: count verts that fall inside door u-span and within 0.6m of glass plane (n)
    names=[
        'TN_Blanton_block_base_UNVERIFIED',
        'TN_Blanton_spandrel_bands_UNVERIFIED',
        'TN_Blanton_piers_UNVERIFIED',
        'TU_Blanton_entrance_%d_surround_UNVERIFIED'%k,
        'TU_Blanton_entrance_%d_landing_UNVERIFIED'%k,
        'TJ_Blanton_entrance_%d_frame_UNVERIFIED'%k,
    ]
    # also any TI lower that intersects
    for o in bpy.data.objects:
        if o.name.startswith('TI_Blanton') and o.type=='MESH':
            names.append(o.name)
    for nm in names:
        o=bpy.data.objects.get(nm)
        if not o: continue
        vs=wv(o)
        # classify verts relative to door
        in_door_u=[]; crossing_low=[]
        for v in vs:
            d=v-gc
            du=d.dot(u); dn=d.dot(n)
            if abs(du)<=half_w+0.15 and abs(dn)<=1.2:
                in_door_u.append(v)
                # low band: within glass z and near glass plane
                if zlo-0.3 <= v.z <= zlo+1.2 and abs(dn)<=0.35:
                    crossing_low.append(v)
        # face centers for block_base / spandrel
        face_cross=0
        if o.data.polygons and nm.startswith('TN_'):
            mw=o.matrix_world
            for p in o.data.polygons:
                c=mw@p.center; d=c-gc
                if abs(d.dot(u))<=half_w+0.1 and abs(d.dot(n))<=0.5 and zlo-0.2<=c.z<=zhi+0.2:
                    face_cross+=1
        entry['objects'][nm]=dict(
            nverts=len(vs),
            in_door_span=len(in_door_u),
            crossing_low_band=len(crossing_low),
            face_centers_in_glass=face_cross,
            low_z_samples=[[round(v.x,2),round(v.y,2),round(v.z,2)] for v in crossing_low[:8]],
            span_z=[round(min(v.z for v in in_door_u),2), round(max(v.z for v in in_door_u),2)] if in_door_u else None,
        )
    report['door_%d'%k]=entry

# sample spandrel: how many separate z-levels?
SP=bpy.data.objects.get('TN_Blanton_spandrel_bands_UNVERIFIED')
if SP:
    zs=sorted(set(round((SP.matrix_world@v.co).z,2) for v in SP.data.vertices))
    # cluster
    clusters=[]; cur=[]
    for z in zs:
        if not cur or z-cur[-1]<0.4: cur.append(z)
        else: clusters.append(cur); cur=[z]
    if cur: clusters.append(cur)
    report['spandrel_z_clusters']=[[c[0],c[-1],len(c)] for c in clusters]

BB=bpy.data.objects.get('TN_Blanton_block_base_UNVERIFIED')
if BB:
    zs=sorted(set(round((BB.matrix_world@v.co).z,2) for v in BB.data.vertices))
    report['block_base_z']=[zs[0],zs[-1],len(zs)]
    report['block_base_mesh']=BB.data.name
    report['has_tu_orig']=('tu_orig_mesh' in BB)

json.dump(report, open('/workspace/nj-scenes/montclair-state/data/vu/probe2.json','w'), indent=1)
print('spandrel clusters', report.get('spandrel_z_clusters'))
print('block_base', report.get('block_base_z'), report.get('block_base_mesh'), report.get('has_tu_orig'))
for k in range(3):
    e=report['door_%d'%k]
    print('=== DOOR',k,'gc',e['gc'],'z',e['z'],'half_w',e['half_w'])
    for nm,info in e['objects'].items():
        if info['in_door_span'] or info['crossing_low_band'] or info['face_centers_in_glass']:
            print(' ',nm, info)
