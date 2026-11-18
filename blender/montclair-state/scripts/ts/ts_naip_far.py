import urllib.parse,urllib.request,io,os,time
from PIL import Image
os.chdir('/workspace/nj-scenes/montclair-state/data/ts')
x0,y0,x1,y1=570958.75,679285.0,652979.5833333334,749822.9166666666
W,H=2500,2150; nx,ny=4,2
out=Image.new('RGB',(W,H)); tw,th=W//nx,H//ny; dx=(x1-x0)/nx; dy=(y1-y0)/ny
for i in range(nx):
  for j in range(ny):
    fn=f'far_t{i}{j}.jpg'; e0=x0+i*dx; n1=y1-j*dy
    q=dict(bbox=f"{e0},{n1-dy},{e0+dx},{n1}",bboxSR=6527,imageSR=6527,size=f"{tw},{th}",format="jpg",compressionQuality=90,f="image",bandIds="0,1,2",interpolation="RSP_BilinearInterpolation")
    url="https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage?"+urllib.parse.urlencode(q)
    for a in range(5):
      if os.path.exists(fn) and os.path.getsize(fn)>30000: break
      try: d=urllib.request.urlopen(url,timeout=170).read(); open(fn,'wb').write(d); print('got',fn,len(d),flush=True)
      except Exception as e: print('retry',fn,e,flush=True); time.sleep(5)
    out.paste(Image.open(fn).convert('RGB'),(i*tw,j*th))
out.save('naip_far.jpg',quality=90); print('FAR_DONE',flush=True)
