# Step 3 (one Blender process per chunk): append the chunk's objects from the main .blend,
# keep modifiers (except skirt_under*), flatten materials to web-safe PBR (flat average colours;
# only CC0 ambientCG / our own authored textures kept, NEVER ortho/aerial/photo images),
# thin tree leaf cards, export GLB.  env: FILE CHUNK OUT
import json
import os
import random
import re

import bmesh
import bpy
import numpy as np
from mathutils import Vector

W = os.environ.get("WORK", "/workspace/nj-scenes/web/build/main") + "/"
FILE = os.environ.get("FILE", "/workspace/nj-scenes/montclair-state/montclair_state.blend")
CH = os.environ["CHUNK"]
OUT = os.environ["OUT"]
names = json.load(open(W + "chunks.json"))[CH]["objects"]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(FILE) as (a, b):
    have = set(a.objects)
    b.objects = [n for n in names if n in have]
sc = bpy.context.scene
for o in b.objects:
    if o is None:
        continue
    sc.collection.objects.link(o)
    for m in o.modifiers:
        # skirt_under GN pushes the far-field skirt below the campus terrain: keep it for the
        # dedicated 'skirt' chunk, drop it elsewhere (memory)
        if "skirt" in m.name.lower() and m.type == "NODES" and CH != "skirt":
            m.show_render = m.show_viewport = False
        else:
            m.show_viewport = m.show_render
print("WEB appended", len(b.objects), flush=True)

# ---------- materials ----------
ALLOW = re.compile(
    r"(^|/)([A-Z][A-Za-z]+\d{3}[A-Z]?_\dK-(JPG|PNG)_(Color|Opacity)\.(jpg|png))$|SweetgumStar_(Color|Opacity)|TulipPoplar_(Color|Opacity)"
)
DENY = re.compile(
    r"ortho|naip|aerial|photo|joe|skirt|ground_classes|paving_mask|walk_panel_tone|_far|mask|\.exr",
    re.I,
)
cache_p = W + "img_avg.json"
AV = json.load(open(cache_p)) if os.path.exists(cache_p) else {}


def img_ok(im):
    p = bpy.path.abspath(im.filepath, library=im.library)
    return bool(ALLOW.search(p)) and not DENY.search(p)


def img_avg(im):
    k = im.name_full + "|" + im.filepath
    if k not in AV:
        try:
            px = np.array(im.pixels[:], dtype=np.float32).reshape(-1, im.channels)
            AV[k] = [float(x) for x in px[::7, :3].mean(0)] + [1.0]
        except Exception:
            AV[k] = [0.5, 0.5, 0.5, 1]
    return AV[k]


def lerp(a, b, t):
    return [a[i] * (1 - t) + b[i] * t for i in range(4)]


