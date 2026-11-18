import urllib.parse,urllib.request,io,os,time,statistics
from PIL import Image
os.chdir('/workspace/nj-scenes/montclair-state/data/ts')
E0,N0=575880.0,738340.0; h=2000*3937/1200
out=Image.new('RGB',(4096,4096))
for i in range(2):
  for j in range(2):
    fn=f'naip_t{i}{j}.jpg'
    e0=E0-h+i*h; n1=N0+h-j*h
    bb=f"{e0},{n1-h},{e0+h},{n1}"
    q=dict(bbox=bb,bboxSR=6527,imageSR=6527,size="2048,2048",format="jpg",compressionQuality=92,f="image",bandIds="0,1,2",interpolation="RSP_BilinearInterpolation")
    url="https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage?"+urllib.parse.urlencode(q)
    for a in range(6):
      if os.path.exists(fn) and os.path.getsize(fn)>100000: break
      try:
        d=urllib.request.urlopen(url,timeout=170).read(); open(fn,'wb').write(d); print('got',fn,len(d),flush=True)
      except Exception as e: print('retry',fn,e,flush=True); time.sleep(5)
    out.paste(Image.open(fn).convert('RGB'),(i*2048,j*2048))
out.save('naip_skirt_4k.jpg',quality=90)
s=out.resize((256,256)); px=list(s.getdata()); print('mean',[round(statistics.mean(p[k] for p in px)) for k in range(3)])
o=Image.open('../skirt_ortho.jpg').convert('RGB').resize((256,256)); px=list(o.getdata()); print('old mean',[round(statistics.mean(p[k] for p in px)) for k in range(3)])
print('NAIP_DONE')
