"""Baking the atlas from procedural materials on the near LOD: _co, _smdi, _nohq (PNG), then
ImageToPAA. The scheme is a coverage mask, no Blender margin (it overwrites neighboring islands),
and gaps are filled with the mean of the neighbors by the mask - baked pixels are not touched.

The device is set by the environment variable OZ_BAKE_DEVICE: GPU (the default, CUDA) or CPU. With
no CUDA device a line goes to the log and the CPU is used. OPTIX is for a remote machine with an
RTX card: with no OptiX, CUDA is used; with none of it, the CPU, with a line in the log.
At most GPU_SLOTS models bake on the GPU at once (OZ_GPU_SLOTS, 2 by default: the pipeline runs
three at once and the memory of a GTX 1660 is not enough for three), the others wait. A bake that
fails on the GPU pauses and retries on the GPU, not on the CPU: the CPU is far too slow."""
import contextlib
import msvcrt
import os
import shutil
import subprocess
import sys
import tempfile
import time

import bpy
import numpy as np

import kmats

IMAGE_TO_PAA = r"E:\SteamLibrary\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe"

MATS = {}

GPU_SLOTS = int(os.environ.get("OZ_GPU_SLOTS", "2"))
# Fast baking: Blender bakes each selected object with a separate call and rebuilds the Cycles
# scene before each one - m23 makes 33 calls per map and the GPU idles (measured on an RTX 4090:
# 12 % load). FAST: the scene is not rebuilt (use_persistent_data), and cover and ao are baked in
# one call on a joined object. The atlas is the same: for m22, m23, m86 identical up to 1 of 255 at
# most, for m05, m16 the differences are smaller than between two runs of the normal mode (their
# boolean difference cuts the surface differently).
# color, smdi, normal cannot be joined: Bevel in kmats.edge_wear sees the edges of its own object
# only - the chips change at the joints of parts. On by default (baking here is 1.8-2.3 times
# faster); OZ_BAKE_FAST=0 turns it off.
FAST = os.environ.get("OZ_BAKE_FAST", "1") == "1"
JOINED_MODES = ("cover", "ao")
# One model across several Blender copies: the per-part passes (PART_MODES; color for the states
# looks) are handed to SPLIT-1 more Blender copies over the same model (kbake.Split); each pass is
# the same as in a single copy, so the atlas is the same. OZ_BAKE_SPLIT=N; kmodel --bake-only sets
# it itself (4 by default; --no-split or OZ_BAKE_SPLIT=1 turns it off). The copies count in
# GPU_SLOTS like separate models; the main copy holds no GPU slot while it waits.
SPLIT = int(os.environ.get("OZ_BAKE_SPLIT", "1"))
PART_MODES = ("color", "smdi", "normal")
GPU_RETRIES = 10     # retries on the GPU after a failure (out of memory), pausing GPU_RETRY_WAIT s each
GPU_RETRY_WAIT = 60
SLOT_DIR = os.path.join(tempfile.gettempdir(), "oz_bake_gpu")
# CPU threads of Blender (several Blender copies at once on all 24 threads overheated a CPU and
# crashed the machine): OZ_CPU_THREADS=N - Cycles and the Split copies use at most N threads;
# 0 or unset - no limit.
CPU_THREADS = int(os.environ.get("OZ_CPU_THREADS", "0") or 0)


def limit_threads(sc):
    """Limit Cycles of this scene to CPU_THREADS threads (if set)."""
    if CPU_THREADS > 0:
        sc.render.threads_mode = "FIXED"
        sc.render.threads = CPU_THREADS


def get_mat(kind_table, kind, origin):
    if kind not in MATS:
        m = bpy.data.materials.new("oz_" + kind)
        outs = kmats.make(kind_table, kind, m, origin)
        MATS[kind] = (m, outs)
    return MATS[kind]


def to_objects(parts, kind_table, origin, tag, remap=None):
    """remap - kind -> another kind of the same table (the second machine look: the screen glows, the lamp is on)."""
    obs = []
    for p in parts:
        if p.section != "atlas":
            continue
        me = bpy.data.meshes.new("%s_%s" % (tag, p.name))
        for f in p.bm.faces:
            f.material_index = f[p.reg]
        p.bm.to_mesh(me)
        for r in p.regions:
            kind = (remap or {}).get(r[1], r[1])
            me.materials.append(get_mat(kind_table, kind, origin)[0])
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(ob)
        obs.append(ob)
    return obs