def sock_col(s, dep=0):
    if s is None:
        return [0.5, 0.5, 0.5, 1]
    if not s.is_linked:
        v = getattr(s, "default_value", None)
        try:
            v = list(v)
            return (v + [1] * 4)[:4] if len(v) >= 3 else [v[0]] * 3 + [1]
        except TypeError:
            return [float(v)] * 3 + [1] if v is not None else [0.5] * 3 + [1]
    if dep > 14:
        return [0.5, 0.5, 0.5, 1]
    l = s.links[0]
    n = l.from_node
    fs = l.from_socket
    t = n.type
    if t == "RGB":
        return list(n.outputs[0].default_value)
    if t == "VALUE":
        return [n.outputs[0].default_value] * 3 + [1]
    if t == "TEX_IMAGE" and n.image:
        return img_avg(n.image)
    if t == "VALTORGB":
        e = n.color_ramp.elements
        return [sum(x.color[i] for x in e) / len(e) for i in range(4)]
    if t in ("MIX", "MIX_RGB"):
        if t == "MIX":
            ins = [i for i in n.inputs if i.enabled]
            fac = ins[0]
            A = ins[1]
            B = ins[2]
        else:
            fac = n.inputs[0]
            A = n.inputs[1]
            B = n.inputs[2]
        f = (
            0.5
            if fac.is_linked
            else float(
                fac.default_value
                if not hasattr(fac.default_value, "__len__")
                else fac.default_value[0]
            )
        )
        return lerp(sock_col(A, dep + 1), sock_col(B, dep + 1), max(0, min(1, f)))
    if t in (
        "HUE_SAT",
        "BRIGHTCONTRAST",
        "GAMMA",
        "INVERT",
        "CURVE_RGB",
        "SEPARATE_COLOR",
        "MAP_RANGE",
        "CLAMP",
        "REROUTE",
        "MATH",
        "VECT_MATH",
    ):
        for i in n.inputs:
            if i.type in ("RGBA", "VALUE", "VECTOR") and (i.is_linked or i.type == "RGBA"):
                return sock_col(i, dep + 1)
    if t == "GROUP" and n.node_tree:
        go = [x for x in n.node_tree.nodes if x.type == "GROUP_OUTPUT"]
        if go:
            gi = go[0].inputs.get(fs.name)
            if gi and gi.is_linked:
                ln = gi.links[0]
                if ln.from_node.type == "GROUP_INPUT":
                    return sock_col(n.inputs.get(ln.from_socket.name), dep + 1)
                return sock_col(gi, dep + 1)
            if gi:
                return sock_col(gi, dep + 1)
    if t == "GROUP_INPUT":
        return [0.5, 0.5, 0.5, 1]
    if t in ("BSDF_PRINCIPLED", "BSDF_DIFFUSE", "EMISSION"):
        return sock_col(n.inputs[0], dep + 1)
    # textures / attributes: average of their colour inputs if any, else mid grey
    cols = [sock_col(i, dep + 1) for i in n.inputs if i.type == "RGBA"]
    if cols:
        return [sum(c[i] for c in cols) / len(cols) for i in range(4)]
    return [0.45, 0.45, 0.45, 1]


def find_bsdf(nt, dep=0):
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output] or [
        n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"
    ]
    if not out or not out[0].inputs["Surface"].is_linked:
        return None
    n = out[0].inputs["Surface"].links[0].from_node
    for _ in range(10):
        if n.type in (
            "BSDF_PRINCIPLED",
            "BSDF_DIFFUSE",
            "EMISSION",
            "BSDF_GLASS",
            "BSDF_TRANSPARENT",
            "BSDF_TRANSLUCENT",
        ):
            return n
        if n.type in ("MIX_SHADER", "ADD_SHADER"):
            ins = [i for i in n.inputs if i.type == "SHADER" and i.is_linked]
            if not ins:
                return None
            n = ins[0].links[0].from_node
            continue
        if n.type == "GROUP" and n.node_tree:
            r = [
                x
                for x in n.node_tree.nodes
                if x.type in ("BSDF_PRINCIPLED", "BSDF_DIFFUSE", "EMISSION")
            ]
            return r[0] if r else None
        return None
    return None


def uv_image(sock):
    # an allowed image texture fed directly (via UV map / no vector) into this socket
    if not sock or not sock.is_linked:
        return None
    n = sock.links[0].from_node
    if n.type == "TEX_IMAGE" and n.image and img_ok(n.image):
        v = n.inputs["Vector"]
        if not v.is_linked:
            return n.image
        f = v.links[0].from_node
        if f.type == "UVMAP" or (f.type == "TEX_COORD" and v.links[0].from_socket.name == "UV"):
            return n.image
        if f.type == "MAPPING" and f.inputs["Vector"].is_linked:
            g = f.inputs["Vector"].links[0]
            if g.from_node.type == "UVMAP" or (
                g.from_node.type == "TEX_COORD" and g.from_socket.name == "UV"
            ):
                return n.image
    return None


