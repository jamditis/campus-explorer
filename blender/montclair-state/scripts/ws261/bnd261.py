import json,collections,sys
d=json.load(open(sys.argv[1]));T=d['top'];NX,NY=d['NX'],d['NY'];X0,Y0,R=d['X0'],d['Y0'],d['R']
pts=[]
for j in range(NY):
  for i in range(NX):
    a=T['%d,%d'%(i,j)]
    for di,dj in ((1,0),(0,1),(-1,0),(0,-1)):
      ii,jj=i+di,j+dj
      if not(0<=ii<NX and 0<=jj<NY): continue
      b=T['%d,%d'%(ii,jj)]
      if a and b and a[0].startswith('WS113') and b[0].startswith('Terrain'):
        pts.append((round(X0+(i+.5)*R,2),round(Y0+(j+.5)*R,2),round(b[1]-a[1],3)))
holes=sum(1 for v in T.values() if v is None or v[0].startswith('Context'))
print('holes',holes,'boundary cells',len(pts),'>3cm',sum(1 for p in pts if abs(p[2])>0.03),'>1.5cm',sum(1 for p in pts if abs(p[2])>0.015),'max |dz| %.3f'%max(abs(p[2]) for p in pts))
print(collections.Counter((v[0][:30] if v else None) for v in T.values()).most_common(6))
if len(sys.argv)>2: json.dump(pts,open(sys.argv[2],'w'))
