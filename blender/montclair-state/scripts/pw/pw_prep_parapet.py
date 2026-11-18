# pw prep (read-only): Dickson north-wing wall-top edges vs roof heights, for replacing the pv_pent stop-gap with a real parapet.
import bpy, json
w=bpy.data.objects['Dickson Hall walls']; mw=w.matrix_world; me=w.data
E2=[]
for e in me.edges:
    a=mw@me.vertices[e.vertices[0]].co; b=mw@me.vertices[e.vertices[1]].co
    if min(a.z,b.z)>146.0 and (a-b).length>0.5: E2.append(dict(a=[round(x,3) for x in a],b=[round(x,3) for x in b],dz=round(abs(a.z-b.z),3)))
rp=bpy.data.objects.get('Roof_pent'); RP=[]
if rp:
    m=rp.matrix_world
    for p in rp.data.polygons:
        if 30<=p.index<=35: RP.append(dict(i=p.index,v=[[round(x,3) for x in m@rp.data.vertices[k].co] for k in p.vertices],mi=p.material_index))
roofs=[]
for o in bpy.data.objects:
    if o.type=='MESH' and 'dickson' in o.name.lower() and 'roof' in o.name.lower():
        zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
        if zs: roofs.append(dict(name=o.name,zmin=round(min(zs),2),zmax=round(max(zs),2),nv=len(zs)))
json.dump(dict(note='pw prep, read-only; wall-top edges above z 146 (sloped = dz>0.3)',sloped=[x for x in E2 if x['dz']>0.3],level_count=sum(1 for x in E2 if x['dz']<=0.3),roof_pent_box=RP,dickson_roof_objects=roofs),open('data/pw/prep_dickson_north_parapet.json','w'),indent=1)
print('PREP sloped',sum(1 for x in E2 if x['dz']>0.3),'level',sum(1 for x in E2 if x['dz']<=0.3),'roofs',len(roofs))
