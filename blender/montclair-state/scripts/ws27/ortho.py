import sys,urllib.parse,urllib.request
sys.path.insert(0,'/workspace/nj-scenes/blender_pylib_proj')
from pyproj import Transformer
FT=1200/3937; tr=Transformer.from_crs("EPSG:4326","EPSG:6527",always_xy=True)
c_e,c_n=tr.transform(-74.19720,40.86000); E0,N0=round(c_e,-1),round(c_n,-1)
x0,x1,y0,y1=-345,-185,-180,-20
bb=f"{E0+x0/FT},{N0+y0/FT},{E0+x1/FT},{N0+y1/FT}"
for nm,url in [('nj2020','https://img.nj.gov/imagerysvc/rest/services/Imagery_2020/ImageServer/exportImage'),('naip','https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage')]:
  q=dict(bbox=bb,bboxSR=6527,imageSR=6527,size="1600,1600",format="jpg",f="image")
  if nm=='naip': q['bandIds']='0,1,2'
  try:
    d=urllib.request.urlopen(url+'?'+urllib.parse.urlencode(q),timeout=120).read(); open(f'data/ws27/{nm}.jpg','wb').write(d); print(nm,len(d))
  except Exception as e: print(nm,'ERR',e)
