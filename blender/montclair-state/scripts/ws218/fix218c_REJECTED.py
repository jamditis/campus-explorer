# ws218 W38 remainder: the WS69 College Ave gap-strip curb ends as a 15-17 cm stub (pale end face = the "lip wedge") right at
# the College Ave crosswalk where the Kasser landing (WS72) and the gap asphalt (WS67) already meet flush (probe218e:
# curb top 125.37 vs landing 125.29 / asphalt 125.20 at x -254.5, y -53.5). A curb at a marked crosswalk is a depressed
# (flush) curb with a transition (NJ/ADA practice; exact ramp length UNVERIFIED). Taper the curb TOP verts within 1.5 m of
# the stub end down to the adjacent paving + 1 cm at the end, full height beyond; paving untouched (nothing raised or
# lowered on paving surfaces; curb-only geometry change).
import bpy, json, math
G=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws218/w38_grid218.json'))
G={tuple(map(float,k.split(','))):v for k,v in G.items()}
o=bpy.data.objects['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']; M=o.matrix_world; Mi=M.inverted()
E=(-254.75,-53.35); R=1.5
def ground(x,y):
    c=[v[1] for (gx,gy),v in G.items() if abs(gx-x)<=0.75 and abs(gy-y)<=0.75]
    return min(c) if c else None
n=0
for v in o.data.vertices:
    w=M@v.co; d=math.hypot(w.x-E[0],w.y-E[1])
    if d>R: continue
    gz=ground(w.x,w.y)
    if gz is None or w.z<gz+0.02: continue   # only top verts standing above the paving
    t=d/R; nz=gz+0.01+(w.z-gz-0.01)*t
    if nz<w.z:
        w.z=nz; v.co=Mi@w; n+=1
o.data.update()
print('F218C curb top verts tapered',n,'mods',[m.type for m in o.modifiers],flush=True)