# ---------- material categories (viewer applies CC0 world-space textures per category) ----------
CATS = [
    ("glass", r"glass|glazing|window_pane|curtainwall"),
    ("asphalt", r"asphalt|tarmac|road|street|lot_|parking|drive|carriageway|Asphalt026"),
    ("brick", r"brick|Bricks066"),
    ("rooftile", r"roof_?tile|clay_tile|terracotta|RoofingTiles"),
    ("pavers", r"paver|herringbone|PavingStones|cobble|plaza"),
    ("mulch", r"mulch|WoodChips|bed_|planting|soil"),
    ("grass", r"lawn|grass|turf|Grass004|skirt|terrain|ground|meadow|field"),
    ("gravel", r"gravel|Gravel022|ballast"),
    ("plaster", r"stucco|plaster|render|Plaster00"),
    ("stone", r"stone|granite|marble|limestone|Granite|cast_stone"),
    (
        "concrete",
        r"concrete|curb|kerb|sidewalk|walk|pav|slab|step|stair|apron|ramp|Concrete034|deck|wall",
    ),
    ("metal", r"metal|steel|alumin|rail|Metal032|pole|fence"),
    ("wood", r"wood|timber|bench|Wood049"),
]
PAINT = set()


def mat_images(nt, dep=0, acc=None):
    acc = [] if acc is None else acc
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image:
            acc.append(n.image.name + " " + os.path.basename(n.image.filepath))
        elif n.type == "GROUP" and n.node_tree and dep < 4:
            mat_images(n.node_tree, dep + 1, acc)
    return acc


def category(m, glass, leaf):
    if leaf:
        return "leaf"
    if glass:
        return "glass"
    imgs = mat_images(m.node_tree) if m.use_nodes and m.node_tree else []
    for i in imgs:
        mm = re.search(r"(ws\d+[a-z]?)_mask_tile_", i)
        if mm:
            PAINT.add(mm.group(1))
    # Aerial-draped terrain averages to grey and its image names mention roads and lots; it is ground
    # with no surface detail of its own, so it gets the lawn tone like the far-field skirt.
    if re.search(r"(ground|skirt)_ortho", m.name, re.I):
        return "grass"
    key = m.name + " " + " ".join(imgs)
    for c, rx in CATS:
        if re.search(rx, key, re.I):
            return c
    return ""


LEAFT = {}
RAMPS = {}
done = set()
stats = {"flat": 0, "tex": 0, "glass": 0}


