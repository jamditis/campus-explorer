# read-only inventory of Dickson / Calcia / Feliciano related objects in the open blend (no save)
import bpy, json, sys, os
KEYS={'dickson':('dickson',),'calcia':('calcia',),'feliciano':('feliciano','business','fsb','school of business')}
out={}
for b,ks in KEYS.items():
    rows=[]
    for o in bpy.data.objects:
        n=o.name.lower(); cn=[c.name for c in o.users_collection]
        if any(k in n for k in ks) or any(any(k in c.lower() for k in ks) for c in cn):
            r={'name':o.name,'type':o.type,'colls':cn,'hide_render':o.hide_render,'loc':[round(v,2) for v in o.matrix_world.translation]}
            if o.type=='MESH': r.update(verts=len(o.data.vertices),faces=len(o.data.polygons),mats=[s.material.name if s.material else None for s in o.material_slots][:6],mods=[m.name for m in o.modifiers],props={k:str(o[k])[:80] for k in o.keys() if not k.startswith('_')})
            rows.append(r)
    out[b]=rows
src=os.path.basename(bpy.data.filepath)
p=sys.argv[sys.argv.index('--')+1]
json.dump({'blend':src,'buildings':out},open(p,'w'),indent=1)
for b,rows in out.items(): print('INV',src,b,len(rows),'objects;',sum(1 for r in rows if 'win' in r['name'].lower()),'window-named')
