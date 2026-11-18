"""uh probe2: curl corner + W sawtooth + apron outline detail."""
import bpy, bmesh, json, math
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state/data/uh/'
dg=bpy.context.evaluated_depsgraph_get()

def caster(n):
    o=bpy.data.objects.get(n)
    if not o: return lambda x,y:(None,None)
    e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
    d=(iw.to_3x3()@Vector((0,0,-1))).normalized()
    def f(x,y):
        r=e.ray_cast(iw@Vector((x,y,400)),d)
        return ((mw@r[1]).z,r[3]) if r[0] else (None,None)
    return f
UG=caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA=caster('SA_ground_lower_patch_UNVERIFIED')
DT=caster('Terrain_LiDAR_DTM_1m')

# --- curl: QXP top verts near y=246, find local peaks ---
o=bpy.data.objects['QXP_pedestrian_area_313024781_paving_UNVERIFIED']
mw=o.matrix_world; me=o.data
# column tops
cols={}
for v in me.vertices:
    p=mw@v.co
    if -70<p.x<-30 and 243<p.y<252:
        k=(round(p.x/0.25), round(p.y/0.25))
        cols[k]=max(cols.get(k,-1e9), p.z)
# for each top vert, compare to 8-neighbour column max
tops=[]
for v in me.vertices:
    p=mw@v.co
    if not (-70<p.x<-30 and 243<p.y<252): continue
    k=(round(p.x/0.25), round(p.y/0.25))
    if abs(p.z - cols[k])>1e-4: continue  # not a top
    neigh=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if dx==0 and dy==0: continue
            kk=(k[0]+dx,k[1]+dy)
            if kk in cols: neigh.append(cols[kk])
    if not neigh: continue
    med=sorted(neigh)[len(neigh)//2]
    tops.append((v.index,p.x,p.y,p.z,med,p.z-med))
tops.sort(key=lambda t:-t[5])
print('=== QXP top curl outliers (above neighbour median) ===')
for t in tops[:25]:
    print('CURL',t)

# QY same
o2=bpy.data.objects.get('QY_plaza_rim_band_313024781_UNVERIFIED')
if o2:
    mw2=o2.matrix_world; me2=o2.data
    cols2={}
    for v in me2.vertices:
        p=mw2@v.co
        if -70<p.x<-30 and 243<p.y<252:
            k=(round(p.x/0.15),round(p.y/0.15)); cols2[k]=max(cols2.get(k,-1e9),p.z)
    tops2=[]
    for v in me2.vertices:
        p=mw2@v.co
        if not (-70<p.x<-30 and 243<p.y<252): continue
        k=(round(p.x/0.15),round(p.y/0.15))
        if abs(p.z-cols2.get(k,-1e9))>1e-4: continue
        neigh=[cols2[kk] for dx in (-1,0,1) for dy in (-1,0,1) if not(dx==0 and dy==0) and (kk:=(k[0]+dx,k[1]+dy)) in cols2]
        if not neigh: continue
        med=sorted(neigh)[len(neigh)//2]
        tops2.append((v.index,p.x,p.y,p.z,med,p.z-med))
    tops2.sort(key=lambda t:-t[5])
    print('=== QY top curl outliers ===')
    for t in tops2[:20]: print('CURLy',t)

# --- W apron boundary verts ALL (no x filter) ---
print('=== apron boundary xy ===')
ap=bpy.data.objects['TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)']
mw=ap.matrix_world; me=ap.data
eu={}
for p in me.polygons:
    for ek in p.edge_keys: eu[ek]=eu.get(ek,0)+1
bvi=set()
for ek,c in eu.items():
    if c==1: bvi.update(ek)
# group by y bins, find min-x (outer/west) and max-x (inner/east toward building)
from collections import defaultdict
yb=defaultdict(list)
for vi in bvi:
    p=mw@me.vertices[vi].co
    yb[round(p.y*4)/4].append((vi,p.x,p.y,p.z))
print('apron y-bins',len(yb),'total bverts',len(bvi))
# west outline (min x per y) — look for sawtooth
west=[]
for y in sorted(yb):
    pts=yb[y]; pts.sort(key=lambda t:t[1])
    west.append(pts[0])  # min x
print('west outline n',len(west))
for i,t in enumerate(west):
    if i==0: continue
    dx=t[1]-west[i-1][1]; dy=t[2]-west[i-1][2]
    if abs(dx)>0.12:
        print('APWJUMP',west[i-1],'->',t,'dx',dx,'dy',dy)
# also print first/last few
print('west head',west[:8]); print('west tail',west[-8:])

# east outline (max x) — against building / right of stair
east=[]
for y in sorted(yb):
    pts=yb[y]; pts.sort(key=lambda t:t[1]); east.append(pts[-1])
print('east outline n',len(east))
for i,t in enumerate(east):
    if i==0: continue
    dx=t[1]-east[i-1][1]
    if abs(dx)>0.08:
        print('APEJUMP',east[i-1],'->',t,'dx',dx)

# steps W door geometry — find "right of stair" paving
print('=== W steps bbox + nearby Footpaths ===')
st=bpy.data.objects['TY Partridge entrance steps+landings (UNVERIFIED)']
smw=st.matrix_world
xs,ys,zs=[],[],[]
for v in st.data.vertices:
    p=smw@v.co
    if p.x<-95:  # W door area
        xs.append(p.x); ys.append(p.y); zs.append(p.z)
print('W steps',min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
# Footpaths verts near stair south (y < min stairs) and east (higher x)
fp=bpy.data.objects['Footpaths_OSM']
fmw=fp.matrix_world
cands=[]
for v in fp.data.vertices:
    p=fmw@v.co
    if -105<p.x<-96 and 245<p.y<255:
        cands.append((v.index,p.x,p.y,p.z))
print('Footpaths near W',len(cands))
if cands:
    print('fp x range',min(t[1] for t in cands),max(t[1] for t in cands))
    print('fp y range',min(t[2] for t in cands),max(t[2] for t in cands))

# walk 404 end edge — the cut face at XCUT
w=bpy.data.objects['TY_footway_313026404_to_Partridge_UNVERIFIED']
wmw=w.matrix_world
eu={}
for p in w.data.polygons:
    for ek in p.edge_keys: eu[ek]=eu.get(ek,0)+1
ends=[]
for ek,c in eu.items():
    if c!=1: continue
    for vi in ek:
        p=wmw@w.data.vertices[vi].co
        if p.x>-103 and p.x<-101.5:
            ends.append((vi,p.x,p.y,p.z))
ends.sort(key=lambda t:t[2])
print('404 end-edge verts',len(ends))
for t in ends: print('404E',t)

# apron mesh face count / segment structure
print('apron verts',len(ap.data.vertices),'polys',len(ap.data.polygons))
# sample apron top verts sorted by y, look at x of outermost
tops_ap=[]
cols_a={}
for v in ap.data.vertices:
    p=mw@v.co; k=(round(p.y*5),); cols_a.setdefault(round(p.y*2)/2, []).append((v.index,p.x,p.y,p.z))
# for each y, the west-most top (high z)
for y in sorted(cols_a):
    pts=cols_a[y]
    zmax=max(t[3] for t in pts)
    westpts=[t for t in pts if abs(t[3]-zmax)<0.02]
    westpts.sort(key=lambda t:t[1])
    tops_ap.append(westpts[0])
print('apron west-top outline')
for i,t in enumerate(tops_ap):
    if i and abs(t[1]-tops_ap[i-1][1])>0.15:
        print('  SAW',tops_ap[i-1],'->',t)
    elif i%3==0:
        print('  ',t)

json.dump({'curl_qxp':[list(t) for t in tops[:30]], 'curl_qy':[list(t) for t in tops2[:20]],
           'apron_west':[list(t) for t in west], 'w404_end':[list(t) for t in ends]},
          open(D+'probe2.json','w'), indent=1)
print('WROTE probe2')
