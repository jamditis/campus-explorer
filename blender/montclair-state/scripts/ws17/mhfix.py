"""ws17: pale grey lens on Morehead's west tile slope (seen from the Cole sign camera) = faces whose
ortho-sampled roofc colour is pale/grey so the shader reads membrane. Force tile (em_ringforce=1) on
pitched faces (normal z<0.95) with pale roofc. APPLY=1 saves."""
import bpy,os,colorsys
o=bpy.data.objects['Morehead Hall roof (LiDAR)']; me=o.data
rc=me.attributes['roofc']
cols=[tuple(rc.data[i].color[:3]) for i in range(len(me.vertices))]
def fc(p):
    cs=[cols[v] for v in p.vertices]; return tuple(sum(c[k] for c in cs)/len(cs) for k in range(3))
near=[];farv=[]
pale=[]
for p in me.polygons:
    if p.material_index!=0 or p.normal.z>0.95: continue
    c=fc(p); h,s,v=colorsys.rgb_to_hsv(*c)
    if abs(p.center.x+39)<1.5 and abs(p.center.y+55.5)<3 and p.center.z<145.8: near.append((s,v))
    else: farv.append((s,v))
    if s<float(os.environ.get('S','0.35')): pale.append(p.index)
import statistics as st
print('NEAR n',len(near),'sat',round(st.mean(x[0] for x in near),3),'val',round(st.mean(x[1] for x in near),3))
print('FAR n',len(farv),'sat',round(st.mean(x[0] for x in farv),3),'val',round(st.mean(x[1] for x in farv),3))
print('NEAR sat min/max',round(min(x[0] for x in near),3),round(max(x[0] for x in near),3))
print('pale pitched faces',len(pale))
at=me.attributes.get('em_ringforce'); print('existing em_ringforce',bool(at))
if os.environ.get('APPLY')=='1':
    at=at or me.attributes.new('em_ringforce','FLOAT','FACE')
    vals=[0.0]*len(me.polygons); at.data.foreach_get('value',vals)
    for i in pale: vals[i]=1.0
    at.data.foreach_set('value',vals); me.update()
    bpy.ops.wm.save_mainfile(); print('SAVED')
