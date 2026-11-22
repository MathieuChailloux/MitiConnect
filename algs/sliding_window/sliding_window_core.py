# -*- coding: utf-8 -*-
"""
MitiConnect - sliding window indices : computational core.

Pure numpy / scipy module, NO QGIS dependency (testable with pytest).
numba is used when available (optional) for the per-pixel kernels;
otherwise an equivalent (slower) scipy.ndimage.generic_filter fallback is used.

Conventions
-----------
* A window is a disc of radius `radius` pixels centred on the pixel (centre included).
* Distances are expressed in pixels.
* Functions returning rasters never read/write files: arrays in, arrays out.
* `valid` is a boolean mask (True = data, False = nodata).
"""

import math

import numpy as np
try:
    from scipy import ndimage
    SCIPY_IMPORT_OK = True
except:
    SCIPY_IMPORT_OK = False


# --------------------------------------------------------------------------
# Constants (enum values are the same as the QGIS enum indices)
# --------------------------------------------------------------------------
NODATA = -9999.0

(FINAL_NONE, FINAL_LOG10, FINAL_EXP, FINAL_SQRT,
 FINAL_INDEX, FINAL_LOGINDEX) = range(6)
DIST_MIN, DIST_MIN_PLUS_ONE, DIST_MEDIAN = range(3)
COEFF_EXP, COEFF_LINEAR = range(2)

USE_NUMBA = True        # set to False to force the scipy fallback
last_backend = None     # "numba" or "scipy" : backend used by the last kernel call

if SCIPY_IMPORT_OK:
    _STRUCT_4 = ndimage.generate_binary_structure(2, 1)   # 4-connexity


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def valid_mask(arr, nodata):
    """Boolean mask of valid pixels (handles nodata None and NaN)."""
    if nodata is None:
        return np.ones(arr.shape, dtype=bool)
    if np.isnan(nodata):
        return ~np.isnan(arr)
    return arr != nodata


def circular_window(radius):
    """Return (footprint, dist) : boolean disc and matrix of distances to centre."""
    y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
    dist = np.hypot(x, y)
    return dist <= radius, dist


def window_offsets(radius):
    """Offsets (dy, dx) and distances of the window pixels, sorted by distance."""
    footprint, dist = circular_window(radius)
    dy, dx = np.nonzero(footprint)
    d = dist[dy, dx]
    order = np.argsort(d, kind="stable")
    return ((dy[order] - radius).astype(np.int64),
            (dx[order] - radius).astype(np.int64),
            d[order].astype(np.float64))


def distance_coefficient(d, radius, coeff_mode):
    """Distance weighting : exp(-d) or linear (radius - d) / radius (clipped at 0)."""
    d = np.asarray(d, dtype=np.float64)
    if coeff_mode == COEFF_EXP:
        return np.exp(-d)
    if coeff_mode == COEFF_LINEAR:
        return np.clip((radius - d) / radius, 0.0, None)
    raise ValueError("Unknown distance coefficient mode : %s" % coeff_mode)


# --------------------------------------------------------------------------
# Final functions
# --------------------------------------------------------------------------
def finalize(values, valid, mode=FINAL_NONE, vmin=None, vmax=None, nodata=NODATA):
    """
    Apply the final function on valid pixels and return a float32 array
    (nodata elsewhere, and wherever the result is not finite : log(0), overflow...).

    INDEX     : (v - vmin) / (vmax - vmin). vmin/vmax default to the min/max of the
                VALID pixels (nodata is never part of the statistics). When both are
                given (theoretical bounds), the result is clipped to [0, 1].
    LOGINDEX  : log then INDEX with data bounds.
    """
    v = np.asarray(values, dtype=np.float64).copy()
    ok = valid & np.isfinite(v)
    with np.errstate(all="ignore"):
        if mode == FINAL_NONE:
            pass
        elif mode == FINAL_LOG10:
            v = np.log10(v)
        elif mode == FINAL_EXP:
            v = np.exp(v)
        elif mode == FINAL_SQRT:
            v = np.sqrt(v)
        elif mode in (FINAL_INDEX, FINAL_LOGINDEX):
            if mode == FINAL_LOGINDEX:
                v = np.log(v)
                vmin = vmax = None
            ok &= np.isfinite(v)
            bounded = vmin is not None and vmax is not None
            if vmin is None:
                vmin = v[ok].min() if ok.any() else 0.0
            if vmax is None:
                vmax = v[ok].max() if ok.any() else 0.0
            span = vmax - vmin
            v = (v - vmin) / span if span > 0 else np.zeros_like(v)
            if bounded:
                v = np.clip(v, 0.0, 1.0)
        else:
            raise ValueError("Unknown final function mode : %s" % mode)
    ok &= np.isfinite(v)
    out = np.full(v.shape, nodata, dtype=np.float32)
    out[ok] = v[ok]
    return out


