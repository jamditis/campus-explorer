# ws91: restore listed objects' mesh data from a backup blend (env SRC, NAMES comma list of object-name prefixes); loads by mesh datablock name
import bpy,os
SRC=os.environ['SRC']; PRE=[p for p in os.environ['NAMES'].split(',') if p]
tg=[o for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(p) for p in PRE)]
mn={o.data.name:o for o in tg}
for o in tg: o.data.name=o.data.name[:40]+'_ws91old'
with bpy.data.libraries.load(SRC,link=False) as (fr,to):
    to.meshes=[n for n in fr.meshes if n in mn]
for m in to.meshes:
    o=[ob for k,ob in mn.items() if k==m.name]
    if not o: print('R91 skip',m.name); continue
    o=o[0]; old=o.data; o.data=m; print('R91 restored',o.name,len(m.vertices))
    if old.users==0: bpy.data.meshes.remove(old)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('R91 SAVED')
