# ws205 low-memory subset render: append only objects whose bbox meets CULL (from bbox205.json) + GOLDEN light + world,
# all modifiers off (same as the ws189+ cut renders), optional CHAIN fixes applied to the appended objects, then cutrend189.
import bpy, os, json
S='/workspace/nj-scenes/montclair-state/scripts/'
FILE=os.environ['FILE']
BB=json.load(open(S+'ws205/bbox205.json'))
cx0,cx1,cy0,cy1=map(float,os.environ['CULL'].split(','))
HIDE=('Context_skirt','BD_farfield')
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,cols) in BB.items() if t in ('MESH','EMPTY','CURVE') and not hr and not n.startswith(HIDE) and not (x1<cx0 or x0>cx1 or y1<cy0 or y0>cy1)]
want+= [n for n,v in BB.items() if v[0]=='LIGHT' and n.endswith('GOLDEN')]
want+= os.environ.get('EXTRA','').split()
with bpy.data.libraries.load(FILE) as (a,b):
    have=set(a.objects); b.objects=[n for n in want if n in have]; b.worlds=[w for w in a.worlds if w=='WP2_World_GOLDEN']
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    sc.collection.objects.link(o)
    for m in o.modifiers: m.show_viewport=False; m.show_render=False
print('SUB205 appended',len(b.objects),flush=True)
for f in os.environ.get('CHAIN','').split(): exec(open(S+f).read())
for o in sc.objects:
    if o.name.startswith('WS205_'):
        for m in o.modifiers: m.show_render=False
exec(open(S+'ws189/cutrend189.py').read())
