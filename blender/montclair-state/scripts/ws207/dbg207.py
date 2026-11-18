for x in (-219.0,-218.0,-217.0):
  for y in np.arange(-83.6,-82.4,0.1):
    r=[]
    for n in names:
      h=T[n].ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); r.append('%s=%s'%(n[:5],'%.3f'%h[0].z if h[0] else '--'))
    print('D207 %.1f %.1f'%(x,y),' '.join(r),'zs=%.3f w=%.2f'%(zs(x,y),wgt(x,y)))
