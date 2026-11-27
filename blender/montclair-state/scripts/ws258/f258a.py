# ws258 DRAFT (parallel stream; NOT applied to main) — UNIFY #2 "Footpaths_OSM dog-leg E of the College Ave S leg".
# probe258a/cover258 (base meshes, library load): the old OSM walk junction (E-W arm meeting the N-S arm at ~(-221,-199)) still has
# 67 Footpaths_OSM faces (94.1 m2, x -226..-212, y -203..-183) and 100 % of their XY area lies under the designed pieces built later
# (WS116 plaza / N connector / mulch beds, WS117 stair + landing, WS119/WS120/WS124/WS126). It is residue: the same kind
# ws119/ws120/ws121 retired. Fix = delete exactly those faces (matched by centroid +-3 cm from cover258.json; abort on mismatch).
# Run in the merge208 chain (modifiers off; base-mesh only):
#   CHAIN="ws258/f258a.py" INF=$PWD/montclair_state.blend OUTN=montclair_state_wsNNNa.blend bash scripts/ws257/run257.sh  (grep tag F258A)
import bpy, bmesh, json
TAG='F258A'; MS='/workspace/nj-scenes/montclair-state/'
R=json.load(open(MS+'scripts/ws258/cover258.json'))
o=bpy.data.objects['Footpaths_OSM']; W=o.matrix_world
b=bmesh.new(); b.from_mesh(o.data); b.faces.ensure_lookup_table()
kill=[]
for f in b.faces:
    c=W@f.calc_center_median()
    if -232<c.x<-205 and -208<c.y<-178:
        for r in R:
            if abs(c.x-r['c'][0])<0.03 and abs(c.y-r['c'][1])<0.03: kill.append(f); break
print(TAG,'matched',len(kill),'of',len(R),flush=True)
if len(kill)!=len(R): raise SystemExit(TAG+' mismatch: main changed since ws258 probe; re-run probe258a + cover258')
n0=len(b.faces)
bmesh.ops.delete(b,geom=kill,context='FACES')
bmesh.ops.delete(b,geom=[v for v in b.verts if not v.link_faces],context='VERTS')
b.to_mesh(o.data); o.data.update(); b.free()
print(TAG,'Footpaths_OSM faces',n0,'->',len(o.data.polygons),flush=True)