# --------------------------------------------------------------------------
# Neighbours count (4-connexity)
# --------------------------------------------------------------------------
def neighbours_count_4(arr):
    """Number of 4-neighbours having the same value as the pixel (0..4)."""
    same = np.zeros(arr.shape, dtype=np.uint8)
    same[1:, :] += arr[1:, :] == arr[:-1, :]
    same[:-1, :] += arr[:-1, :] == arr[1:, :]
    same[:, 1:] += arr[:, 1:] == arr[:, :-1]
    same[:, :-1] += arr[:, :-1] == arr[:, 1:]
    return same


# --------------------------------------------------------------------------
# Patch labelling
# --------------------------------------------------------------------------
def label_mask(mask):
    """4-connected labelling of a boolean mask (0 = background)."""
    return ndimage.label(mask, structure=_STRUCT_4)[0].astype(np.int32)


def label_patches(arr, valid):
    """
    Label the 4-connected patches of each class (unique labels over the raster,
    0 = nodata).
    """
    out = np.zeros(arr.shape, dtype=np.int32)
    offset = 0
    for c in np.unique(arr[valid]):
        lab, n = ndimage.label(arr == c, structure=_STRUCT_4)
        m = lab > 0
        out[m] = lab[m] + offset
        offset += n
    return out


# --------------------------------------------------------------------------
# Connectivity index (favorability classes) : 2 convolutions whatever the
# number of classes.
#   index(x) = sum_{p in window, class(p) listed} w(d_p)  +  radius * sum_{p} rank(p)
# --------------------------------------------------------------------------
def connectivity_index(arr, classes, ranks, radius, coeff_mode=COEFF_EXP):
    """
    classes : classes (ordered from unfavourable to very favourable)
    ranks   : rank of each class (0 for the least favourable). The quantity
              redistributed to a pixel is rank * radius.
    """
    footprint, dist = circular_window(radius)
    kernel = np.where(footprint, distance_coefficient(dist, radius, coeff_mode), 0.0)
    kernel = kernel.astype(np.float32)
    valid = np.zeros(arr.shape, dtype=np.float32)
    rank_arr = np.zeros(arr.shape, dtype=np.float32)
    for c, r in zip(classes, ranks):
        m = arr == c
        valid[m] = 1.0
        rank_arr[m] = r * radius
    kw = dict(mode="constant", cval=0.0)
    return (ndimage.correlate(valid, kernel, **kw)
            + ndimage.correlate(rank_arr, footprint.astype(np.float32), **kw))


def connectivity_bounds(radius, coeff_mode, max_rank):
    """Theoretical (min, max) of connectivity_index for a full (non truncated) window."""
    footprint, dist = circular_window(radius)
    w = float(distance_coefficient(dist[footprint], radius, coeff_mode).sum())
    return w, w + float(footprint.sum()) * max_rank * radius


# --------------------------------------------------------------------------
# Redistribution (surface index)
# --------------------------------------------------------------------------
def redistribute_by_class(values, arr, classes, quantile):
    """
    Add to every pixel of class c the cumulated `quantile` of `values` over the
    classes (taken in order up to c).
    """
    out = np.asarray(values, dtype=np.float32).copy()
    acc = 0.0
    for c in classes:
        m = arr == c
        if not m.any():
            continue
        q = np.nanquantile(values[m], quantile)
        if np.isfinite(q):
            acc += float(q)
        out[m] += acc
    return out


