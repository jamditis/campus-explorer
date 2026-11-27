# ws257 read-only: dump top-down polygons of the paving pieces + the ws257 joint strips (sanity plot with plotxy257.py)
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json
F=os.environ.get('F','/workspace/nj-scenes/montclair-state/montclair_state_ws257a.blend')
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS252','WS253','WS254','WS255','WS257')) and 'Lamp' not in n]
OUT=[]
for o in b.objects:
    M=o.matrix_world; vs=[tuple((M@v.co)[:2]) for v in o.data.vertices]
    OUT.append([o.name,[[vs[i] for i in p.vertices] for p in o.data.polygons]])
json.dump(OUT,open('/tmp/plot257.json','w')); print('PLOT257 ok')
os._exit(0)