def flatten(m):
    if m is None or m.name in done:
        return
    done.add(m.name)
    col = list(m.diffuse_color)
    rough = 0.8
    metal = 0.0
    alpha = 1.0
    img = None
    aimg = None
    glass = False
    if m.use_nodes and m.node_tree:
        bs = find_bsdf(m.node_tree)
        if bs is not None:
            if bs.type == "BSDF_PRINCIPLED":
                col = sock_col(bs.inputs["Base Color"])
                img = uv_image(bs.inputs["Base Color"])
                aimg = uv_image(bs.inputs["Alpha"])
                r = bs.inputs["Roughness"]
                rough = 0.7 if r.is_linked else r.default_value
                mt = bs.inputs["Metallic"]
                metal = 0 if mt.is_linked else mt.default_value
                tr = bs.inputs.get("Transmission Weight")
                al = bs.inputs["Alpha"]
                if tr and not tr.is_linked and tr.default_value > 0.5:
                    glass = True
                if not al.is_linked and al.default_value < 0.6:
                    glass = True
                    alpha = max(0.2, al.default_value)
                if bs.inputs["Alpha"].is_linked and not aimg:
                    aimg = None
            elif bs.type in ("BSDF_GLASS", "BSDF_TRANSPARENT"):
                glass = True
                col = sock_col(bs.inputs[0])
            else:
                col = sock_col(bs.inputs[0])
    # leaf/alpha-card materials: allowed *_Opacity image fed from UVs (optionally via Mapping) anywhere in the tree
    leaf = None
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image and "pacity" in n.image.name and img_ok(n.image):
                v = n.inputs["Vector"]
                mp = None
                if v.is_linked and v.links[0].from_node.type == "MAPPING":
                    mp = v.links[0].from_node
                cimg = next(
                    (
                        x.image
                        for x in m.node_tree.nodes
                        if x.type == "TEX_IMAGE"
                        and x.image
                        and "Color" in x.image.name
                        and img_ok(x.image)
                    ),
                    None,
                )
                leaf = (
                    n.image,
                    cimg,
                    mp
                    and (
                        tuple(mp.inputs["Location"].default_value),
                        tuple(mp.inputs["Rotation"].default_value),
                        tuple(mp.inputs["Scale"].default_value),
                    ),
                )
                glass = False
                break
    if glass and re.search(r"leaf|needle|foliage|crown|canopy|hedge|shrub|grass", m.name, re.I):
        glass = False
        alpha = 1.0
    if glass:
        col = [0.55, 0.62, 0.66, 1]
        alpha = 0.35
        rough = 0.08
        metal = 0.0
        stats["glass"] += 1
    if leaf and m.node_tree:
        RAMPS[m.name] = [
            tuple(e.color[:3])
            for x in m.node_tree.nodes
            if x.type == "VALTORGB"
            for e in x.color_ramp.elements
        ]
    m["cat"] = category(m, glass, leaf)
    nt = m.node_tree if m.use_nodes else None
    if nt is None:
        m.use_nodes = True
        nt = m.node_tree
    nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], o.inputs["Surface"])
    p.inputs["Base Color"].default_value = [max(0, min(1, c)) for c in col[:3]] + [1]
    p.inputs["Roughness"].default_value = max(0.05, min(1, rough))
    p.inputs["Metallic"].default_value = max(0, min(1, metal))
    if leaf:
        oimg, cimg, mp = leaf
        uv = nt.nodes.new("ShaderNodeUVMap")
        src = uv.outputs[0]
        if mp:
            mn = nt.nodes.new("ShaderNodeMapping")
            nt.links.new(uv.outputs[0], mn.inputs["Vector"])
            mn.inputs["Location"].default_value = mp[0]
            mn.inputs["Rotation"].default_value = mp[1]
            mn.inputs["Scale"].default_value = mp[2]
            src = mn.outputs[0]
        # glTF has no tint node: the exporter keeps the CC0 colour+opacity images; the tint goes to leaf_tints.json
        # and tint_leaves.mjs writes it into baseColorFactor before optimisation.
        rr = (
            [x for x in m.node_tree.nodes if x.type == "VALTORGB"]
            if False
            else RAMPS.get(m.name, [])
        )
        base = [sum(e[i] for e in rr) / len(rr) for i in range(3)] if rr else [0.18, 0.28, 0.10]
        tl = sum(img_avg(cimg)[:3]) / 3 if cimg else 1.0
        LEAFT[m.name] = [max(0.03, min(1.0, c / max(0.15, tl))) for c in base]
        if cimg:
            tc = nt.nodes.new("ShaderNodeTexImage")
            tc.image = cimg
            nt.links.new(src, tc.inputs["Vector"])
            nt.links.new(tc.outputs[0], p.inputs["Base Color"])
        ta = nt.nodes.new("ShaderNodeTexImage")
        ta.image = oimg
        nt.links.new(src, ta.inputs["Vector"])
        nt.links.new(ta.outputs[0], p.inputs["Alpha"])
        try:
            m.surface_render_method = "DITHERED"
        except Exception:
            pass
        m.alpha_threshold = 0.5
        stats["tex"] += 1
        img = None
        aimg = None
    elif img:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = img
        nt.links.new(t.outputs[0], p.inputs["Base Color"])
        stats["tex"] += 1
    else:
        stats["flat"] += 1
    if aimg:
        ta = nt.nodes.new("ShaderNodeTexImage")
        ta.image = aimg
        nt.links.new(ta.outputs[0], p.inputs["Alpha"])
        m.blend_method = "CLIP" if hasattr(m, "blend_method") else None
        m.alpha_threshold = 0.5
        try:
            m.surface_render_method = "DITHERED"
        except Exception:
            pass
    elif alpha < 1:
        p.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
            m.blend_method = "BLEND"
        except Exception:
            pass


for mat in list(bpy.data.materials):
    flatten(mat)
json.dump(AV, open(cache_p, "w"))
print("WEB materials", stats, flush=True)
json.dump(LEAFT, open(OUT + ".leaf.json", "w"))
json.dump(sorted(PAINT), open(OUT + ".paint.json", "w"))
# only material categories go out as glTF extras: drop object/mesh custom properties
for idb in list(bpy.data.objects) + list(bpy.data.meshes):
    for k in list(idb.keys()):
        try:
            del idb[k]
        except Exception:
            pass

