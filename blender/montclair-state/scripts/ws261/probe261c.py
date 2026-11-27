# ws261 probe (subset CHAIN, terrain GN on, crop259, exits before render): UNIFY #16 — old Footpaths_OSM N-S walk N of the WS112 brick
# link (x -237..-230, y -237..-224). Evaluated top object per 0.25 m cell + depth of any Footpaths_OSM hit below the top, and the
# Footpaths_OSM BASE faces whose centroid lies in the box (with the fraction of their area covered by designed paving).
import bpy, json
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,X1,Y0,Y1,R=-237.0,-230.0,-237.0,-224.0,0.25
tops={}; fp=[]; cells={}
x=X0
while x<X1:
    y=Y0
    while y<Y1:
        o0=Vector((x+R/2,y+R/2,200)); hs=[]
        for k in range(60):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if not nm.startswith(('T_','TREE','MID_canopy')): hs.append((nm,round(r[1].z,3)))
            if nm.startswith('Context_'): break
            o0=r[1]+Vector((0,0,-0.001))
        cells['%.2f,%.2f'%(x+R/2,y+R/2)]=hs[:4]
        if hs:
            tops[hs[0][0][:50]]=tops.get(hs[0][0][:50],0)+1
            f=[h for h in hs if h[0]=='Footpaths_OSM']
            if f: fp.append((round(x+R/2,2),round(y+R/2,2),hs[0][0][:30],round(hs[0][1]-f[0][1],3)))
        y+=R
    x+=R
o=bpy.data.objects['Footpaths_OSM']; W=o.matrix_world; base=[]
for p in o.data.polygons:
    c=W@p.center
    if X0<c.x<X1 and Y0<c.y<Y1: base.append({'i':p.index,'c':[round(c.x,3),round(c.y,3),round(c.z,3)],'a':round(p.area,3)})
json.dump({'tops':tops,'fp_hits':fp,'base':base,'cells':cells},open('/workspace/nj-scenes/montclair-state/scripts/ws261/eval261c.json','w'))
raise SystemExit