def use_device(sc):
    """Set the Cycles device from OZ_BAKE_DEVICE; returns the one we will bake on."""
    limit_threads(sc)
    want = os.environ.get("OZ_BAKE_DEVICE", "GPU").strip().upper()
    if want != "CPU":
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            if want == "OPTIX":
                try:
                    prefs.compute_device_type = "OPTIX"
                    prefs.refresh_devices()
                    optix = [d for d in prefs.devices if d.type == "OPTIX"]
                    for d in prefs.devices:
                        d.use = d.type == "OPTIX"
                    if optix:
                        sc.cycles.device = "GPU"
                        print("bake device: GPU OPTIX (%s)" % ", ".join(d.name for d in optix))
                        return "GPU"
                    print("bake device: no OptiX device - trying CUDA")
                except Exception as e:  # noqa: BLE001 - OptiX did not start -> CUDA
                    print("bake device: OptiX did not start (%s) - trying CUDA" % e)
            prefs.compute_device_type = "CUDA"
            prefs.refresh_devices()
            cuda = [d for d in prefs.devices if d.type == "CUDA"]
            for d in prefs.devices:
                d.use = d.type == "CUDA"
            if cuda:
                sc.cycles.device = "GPU"
                print("bake device: GPU (%s)" % ", ".join(d.name for d in cuda))
                return "GPU"
            print("bake device: no CUDA device - baking on the CPU")
        except Exception as e:  # noqa: BLE001 - any setup failure -> CPU
            print("bake device: the GPU did not start (%s) - baking on the CPU" % e)
    sc.cycles.device = "CPU"
    print("bake device: CPU")
    return "CPU"


