import bpy,os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
codes={}
def hit(x,y):
    z=128.0
    for _ in range(8):
        h,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)))
        if not h: return None
        if ob.hide_render or ob.name.startswith('Ground') : z=loc.z-0.001; continue
        return ob,loc.z
X0,X1,Y0,Y1,S=[float(s) for s in os.environ['GRID'].split(',')]
rows=[]
y=Y1
while y>=Y0-1e-6:
    row=[]; x=X0
    while x<=X1+1e-6:
        r=hit(x,y)
        if r:
            k=r[0].name[:22]
            if k not in codes: codes[k]=chr(65+len(codes))
            row.append(codes[k]+'%02d'%int(round((r[1]-125)*100)))
        else: row.append('---')
        x+=S
    print('P222 y%.2f '%y+' '.join(row)); y-=S
for k,v in codes.items(): print('P222 code',v,k)
