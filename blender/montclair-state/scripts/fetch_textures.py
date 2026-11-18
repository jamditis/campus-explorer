"""Download CC0 PBR textures from ambientCG (CC0 1.0). Usage: python fetch_textures.py ID [ID...]; res 1K/2K via RES env."""
import os, sys, io, zipfile, urllib.request
RES = os.environ.get('RES', '1K')
out = os.path.join(os.path.dirname(__file__), '..', 'textures')
for aid in sys.argv[1:]:
    d = os.path.join(out, aid)
    if os.path.isdir(d) and os.listdir(d): print('have', aid); continue
    url = f'https://ambientcg.com/get?file={aid}_{RES}-JPG.zip'
    req = urllib.request.Request(url, headers={'User-Agent': 'nj-scenes/0.1'})
    try:
        data = urllib.request.urlopen(req, timeout=120).read()
        zipfile.ZipFile(io.BytesIO(data)).extractall(d)
        print('ok', aid, len(data), sorted(os.listdir(d)))
    except Exception as e:
        print('FAIL', aid, e)