# --------------------------------------------------------------------------
# Per-pixel kernels (numba) - written in plain python, compiled lazily
# --------------------------------------------------------------------------
def _patch_area_kernel(lab, oy, ox):
    h, w = lab.shape
    out = np.zeros((h, w), np.uint32)
    for y in range(h):
        for x in range(w):
            lbl = lab[y, x]
            if lbl == 0:
                continue
            c = 0
            for k in range(oy.size):
                yy = y + oy[k]
                xx = x + ox[k]
                if yy >= 0 and yy < h and xx >= 0 and xx < w and lab[yy, xx] == lbl:
                    c += 1
            out[y, x] = c
    return out


def _isolation_kernel(lab, oy, ox, od, exponent, dist_offset, coeff_mode, radius):
    h, w = lab.shape
    n = oy.size
    out = np.zeros((h, w), np.float32)
    labs = np.empty(n, np.int64)
    cnt = np.empty(n, np.int64)
    dmin = np.empty(n, np.float64)
    for y in range(h):
        for x in range(w):
            m = 0
            for k in range(n):
                yy = y + oy[k]
                xx = x + ox[k]
                if yy < 0 or yy >= h or xx < 0 or xx >= w:
                    continue
                lbl = lab[yy, xx]
                if lbl == 0:
                    continue
                found = False
                for q in range(m):
                    if labs[q] == lbl:
                        cnt[q] += 1
                        if od[k] < dmin[q]:
                            dmin[q] = od[k]
                        found = True
                        break
                if not found:
                    labs[m] = lbl
                    cnt[m] = 1
                    dmin[m] = od[k]
                    m += 1
            s = 0.0
            for q in range(m):
                d = dmin[q] + dist_offset
                if coeff_mode == 0:
                    c = math.exp(-d)
                else:
                    c = (radius - d) / radius
                    if c < 0.0:
                        c = 0.0
                s += c * (float(cnt[q]) ** exponent)
            out[y, x] = s
    return out


def _quantile_kernel(arr, valid, oy, ox, od, q, use_class, class_id, nodata_out):
    # offsets are sorted by distance => collected distances are already sorted
    h, w = arr.shape
    n = oy.size
    out = np.empty((h, w), np.float32)
    buf = np.empty(n, np.float64)
    for y in range(h):
        for x in range(w):
            if not valid[y, x]:
                out[y, x] = nodata_out
                continue
            cell = class_id if use_class else arr[y, x]
            m = 0
            for k in range(n):
                yy = y + oy[k]
                xx = x + ox[k]
                if yy < 0 or yy >= h or xx < 0 or xx >= w:
                    continue
                if arr[yy, xx] == cell:
                    buf[m] = od[k]
                    m += 1
            if m == 0:
                out[y, x] = nodata_out
            else:
                pos = q * (m - 1)
                lo = int(math.floor(pos))
                hi = lo + 1 if lo + 1 < m else m - 1
                frac = pos - lo
                out[y, x] = buf[lo] * (1.0 - frac) + buf[hi] * frac
    return out


_kernels = {}


def _get_kernels():
    """Lazily compile the numba kernels. Returns None if numba is unavailable."""
    if not USE_NUMBA:
        return None
    if "k" not in _kernels:
        try:
            from numba import njit
            _kernels["k"] = {
                "patch_area": njit(_patch_area_kernel),
                "isolation": njit(_isolation_kernel),
                "quantile": njit(_quantile_kernel),
            }
        except Exception:
            _kernels["k"] = None
    return _kernels["k"]


def _run(name, fast_args, fallback):
    """Run the numba kernel `name` if possible, otherwise the scipy fallback."""
    global last_backend
    kernels = _get_kernels()
    if kernels is not None:
        try:
            res = kernels[name](*fast_args)
            last_backend = "numba"
            return res
        except Exception:
            pass    # compilation/runtime failure : use the fallback
    last_backend = "scipy"
    return fallback()