@contextlib.contextmanager
def gpu_slot(sc):
    """A GPU slot: a lock on one of the GPU_SLOTS files. The system releases the lock itself if
    Blender crashes, so there are no stuck slots."""
    if sc.cycles.device != "GPU":
        yield
        return
    os.makedirs(SLOT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    said = False
    while True:
        for i in range(GPU_SLOTS):
            f = open(os.path.join(SLOT_DIR, "slot%d.lock" % i), "a+b")
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                f.close()
                continue
            if said:
                print("bake device: a GPU slot freed up after %.0f s" % (time.perf_counter() - t0))
            try:
                yield
            finally:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                f.close()
            return
        if not said:
            print("bake device: %d models are already baking on the GPU - waiting for a slot" % GPU_SLOTS)
            said = True
        time.sleep(10)


def run_bake(sc, kind):
    """One pass; if it fails on the GPU, pause and retry on the GPU (not on the CPU)."""
    for attempt in range(GPU_RETRIES + 1):
        try:
            bpy.ops.object.bake(type=kind)
            return
        except RuntimeError as e:
            if sc.cycles.device != "GPU" or attempt == GPU_RETRIES:
                raise
            print("bake device: baking on the GPU failed (%s) - retry %d in %d s"
                  % (e, attempt + 1, GPU_RETRY_WAIT))
            time.sleep(GPU_RETRY_WAIT)


AO_CACHE = {}       # atlas size -> AO of the main pass: the "working" look (color_only) reuses it


def modes_for(color_only):
    """The passes of an atlas: cover (island mask), color, smdi, normal; the "dayz" profile adds ao.
    color_only (a machine look) - cover and color."""
    modes = ("cover", "color") if color_only else ("cover", "color", "smdi", "normal")
    if kmats.LOOK["name"] == "dayz" and not color_only:
        modes += ("ao",)
    return modes


def bake(parts, kind_table, origin, atlas, out_dir, texname, samples=16, remap=None, color_only=False,
         elsewhere=None):
    """The atlases _co, _nohq, _smdi. color_only - _co only (the second machine look: the same
    relief and gloss, a different color for some kinds - remap). The "dayz" look profile
    (kmats.use_look): one more pass, AO - corner shading is multiplied into the color (_ao.png is
    saved for inspection), the color is slightly desaturated, the highlight and gloss of _smdi are
    recomputed by the profile; the look measurement goes to the log (look: ...). elsewhere -
    kbake.Split: part of the passes is baked by another Blender copy, and their result is
    collected here before the finishing."""
    dayz = kmats.LOOK["name"] == "dayz"
    os.makedirs(out_dir, exist_ok=True)
    skip = elsewhere.modes(texname) if elsewhere else ()
    result = bake_passes(parts, kind_table, origin, atlas, texname, [m for m in modes_for(color_only) if m not in skip],
                         samples, remap)
    if skip:
        got = elsewhere.fetch(texname)
        result.update(got)
        lost = [m for m in skip if m not in got]
        if lost:
            print("bake split: the copy did not bake %s - baking here" % ", ".join(lost))
            result.update(bake_passes(parts, kind_table, origin, atlas, texname, lost, samples, remap))
    finish(result, atlas, out_dir, texname, color_only, dayz)


def bake_passes(parts, kind_table, origin, atlas, texname, modes, samples=16, remap=None):
    """The passes in modes of one atlas -> {mode: an array atlas x atlas x 3, rows top to bottom}."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    use_device(sc)
    sc.cycles.samples = samples
    sc.render.bake.margin = 0
    obs = to_objects(parts, kind_table, origin, "bake", remap)
    for ob in bpy.context.scene.objects:
        ob.select_set(ob in obs)
    bpy.context.view_layer.objects.active = obs[0]
    if FAST:
        sc.render.use_persistent_data = True
    result = {}
    t_all = time.perf_counter()
    if "ao" in modes:
        if sc.world is None:
            sc.world = bpy.data.worlds.new("bake_world")
        sc.world.light_settings.distance = 0.25      # AO: shadows of neighboring parts within 25 cm
    if FAST:
        # per-part passes first, then the joined ones: joining is irreversible
        modes = tuple(m for m in modes if m not in JOINED_MODES) + tuple(m for m in modes if m in JOINED_MODES)
    with gpu_slot(sc):
        for mode in modes:
            if FAST and mode in JOINED_MODES and len(obs) > 1:
                bpy.ops.object.join()
                obs = [bpy.context.view_layer.objects.active]
                print("bake: parts joined into one object for %s" % ", ".join(JOINED_MODES))
            img = bpy.data.images.new("bake_" + mode, atlas, atlas, alpha=False, float_buffer=True)
            img.colorspace_settings.name = "Non-Color" if mode != "color" else "Linear Rec.709"
            t0 = time.perf_counter()
            for kind, (m, outs) in MATS.items():
                kmats.wire(m, outs, "cover" if mode == "ao" else mode, img)
            if mode == "normal":
                sc.render.bake.normal_space = "TANGENT"
                sc.render.bake.normal_g = "NEG_Y"        # DirectX: green points down
                run_bake(sc, "NORMAL")
            elif mode == "ao":
                run_bake(sc, "AO")
            else:
                run_bake(sc, "EMIT")
            a = np.array(img.pixels[:], np.float32).reshape(atlas, atlas, 4)[::-1, :, :3]
            result[mode] = a
            print("baked %s: %.1f s (%s)" % (mode, time.perf_counter() - t0, sc.cycles.device))
    print("bake %s total: %.1f s (%s)" % (texname, time.perf_counter() - t_all, sc.cycles.device))
    for ob in obs:
        bpy.data.objects.remove(ob)
    return result


def finish(result, atlas, out_dir, texname, color_only, dayz):
    """Finishing the passes: filling gaps, AO into the color, _smdi by profile, PNG."""
    covered = result.pop("cover")[..., 0] > 0.5
    print("atlas coverage %.0f%%" % (100.0 * covered.mean()))
    t0 = time.perf_counter()
    # the maps are independent - each in its own thread (numpy releases the GIL on large arrays); the result is the same
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(result))) as ex:
        filled = list(ex.map(lambda a: fill_unbaked(a, covered), list(result.values())))
    for mode, a in zip(list(result), filled):
        result[mode] = a
    print("filled %s: %.1f s" % (", ".join(result), time.perf_counter() - t0))
    if dayz:
        if "ao" in result:
            AO_CACHE[atlas] = result.pop("ao")[..., 0]
            save_png(os.path.join(out_dir, texname + "_ao.png"), np.repeat(AO_CACHE[atlas][..., None], 3, axis=2))
            # The island mask lets a checker tell the empty space of the atlas (black in _ao) from
            # shadowed pixels: without it, 35 % of "black" turned out to include 23 % of empty space.
            save_png(os.path.join(out_dir, texname + "_cover.png"),
                     np.repeat(covered[..., None].astype(np.float32), 3, axis=2))
        result["color"] = patina(result["color"], AO_CACHE.get(atlas))
    save_png(os.path.join(out_dir, texname + "_co.png"), to_srgb(result["color"]))
    if color_only:
        print("textures written to", out_dir)
        return
    save_png(os.path.join(out_dir, texname + "_nohq.png"), result["normal"])
    smdi = np.zeros((atlas, atlas, 3), np.float32)
    smdi[..., 0] = 1.0
    smdi[..., 1] = np.clip(kmats.spec_out(np.clip(result["smdi"][..., 0], 0, 1)), 0, 1)
    smdi[..., 2] = np.clip(result["smdi"][..., 1] * (kmats.LOOK["gloss"] if dayz else 1.0), 0, 1)
    if dayz:
        look_report(to_srgb(result["color"]), smdi, covered)
    h2 = atlas // 2
    smdi = smdi.reshape(h2, 2, h2, 2, 3).mean(axis=(1, 3))
    save_png(os.path.join(out_dir, texname + "_smdi.png"), smdi)
    print("textures written to", out_dir)


def patina(color, ao):
    """The "dayz" profile: corner shading (AO) into the color (linear RGB). The color is already
    subdued in the material (kmats.dayz_layers), so the preview without baking matches the game."""
    k = kmats.LOOK
    if ao is not None:
        color = color * (1.0 - k["ao"] + k["ao"] * np.clip(ao, 0, 1))[..., None]
    return color


def look_report(co_srgb, smdi, covered):
    """Measure the look over the occupied part of the atlas - the same numbers that were measured for vanilla textures."""
    m = covered
    lum = (co_srgb[..., 0] * 0.299 + co_srgb[..., 1] * 0.587 + co_srgb[..., 2] * 0.114)[m] * 255
    mx, mn = co_srgb.max(axis=2)[m], co_srgb.min(axis=2)[m]
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0.0)
    g, b = smdi[..., 1][m], smdi[..., 2][m]
    spec = kmats.LOOK["rvmat"]["specular"]
    print("look: L %.0f (10%% %.0f, 90%% %.0f), S %.2f, smdi G %.3f (90%% %.3f), B %.2f, specular x G %.3f"
          % (lum.mean(), np.percentile(lum, 10), np.percentile(lum, 90), sat.mean(), g.mean(),
             np.percentile(g, 90), b.mean(), spec * g.mean()))
    print("look: vanilla - workshop furniture L 31..78, specular x G 0.01..0.09; tools 0.06..0.24")


def fill_unbaked(img, covered, iters=64):
    """Fill the atlas gaps layer by layer with the mean of the already filled neighbors (4 sides,
    wrapping around, like np.roll), at most iters layers. Only the pixels of the new layer are
    computed, with float32 additions in the same order as a plain np.roll pass over the whole
    image: the result is bit-identical to it, and a 2048 map takes seconds instead of 30 s on one core."""
    img = img.copy()
    m = covered.copy()
    h, w = m.shape
    shifts = ((1, 0), (-1, 0), (0, 1), (0, -1))      # np.roll (dy, dx): the value comes from (y - dy, x - dx)
    for _ in range(iters):
        if m.all():
            break
        cnt = np.zeros(m.shape, np.float32)
        for dy, dx in shifts:
            cnt += np.roll(m, (dy, dx), axis=(0, 1))
        ys, xs = np.nonzero((~m) & (cnt > 0))
        acc = np.zeros((len(ys),) + img.shape[2:], img.dtype)
        for dy, dx in shifts:
            ny, nx = (ys - dy) % h, (xs - dx) % w
            acc += img[ny, nx] * m[ny, nx][:, None]
        img[ys, xs] = acc / cnt[ys, xs][:, None]
        m[ys, xs] = True
    return img


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def save_png(path, img):
    """RGB or RGBA 0..1 with rows TOP TO BOTTOM (the Blender buffer runs bottom to top)."""
    img = np.clip(img[::-1], 0, 1)
    h, w, c = img.shape
    im = bpy.data.images.new(os.path.basename(path), w, h, alpha=(c == 4))
    rgba = np.ones((h, w, 4), np.float32)
    rgba[..., :c] = img
    im.pixels.foreach_set(rgba.ravel())
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


def resize_png(src, dst, size):
    """PNG -> a square size x size (the PAA side is a power of two): the screen picture is
    stretched over the whole UV 0..1 of the part, and the part's shape restores the proportions."""
    im = bpy.data.images.load(src, check_existing=False)
    im.scale(size, size)
    im.filepath_raw = dst
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


def to_paa(src_dir, dst_dir, names):
    os.makedirs(dst_dir, exist_ok=True)
    for n in names:
        src = os.path.join(src_dir, n + ".png")
        dst = os.path.join(dst_dir, n + ".paa")
        r = subprocess.run([IMAGE_TO_PAA, src, dst], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(dst):
            raise RuntimeError("ImageToPAA failed for %s: %s %s" % (n, r.stdout, r.stderr))
        print("paa:", dst, os.path.getsize(dst))


class Split:
    """One model across several Blender copies (SPLIT): the per-part passes are handed to Blender
    copies running the same model script with the --bake-part key (kmodel); a copy saves its arrays
    into a temp folder, and the main one collects them before the finishing - bake(...,
    elsewhere=Split). The copies' output goes to the same log."""

    def __init__(self, script, argv, tasks, n):
        """tasks: [(atlas, mode)] - the passes that can be handed out; n - how many Blender copies
        there are in total, including the main one. The main copy gets the first pass (it also
        bakes cover and ao), the copies get the rest round-robin."""
        self.dir = tempfile.mkdtemp(prefix="oz_bake_split_")
        n = max(1, min(n, len(tasks)))
        shares = [[] for _ in range(n)]
        for i, t in enumerate(tasks):
            shares[0 if i == 0 or n == 1 else 1 + (i - 1) % (n - 1)].append(t)
        self.away = [t for share in shares[1:] for t in share]
        self.procs = []
        try:
            out = sys.stdout.fileno()
        except (AttributeError, OSError, ValueError):
            out = None
        # the copies exit together with this Blender (if the runner cancels the job, the copies do
        # not finish their pass and do not hold its log)
        self.job = kill_with_me()
        for k, share in enumerate(shares[1:], 1):
            spec = ",".join("%s:%s" % t for t in share)
            cmd = [bpy.app.binary_path, "-b", "--factory-startup"] + (["-t", str(CPU_THREADS)] if CPU_THREADS > 0 else []) + [
                   "--python-exit-code", "1", "--python", script, "--"] + list(argv) + ["--bake-part", self.dir, spec,
                                                                                       str(os.getpid())]
            sys.stdout.flush()
            p = subprocess.Popen(cmd, stdout=out, stderr=out)
            join_job(self.job, p)
            self.procs.append(p)
            print("bake split: copy %d bakes %s" % (k, spec))
        self.waited = False

    def modes(self, texname):
        return [m for t, m in self.away if t == texname]

    def fetch(self, texname):
        """The pass arrays of atlas texname from the copies (waits until all the copies finish)."""
        if not self.waited:
            t0 = time.perf_counter()
            for p in self.procs:
                p.wait()
                if p.returncode != 0:
                    print("bake split: a copy exited with code %d" % p.returncode)
            self.waited = True
            print("bake split: the copies finished, waited %.1f s" % (time.perf_counter() - t0))
        out = {}
        for t, m in self.away:
            fn = part_path(self.dir, t, m)
            if t == texname and os.path.exists(fn):
                out[m] = np.load(fn)
        return out

    def close(self):
        for p in self.procs:
            if p.poll() is None:
                p.kill()
        shutil.rmtree(self.dir, ignore_errors=True)


def part_path(folder, texname, mode):
    return os.path.join(folder, "%s__%s.npy" % (texname, mode))


def bake_part(parts, kind_table, origin, atlas, folder, spec, parent, remaps, samples=16):
    """A Blender copy for Split: the passes in spec ("atlas:mode,...") -> arrays in folder. If the
    main copy is gone (the job was cancelled), exit."""
    for item in spec.split(","):
        texname, mode = item.split(":")
        if not alive(parent):
            print("bake split: the main Blender is gone - exiting")
            return
        res = bake_passes(parts, kind_table, origin, atlas, texname, [mode], samples, remaps.get(texname))
        np.save(part_path(folder, texname, mode), res[mode])


def alive(pid):
    """The process is still running (Windows)."""
    import ctypes
    k = ctypes.windll.kernel32
    h = k.OpenProcess(0x00100000, False, int(pid))        # SYNCHRONIZE
    if not h:
        return False
    try:
        return k.WaitForSingleObject(h, 0) == 0x102       # WAIT_TIMEOUT - not finished yet
    finally:
        k.CloseHandle(h)


def kill_with_me():
    """A Windows Job Object that kills its processes together with this one
    (JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE): the system terminates the processes in it when its handle
    closes, that is, when this Blender exits. None - it failed (the copies then exit by themselves
    after their pass, see kbake.alive)."""
    try:
        import ctypes
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", ctypes.c_ulonglong * 6),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        k = ctypes.windll.kernel32
        k.CreateJobObjectW.restype = wintypes.HANDLE
        job = k.CreateJobObjectW(None, None)
        info = Extended()
        info.BasicLimitInformation.LimitFlags = 0x2000
        if not job or not k.SetInformationJobObject(wintypes.HANDLE(job), 9, ctypes.byref(info), ctypes.sizeof(info)):
            return None
        return job
    except Exception as e:  # noqa: BLE001 - baking is the same without it
        print("bake split: Job Object not created (%s)" % e)
        return None


def join_job(job, proc):
    if job is None:
        return
    import ctypes
    from ctypes import wintypes
    if not ctypes.windll.kernel32.AssignProcessToJobObject(wintypes.HANDLE(job), wintypes.HANDLE(int(proc._handle))):
        print("bake split: could not attach the copy to the main Blender")
