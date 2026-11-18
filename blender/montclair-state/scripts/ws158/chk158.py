import bpy,sys,json
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
J=json.load(open('/workspace/nj-scenes/montclair-state/prep/ws158_PanzerE/panzer158.json'))
def inside(x,y,poly):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
o=J['outer']
for ob in bpy.data.objects:
    if ob.type=='MESH' and -294<ob.location.x<-233 and -243<ob.location.y<-136 and not ob.name.startswith('WS158'):
        print('CHK',ob.name,[round(v,1) for v in ob.location],'inside',inside(ob.location.x,ob.location.y,o), [round(v,1) for v in ob.dimensions])