# --------------------------------------------------------------------------
# Patch area inside the window
# --------------------------------------------------------------------------
def patch_area_window(labels, radius):
    """For each labelled pixel : number of pixels of the same patch inside the window."""
    labels = np.ascontiguousarray(labels, dtype=np.int32)
    oy, ox, _ = window_offsets(radius)

    def fallback():
        footprint, _ = circular_window(radius)

        def f(a):
            c = a[len(a) // 2]
            return 0 if c == 0 else np.count_nonzero(a == c)
        return ndimage.generic_filter(labels, f, footprint=footprint,
                                      mode="constant", cval=0, output=np.uint32)
    return _run("patch_area", (labels, oy, ox), fallback)


# --------------------------------------------------------------------------
# Isolation index (Hanski-like) : sum_j coeff(d_j) * A_j ** exponent
#   A_j : number of pixels of patch j inside the window
#   d_j : distance from the centre to patch j (min, min + 1 or median)
# --------------------------------------------------------------------------
def isolation_index(labels, radius, exponent=2, dist_mode=DIST_MIN,
                    coeff_mode=COEFF_EXP):
    """Returns a float32 array, 0 where there is no patch inside the window."""
    global last_backend
    labels = np.ascontiguousarray(labels, dtype=np.int32)
    oy, ox, od = window_offsets(radius)
    dist_offset = 1.0 if dist_mode == DIST_MIN_PLUS_ONE else 0.0

    def fallback():
        footprint, dist = circular_window(radius)
        dflat = dist[footprint]

        def f(a):
            m = a != 0
            if not m.any():
                return 0.0
            labs, d = a[m], dflat[m]
            res = 0.0
            for v in np.unique(labs):
                dv = d[labs == v]
                dd = np.median(dv) if dist_mode == DIST_MEDIAN else dv.min() + dist_offset
                res += float(distance_coefficient(dd, radius, coeff_mode)) \
                    * float(dv.size) ** exponent
            return res
        return ndimage.generic_filter(labels, f, footprint=footprint,
                                      mode="constant", cval=0, output=np.float32)

    if dist_mode == DIST_MEDIAN:        # not implemented in the numba kernel
        last_backend = "scipy"
        return fallback()
    return _run("isolation",
                (labels, oy, ox, od, float(exponent), dist_offset,
                 int(coeff_mode), float(radius)),
                fallback)


def isolation_bounds(radius, exponent, dist_mode, coeff_mode):
    """Theoretical (min, max) : a single patch filling the window. (None, None) if unknown."""
    if dist_mode == DIST_MEDIAN:
        return None, None
    footprint, _ = circular_window(radius)
    d0 = 1.0 if dist_mode == DIST_MIN_PLUS_ONE else 0.0
    vmax = float(distance_coefficient(d0, radius, coeff_mode)) \
        * float(footprint.sum()) ** exponent
    return 0.0, vmax


# --------------------------------------------------------------------------
# Quantile of the distances to the pixels of a class inside the window
# --------------------------------------------------------------------------
def quantile_distance(arr, valid, radius, quantile, class_id=None):
    """
    For each valid pixel : quantile of the distances (in pixels) to the pixels
    of value `class_id` (or of the value of the pixel itself if class_id is None)
    inside the window. NODATA where undefined.
    """
    oy, ox, od = window_offsets(radius)
    use_class = class_id is not None
    cid = class_id if use_class else 0

    def fallback():
        footprint, dist = circular_window(radius)
        dflat = dist[footprint]
        work = arr.astype(np.float64)
        work[~valid] = np.nan

        def f(a):
            cell = cid if use_class else a[len(a) // 2]
            if np.isnan(cell):
                return NODATA
            d = dflat[a == cell]
            return NODATA if d.size == 0 else float(np.quantile(d, quantile))
        res = ndimage.generic_filter(work, f, footprint=footprint, mode="constant",
                                     cval=np.nan, output=np.float32)
        res[~valid] = NODATA
        return res
    return _run("quantile",
                (np.ascontiguousarray(arr), np.ascontiguousarray(valid), oy, ox, od,
                 float(quantile), use_class, cid, NODATA),
                fallback)