# ---------- tree thinning (shared Tree_* meshes): keep ~1/3 of leaf cards, enlarge them ----------
KEEP = float(os.environ.get("LEAFKEEP", "0.35"))
random.seed(7)
for me in bpy.data.meshes:
    if not me.name.startswith("Tree_") or len(me.polygons) < 6000:
        continue
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    leafmat = set(
        i
        for i, mm in enumerate(me.materials)
        if mm and re.search(r"leaf|foliage|needle|crown|canopy", mm.name, re.I)
    )
    if not leafmat:
        bm.free()
        continue
    seen = set()
    kill = []
    for f in bm.faces:
        if f.index in seen or f.material_index not in leafmat:
            continue
        isl = []
        st = [f]
        seen.add(f.index)
        while st:
            g = st.pop()
            isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen and h.material_index in leafmat:
                        seen.add(h.index)
                        st.append(h)
        if random.random() > KEEP:
            kill += isl
        else:
            vs = {v for g in isl for v in g.verts}
            c = sum((v.co for v in vs), Vector()) / len(vs)
            for v in vs:
                v.co = c + (v.co - c) * 1.55
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(me)
    bm.free()
    print("WEB thinned", me.name, len(me.polygons), flush=True)

# ---------- web decimation (Blender-side; gltf-transform simplify would eat leaf cards) ----------
LEAFRE = re.compile(r"leaf|foliage|needle|crown|canopy|card|grass|hedge|shrub", re.I)
DEC = float(os.environ.get("DECIMATE", "0.5"))
for me in bpy.data.meshes:
    if me.name.startswith("WS62_crown_") and len(me.polygons) > 30:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("tmp_dec", me)
        sc.collection.objects.link(o)
        d = o.modifiers.new("d", "DECIMATE")
        d.ratio = 0.18
        dg = bpy.context.evaluated_depsgraph_get()
        ev = o.evaluated_get(dg)
        nm = bpy.data.meshes.new_from_object(ev)
        me.clear_geometry()
        bm = bmesh.new()
        bm.from_mesh(nm)
        bm.to_mesh(me)
        bm.free()
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(nm)
        print("WEB crown", me.name, len(me.polygons), flush=True)
ndec = 0
for o in sc.objects:
    if o.type != "MESH" or o.data.name.startswith(("Tree_", "WS62_crown_")):
        continue
    if any(s.material and LEAFRE.search(s.material.name) for s in o.material_slots):
        continue
    n = len(o.data.polygons)
    gn = any(m.type in ("NODES", "SUBSURF") and m.show_render for m in o.modifiers)
    if n > 12000 or (gn and n > 2000):
        d = o.modifiers.new("web_decimate", "DECIMATE")
        d.ratio = DEC
        d.use_collapse_triangulate = True
        ndec += 1
print("WEB decimated objects", ndec, flush=True)
# speed patch: the 4.5 exporter dedups with list.index (O(n^2)); use an identity map instead
import io_scene_gltf2.blender.exp.exporter as _ex

_cls = [
    c
    for c in vars(_ex).values()
    if isinstance(c, type) and hasattr(c, "_" + c.__name__ + "__append_unique_and_get_index")
][0]
_IDX = {}


def _fast(target, obj):
    d = _IDX.setdefault(id(target), {})
    k = id(obj)
    if k in d and d[k] < len(target) and target[d[k]] is obj:
        return d[k]
    d[k] = len(target)
    target.append(obj)
    return d[k]


setattr(_cls, "_" + _cls.__name__ + "__append_unique_and_get_index", staticmethod(_fast))
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_yup=True,
    export_image_format="WEBP",
    export_texcoords=True,
    export_normals=True,
    export_materials="EXPORT",
    export_gn_mesh=True,
    export_gpu_instances=False,
    export_extras=True,
    export_animations=False,
    export_skins=False,
    export_morph=False,
)
print("WEB WROTE", OUT, os.path.getsize(OUT), flush=True)
for l in open("/proc/self/status"):
    if l.startswith("VmHWM"):
        print("WEB MEM", l.strip(), flush=True)
