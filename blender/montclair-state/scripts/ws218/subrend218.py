# ws212: subrend208 + KEEPALL=1 (all modifiers stay ON for every appended object = full-terrain subset render)
# ws212 default: terrain GN (band_to_DTM/cut/clamp/patch/regrid...) kept ON so subset renders show true terrain; NOTERRAIN=1 = old all-off behaviour.
# ws208: subrend206 + KEEPMOD (space list of objects whose modifiers stay ON, e.g. GN-draped walks/roads/terrain)
# ws205 low-memory subset render: append only objects whose bbox meets CULL (from bbox205.json) + GOLDEN light + world,
# all modifiers off (same as the ws189+ cut renders), optional CHAIN fixes applied to the appended objects, then cutrend189.
import bpy, os, json
S='/workspace/nj-scenes/montclair-state/scripts/'
FILE=os.environ['FILE']
BB=json.load(open(S+'ws205/bbox205.json'))
cx0,cx1,cy0,cy1=map(float,os.environ['CULL'].split(','))
HIDE=(('BD_farfield',) if os.environ.get('SKIRT')=='1' else ('Context_skirt','BD_farfield'))+tuple(os.environ.get('HIDEX','').split())
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,cols) in BB.items() if t in ('MESH','EMPTY','CURVE') and not hr and not n.startswith(HIDE) and not (x1<cx0 or x0>cx1 or y1<cy0 or y0>cy1)]
want+= [n for n,v in BB.items() if v[0]=='LIGHT' and n.endswith('GOLDEN')]
want+= os.environ.get('EXTRA','').split()
with bpy.data.libraries.load(FILE) as (a,b):
    have=set(a.objects); b.objects=[n for n in want if n in have]; b.worlds=[w for w in a.worlds if w=='WP2_World_GOLDEN']
KEEP=set(os.environ.get('KEEPMOD','').split()); KEEPALL=os.environ.get('KEEPALL')=='1'
import re; TERR=os.environ.get('NOTERRAIN')!='1'; TRX=re.compile(r'band_to_DTM|terrain|_cut|clamp|LiDAR_patch|regrid|seam_ramp|edge_grade|hump',re.I)
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    sc.collection.objects.link(o)
    if KEEPALL or o.name in KEEP: continue
    for m in o.modifiers:
        # ws212 FIX: terrain re-snap/cut/clamp GN stay ON by default (without them the raw LiDAR mesh
        # bulges over College Ave / the Red Hawk deck edge and the lots read as pits). skirt_under stays off (memory).
        if TERR and m.type=='NODES' and TRX.search(m.name) and 'skirt' not in m.name.lower(): continue
        m.show_viewport=False; m.show_render=False
print('SUB205 appended',len(b.objects),'terrainGN',TERR,sum(1 for o in b.objects if o for m in o.modifiers if m.show_render),flush=True)
for f in os.environ.get('CHAIN','').split(): exec(open(S+f).read())
for o in sc.objects:
    if o.name.startswith(('WS205_','WS206_')):
        for m in o.modifiers: m.show_render=False
if os.environ.get('SKIRT')=='1' and 'HIDE' not in os.environ: os.environ['HIDE']='BD_farfield'  # keep the context ground visible through cutrend189 too (Codex P2 on PR #10)
exec(open(S+'ws189/cutrend189.py').read())
