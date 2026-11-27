# ws258 read-only (PARALLEL stream; main not opened for edit): UNIFY #2 Footpaths dog-leg E of the College Ave S leg.
# library-loads base meshes only (no modifier evaluation) and plots walk/paving footprints in XY.
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, re, json
MS='/workspace/nj-scenes/montclair-state/'
BOX=(-265,-180,-235,-120)
pat=re.compile(r'^(Footpaths|Roads_OSM|WS(2[7-9]|3\d|4\d|7\d|8\d|9\d|1[0-2]\d)_)')
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b):
    b.objects=[n for n in a.objects if pat.match(n)]
print('P258A loaded',len(b.objects))
out=[]
for o in b.objects:
    if not o or o.type!='MESH': continue
    W=o.matrix_world; vs=[W@v.co for v in o.data.vertices]
    polys=[]
    for p in o.data.polygons:
        c=[vs[i] for i in p.vertices]
        cx=sum(v.x for v in c)/len(c); cy=sum(v.y for v in c)/len(c)
        if BOX[0]<cx<BOX[1] and BOX[2]<cy<BOX[3]:
            polys.append([[round(v.x,2),round(v.y,2),round(v.z,2)] for v in c])
    if polys:
        out.append({'name':o.name,'hide_render':o.hide_render,'mods':[m.name for m in o.modifiers],'mats':[m.name for m in o.data.materials if m][:4],'polys':polys})
        print('P258A',o.name[:70],'faces',len(polys),'hide',o.hide_render,'mods',[m.name for m in o.modifiers][:4])
json.dump(out,open(MS+'scripts/ws258/probe258a.json','w'))
with open('/proc/self/status') as f:
    for l in f:
        if l.startswith('VmHWM'): print('P258A',l.strip())
os._exit(0)
