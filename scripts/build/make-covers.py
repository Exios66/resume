#!/usr/bin/env python3
"""Draw the project cover motifs in partials/covers/.

Run from the repository root: python3 scripts/build/make-covers.py
Each motif pictures a project's subject. None of them plots data. They draw with shared classes
(cv-*) that styles.css colours from the theme, so they carry no colours and no ids.

House style, so the fourteen read as one set:
- canvas 320 x 120, content inside a 20 px margin (the two full-bleed scenes excepted);
- one stroke weight; pages have radius 4, pills radius 7, nodes are a 9 px ring with a 3.5 px core;
- cards, pages and pills cast a soft offset shade; each motif has one focal element with a glow,
  and that element alone is hot pink (class cv-pop);
- curves are smooth cubic splines, never visible line segments.
"""
import math
import pathlib
import random

W, H = 320, 120
OUT = pathlib.Path(__file__).resolve().parent.parent.parent / "partials" / "covers"


def n(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if "." in f"{x:.1f}" else f"{x:.1f}"


def el(tag, cls, **a):
    attrs = "".join(f' {k.replace("_", "-")}="{n(v) if isinstance(v, (int, float)) else v}"' for k, v in a.items())
    return f'<{tag} class="{cls}"{attrs}/>'


def path(cls, d):
    return el("path", cls, d=d)


def circle(cls, x, y, r):
    return el("circle", cls, cx=x, cy=y, r=r)


def ellipse(cls, x, y, rx, ry):
    return el("ellipse", cls, cx=x, cy=y, rx=rx, ry=ry)


def rect(cls, x, y, w, h, rx=0):
    return el("rect", cls, x=x, y=y, width=w, height=h, rx=rx)


def group(transform, body):
    return f'<g transform="{transform}">{body}</g>'


def poly(pts, close=False):
    return "M" + " L".join(f"{n(x)} {n(y)}" for x, y in pts) + (" Z" if close else "")


def smooth(pts):
    """A cubic spline through the points (Catmull-Rom), so sampled curves have no corners."""
    d = f"M{n(pts[0][0])} {n(pts[0][1])}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(p2[0])} {n(p2[1])}"
    return d


def shaded(x, y, w, h, rx, cls="cv-page"):
    return rect("cv-shade", x + 3, y + 3, w, h, rx) + rect(cls, x, y, w, h, rx)


def page(x, y, w=40, h=52, lines=4, shade=True):
    out = shaded(x, y, w, h, 4) if shade else rect("cv-page", x, y, w, h, 4)
    for k in range(lines):
        out += path("cv-line", f"M{n(x + 7)} {n(y + 11 + k * 9)} h{n((w - 14) * (0.55 if k == lines - 1 else 1))}")
    return out


def pill(x, y, w=66, h=24, line=0.55, mark=None, cls="cv-page"):
    out = shaded(x, y, w, h, 7, cls)
    start = x + 12
    if mark:
        out += circle(mark, x + 13, y + h / 2, 3.2)
        start = x + 22
    return out + path("cv-line", f"M{n(start)} {n(y + h / 2)} h{n((x + w - 12 - start) * line)}")


def node(x, y, r=9, core=3.5):
    return circle("cv-page", x, y, r) + circle("cv-dot", x, y, core)


def branch(x0, y0, x1, y1, cls="cv-accent"):
    mid = (x0 + x1) / 2
    return path(cls, f"M{n(x0)} {n(y0)} C{n(mid + 6)} {n(y0)} {n(mid - 6)} {n(y1)} {n(x1)} {n(y1)}")


def glow(x, y, r=30):
    return circle("cv-glow", x, y, r)


def wave_laboratory():
    # a container ship on a long swell, with shorter wave trains layered beneath it
    def surf(y0, parts):
        return lambda x: y0 + sum(a * math.sin(2 * math.pi * x / lam + ph) for a, lam, ph in parts)

    def band(fn, line_cls, step):
        d = smooth([(x, fn(x)) for x in range(-16, W + 17, step)])
        return path("cv-soft", d + f" L{W + 8} {H} L-8 {H} Z") + path(line_cls, d)

    swell = surf(62, [(8, 176, 0.5), (2.2, 62, 1.7)])
    out = glow(252, 36, 30) + circle("cv-under", 252, 36, 14) + circle("cv-accent cv-pop", 252, 36, 14)
    out += path("cv-line cv-faint", "M0 51 H58 M168 51 H230 M274 51 H320")
    out += path("cv-line", "M26 24 q4.5 -4.5 9 0 q4.5 -4.5 9 0 M52 34 q3.5 -3.5 7 0 q3.5 -3.5 7 0")
    sx = 112
    slope = (swell(sx + 8) - swell(sx - 8)) / 16
    boxes = ""
    for row, (first, count) in enumerate(((-18, 5), (-18, 4), (-10, 2))):
        for k in range(count):
            cls = "cv-crate cv-soft" if (row + k) % 3 == 0 else "cv-crate"
            boxes += rect(cls, first + k * 8, -16 - row * 6, 8, 6)
    ship = (
        boxes
        + path("cv-fill", "M-40 -10 H24 L26 -13 L44 -14 Q40 -3 33 3 H-34 Q-39 -1 -40 -10 Z")
        + path("cv-fill", "M-34 -10 V-24 H-22 V-10 Z M-36 -24 V-27 H-20 V-24 Z M-30 -27 V-33 H-25 V-27 Z")
        + path("cv-accent", "M-27.5 -33 V-38 M34 -13.5 V-23 M34 -23 L24 -10")
        + path("cv-cut", "M-32 -20.5 H-24 M-37 -3 H37")
    )
    out += group(f"translate({sx} {n(swell(sx) + 1.5)}) rotate({n(math.degrees(math.atan(slope)) * 0.35)})", ship)
    out += band(swell, "cv-accent", 16)
    out += path("cv-cut", "M70 62.5 q5 -3 10 -1 M150 60 q6 -3.5 12 -0.5")
    out += band(surf(80, [(4.5, 96, 2.4), (1.4, 37, 0.3)]), "cv-line", 12)
    out += band(surf(94, [(2.6, 54, 1.1), (0.9, 23, 2.6)]), "cv-line", 8)
    out += band(surf(106, [(1.4, 30, 0.2), (0.5, 13, 1.2)]), "cv-line cv-faint", 5)
    return out


def neuron_atlas():
    # a field of neurons; a few fire together, and one is selected for steering
    rng = random.Random(11)
    out, act = "", []
    for r in range(6):
        for c in range(20):
            x, y = 17 + c * 15, 17 + r * 17
            if rng.random() < 0.12 and 1 <= c <= 18:
                act.append((x, y))
            else:
                out += circle("cv-dotsoft", x, y, 2.2)
    edges = set()
    for i, a in enumerate(act):
        for j in sorted(range(len(act)), key=lambda k: math.dist(a, act[k]))[1:3]:
            if math.dist(a, act[j]) < 70:
                edges.add(tuple(sorted((i, j))))
    fx, fy = min(act, key=lambda p: abs(p[0] - 160) + abs(p[1] - 60))
    out = glow(fx, fy, 34) + out
    out += path("cv-line", " ".join(f"M{act[i][0]} {act[i][1]} L{act[j][0]} {act[j][1]}" for i, j in sorted(edges)))
    for i, (x, y) in enumerate(act):
        out += circle("cv-dot", x, y, 4.2 if i % 3 == 0 else 3)
    return out + f'<g class="cv-pop">' + circle("cv-dot", fx, fy, 3.4) + circle("cv-accent", fx, fy, 9) + circle("cv-line", fx, fy, 14) + "</g>"


def digital_mailroom():
    # an inbox tray of legal documents; the router sends each one to the cheapest step that can handle it,
    # drawn as three steps of rising cost, with the dearer steps only as dashed fallbacks
    out = rect("cv-page", 32, 40, 30, 40, 3) + rect("cv-page", 39, 33, 30, 40, 3) + shaded(46, 26, 30, 40, 3)
    out += path("cv-line", "M52 35 h18 M52 42 h18 M52 49 h18 M52 56 h10")
    out += shaded(24, 66, 64, 32, 5) + path("cv-accent", "M46 82 h20")
    out += glow(120, 60, 26) + path("cv-accent", "M91 60 H112")
    out += path("cv-line", "M150 104 H196 V74 H242 V44 H296")
    steps = ((173, 98, 5.5, 2.2, 196, 104), (219, 65, 8.5, 3.2, 242, 74), (269, 31.5, 12, 4.4, 296, 44))
    for k, (x, y, r, core, edge, tread) in enumerate(steps):
        cls = "cv-accent" if k == 0 else "cv-accent cv-dash"
        out += path(cls, f"M128 60 C{n(128 + (x - r - 128) * 0.5)} 60 {n(128 + (x - r - 128) * 0.5)} {y} {n(x - r - 1)} {y}")
        out += circle("cv-page", x, y, r) + circle("cv-dot" if k == 0 else "cv-dotsoft", x, y, core)
        for c in range(k + 1):
            out += circle("cv-dotsoft", edge - 8 - c * 7, tread + 7, 2.2)
    return out + circle("cv-dot cv-pop", 120, 60, 7.5)


def mailroom_ml():
    # a calibration curve against the diagonal; above the confidence gate the classifier answers,
    # below it the document goes to the fallback
    x0, y0, s = 40, 102, 84
    gate = x0 + 0.7 * s
    out = rect("cv-soft", gate, y0 - s, x0 + s - gate, s)
    out += path("cv-line cv-faint", f"M{x0} {y0 - s} V{y0} H{x0 + s}")
    for t in (0.25, 0.5, 0.75):
        out += path("cv-line cv-faint", f"M{n(x0 + t * s)} {y0} v-3 M{x0} {n(y0 - t * s)} h3")
    out += path("cv-line cv-dash", f"M{x0} {y0} L{x0 + s} {y0 - s}")
    pts = [(x0 + t * s, y0 - (t + 0.26 * math.sin(math.pi * t) * (1 - t)) * s) for t in (0.08, 0.22, 0.36, 0.5, 0.64, 0.78, 0.92)]
    out += path("cv-accent", smooth(pts)) + "".join(circle("cv-dot", x, y, 3) for x, y in pts)
    out += path("cv-accent cv-dash", f"M{n(gate)} {y0} v-{s}")
    jx = x0 + s + 28
    out += glow(jx, 60, 26) + path("cv-accent", f"M{x0 + s + 5} 60 H{jx - 8}") + circle("cv-dot cv-pop", jx, 60, 7.5)
    out += branch(jx + 8, 60, jx + 56, 36) + pill(jx + 58, 23, 74, 26, 0.9, "cv-dot")
    out += branch(jx + 8, 60, jx + 56, 84, "cv-accent cv-dash") + pill(jx + 58, 71, 74, 26, 0.6, "cv-dotsoft")
    return out


def mailroom_reloaded():
    # agents run in a fixed order; one step can escalate; every decision lands in the audit log
    out = page(24, 22, 36, 46, 3)
    xs = (96, 136, 176, 216)
    out += path("cv-accent", f"M64 45 H{xs[0] - 9}")
    for i, x in enumerate(xs):
        out += path("cv-line cv-dash", f"M{x} 54 V82")
        if i < 3:
            out += path("cv-accent", f"M{x + 9} 45 H{xs[i + 1] - 9}")
    out += path("cv-accent", f"M{xs[3] + 9} 45 H244") + pill(246, 33, 50, 24, 0.9, "cv-dot")
    out += path("cv-accent cv-dash cv-pop", f"M{xs[2]} 36 V18 H250") + circle("cv-under", 261, 18, 8) + circle("cv-accent cv-pop", 261, 18, 8) + path("cv-accent cv-pop", "M261 14 v5 M261 22 v.4")
    out += glow(xs[2], 45, 24) + "".join(node(x, 45) for x in xs)
    out += shaded(80, 82, 152, 26, 5)
    for i, x in enumerate(xs):
        out += circle("cv-dot", x, 90.5, 2.2) + path("cv-line", f"M{x - 10} 99.5 h{(20, 14, 20, 16)[i]}")
    return out


def rvl_cdip_classifier():
    # a skewed scan of a letter, a vision model, and the sixteen RVL-CDIP classes as page glyphs:
    # the model picks letter; memo, the class it most often confuses with letter, is ringed
    scan = shaded(-28, -38, 56, 76, 3) + path("cv-line", "M-20 -27 h16 M-20 -21 h11")
    scan += "".join(path("cv-line", f"M-20 {y} h{w}") for y, w in ((-9, 40), (-2, 40), (5, 40), (12, 26)))
    scan += path("cv-accent", "M2 27 q4 -7 8 -1 t7 -2 t5 1")
    out = group("translate(60 60) rotate(-5)", scan)
    out += glow(150, 60, 30) + path("cv-accent", "M98 60 H124 M176 60 H200")
    out += path("cv-page", "M126 60 Q150 36 174 60 Q150 84 126 60 Z") + path("cv-accent", "M126 60 Q150 36 174 60 Q150 84 126 60 Z")
    out += circle("cv-accent", 150, 60, 10) + circle("cv-dot", 150, 60, 5)
    glyphs = (
        "M4 6h12v9h-12z M4 6l6 5l6-5",                                      # email
        "M5 5h4v4h-4z M11 7h4 M5 11h4v4h-4z M11 13h4",                      # form
        "M4 8q2-3 4 0t4 0t4 0 M4 13q2-3 4 0t4 0",                           # handwritten
        "M5 5h10v6h-10z M5 14h10",                                          # advertisement
        "M5 5h10 M5 8h4.5 M5 11h4.5 M5 14h4.5 M10.5 8h4.5 M10.5 11h4.5 M10.5 14h4.5",  # scientific report
        "M5 5h10 M7 7.5h6 M5 10.5h10 M5 13h10 M5 15.5h6",                   # scientific publication
        "M5 6h10 M5 9.5h10 M5 13h6 M11.5 15.5q1.5-2.5 3.5 0",               # letter
        "M4.5 5h11v10h-11z M4.5 8.5h11 M4.5 12h11 M9 5v10",                 # specification
        "M4 7h4l1.5 1.5h6.5v7h-12z",                                        # file folder
        "M4.5 5.5h11 M4.5 8.5h3v6.5h-3z M9.5 8.5h6 M9.5 11.5h6 M9.5 14.5h6",  # news article
        "M5 5.5h4 M5 8h6 M4.5 10.5h11 M5 13.5h10 M5 16h6",                  # memo
        "M5 6h5 M13 6h2 M5 9.5h5 M13 9.5h2 M5 13h5 M13 13h2 M12 15.5h3.5",  # budget
        "M5 5.5h5 M5 9h10 M5 12h10 M10 15h5",                               # invoice
        "M4 6h12v8h-12z M7 9h6 M10 14v2.5",                                 # presentation
        "M5 7l1.2 1.2l2-2.4 M10 7h5 M5 13l1.2 1.2l2-2.4 M10 13h5",          # questionnaire
        "M5 5.5h3v3h-3z M10 6h5 M10 8.5h3 M5 12h10 M5 15h7",                # resume
    )
    for i, d in enumerate(glyphs):
        cx, cy = 205 + (i % 4) * 23, 15 + (i // 4) * 23
        if i == 6:
            body = rect("cv-shade", cx + 3, cy + 3, 20, 20, 4) + rect("cv-fill cv-pop", cx, cy, 20, 20, 4)
            out += body + group(f"translate({cx} {cy})", path("cv-cut", d))
        else:
            out += rect("cv-page", cx, cy, 20, 20, 4) + group(f"translate({cx} {cy})", path("cv-line", d))
            if i == 10:
                out += rect("cv-accent cv-dash", cx - 2.5, cy - 2.5, 25, 25, 6)
    return out


def mailroom_corpus_eda():
    # documents from several public sources, gathered into one audited dataset
    out = ""
    docs = [(22, 14, 0), (58, 8, 1), (40, 46, 2), (78, 40, 0), (24, 78, 1), (64, 76, 2)]
    for x, y, k in docs:
        out += shaded(x, y, 22, 28, 3)
        out += path("cv-line", f"M{x + 5} {y + 8} h12 M{x + 5} {y + 14} h{(12, 8, 10)[k]} M{x + 5} {y + 20} h{(7, 12, 5)[k]}")
    for y0 in (26, 60, 94):
        out += branch(108, y0, 166, 60, "cv-accent" if y0 == 60 else "cv-line")
    cx, w, top, bottom = 204, 36, 28, 90
    out += path("cv-shade", f"M{cx - w + 3} {top + 3} V{bottom + 3} A{w} 10 0 0 0 {cx + w + 3} {bottom + 3} V{top + 3} Z")
    out += path("cv-page", f"M{cx - w} {top} V{bottom} A{w} 10 0 0 0 {cx + w} {bottom} V{top}")
    for y in (top + 21, top + 42):
        out += path("cv-line", f"M{cx - w} {y} A{w} 10 0 0 0 {cx + w} {y}")
    out += ellipse("cv-page", cx, top, w, 10) + ellipse("cv-soft", cx, top, w, 10)
    out += glow(274, 60, 26) + path("cv-accent", f"M{cx + w + 3} 60 H258")
    out += circle("cv-fill cv-pop", 274, 60, 15) + path("cv-tick", "M266.5 60.5 l5 5 l9 -10.5")
    return out


def aeroglobe():
    # a globe with its graticule, routes between cities, and one aircraft in flight
    cx, cy, r = 160, 62, 46
    out = glow(cx, cy, 54) + circle("cv-page", cx, cy, r)
    out += path("cv-soft", f"M{cx} {cy - r} A{r} {r} 0 0 1 {cx} {cy + r} A{r * 0.42} {r} 0 0 0 {cx} {cy - r} Z")
    for rx in (r * 0.36, r * 0.74):
        out += ellipse("cv-line cv-faint", cx, cy, rx, r)
    out += path("cv-line cv-faint", f"M{cx} {cy - r} V{cy + r}")
    for dy in (-26, 0, 26):
        half = math.sqrt(r * r - dy * dy)
        out += path("cv-line cv-faint", f"M{n(cx - half)} {cy + dy} Q{cx} {cy + dy + 9} {n(cx + half)} {cy + dy}")
    out += circle("cv-accent", cx, cy, r)
    cities = {"a": (134, 46), "b": (178, 38), "c": (187, 76), "d": (141, 84), "w": (34, 80), "e": (290, 38), "s": (266, 100)}
    routes = [("a", "c", (166, 44), ""), ("d", "b", (150, 52), ""), ("w", "a", (74, 18), " cv-dash"),
              ("c", "e", (246, 34), " cv-dash"), ("d", "s", (204, 122), " cv-dash")]
    for a, b, ctrl, dash in routes:
        (x0, y0), (x1, y1) = cities[a], cities[b]
        out += path("cv-accent" + dash, f"M{x0} {y0} Q{ctrl[0]} {ctrl[1]} {x1} {y1}")
    for name, (x, y) in cities.items():
        out += circle("cv-dot", x, y, 3.2 if name in "abcd" else 2.6)
    (x0, y0), (qx, qy), (x1, y1), t = cities["c"], (246, 34), cities["e"], 0.56
    px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * qx + t * t * x1
    py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * qy + t * t * y1
    ang = math.degrees(math.atan2(2 * (1 - t) * (qy - y0) + 2 * t * (y1 - qy), 2 * (1 - t) * (qx - x0) + 2 * t * (x1 - qx)))
    plane = ("M10 0 Q8 -1.7 4 -1.7 L1 -1.7 L-3 -9 L-5.6 -9 L-3.6 -1.7 L-8 -1.5 L-10 -4.6 L-11.6 -4.6 L-10.9 0 "
             "L-11.6 4.6 L-10 4.6 L-8 1.5 L-3.6 1.7 L-5.6 9 L-3 9 L1 1.7 L4 1.7 Q8 1.7 10 0 Z")
    out += group(f"translate({n(px)} {n(py)}) rotate({n(ang)})", path("cv-fill cv-pop", plane))
    return out


def mapreduce_reloaded():
    # input splits, map workers, the shuffle, reduce workers, one output. One map worker has died:
    # its split is handed to a backup worker, which finishes the task (the fault-injection tests)
    ys4, ys2 = (21, 47, 73, 99), (40, 80)
    dead, bx, by = 2, 132, 88
    out = glow(bx, by, 24)
    for y in ys4:
        out += shaded(24, y - 9, 36, 18, 4) + path("cv-line", f"M32 {y} h20")
    for i, y in enumerate(ys4):
        out += path("cv-line cv-dash" if i == dead else "cv-accent", f"M60 {y} H{91 if i == dead else 93}")
        x0, y0 = (bx + 9, by) if i == dead else (111, y)
        for j, y2 in enumerate(ys2):
            out += branch(x0, y0, 196, y2, "cv-accent" if (i + j) % 2 == 0 else "cv-line")
    out += path("cv-accent cv-dash cv-pop", f"M60 {ys4[dead] + 5} C84 {by + 4} 100 {by} {bx - 10} {by}")
    for y2 in ys2:
        out += branch(216, y2, 254, 60)
    for i, y in enumerate(ys4):
        if i == dead:
            out += circle("cv-under", 102, y, 9) + circle("cv-line cv-dash", 102, y, 9) + path("cv-line", f"M98 {y - 4} l8 8 M106 {y - 4} l-8 8")
        else:
            out += node(102, y)
    out += circle("cv-under", bx, by, 9) + circle("cv-accent cv-pop", bx, by, 9) + circle("cv-dot cv-pop", bx, by, 3.5)
    out += "".join(circle("cv-page", 206, y2, 10) + circle("cv-dot", 206, y2, 4) for y2 in ys2)
    out += shaded(256, 43, 42, 34, 5) + path("cv-line", "M265 53.5 h24 M265 60 h24 M265 66.5 h15")
    return out


def psychometric_digital_twin():
    # a respondent, a persona built to answer as them, and their answers side by side on survey scales
    def person(x, cls, shade):
        body = f"M{x - 24} 100 V84 A24 22 0 0 1 {x + 24} 84 V100 Z"
        out = (circle("cv-shade", x + 3, 43, 13) + path("cv-shade", f"M{x - 21} 103 V87 A24 22 0 0 1 {x + 27} 87 V103 Z")) if shade else ""
        return out + circle(cls, x, 40, 13) + path(cls, body)

    out = person(52, "cv-page", True) + person(268, "cv-accent cv-dash", False)
    rows = ((24, 0.30, 0.52), (42, 0.62, 0.50), (60, 0.45, 0.70), (78, 0.78, 0.60), (96, 0.22, 0.40))
    x0, x1 = 102, 218
    out += glow(160, 60, 44)
    for y, real, twin in rows:
        out += path("cv-line", f"M{x0} {y} H{x1}")
        out += path("cv-line cv-faint", " ".join(f"M{n(x0 + t * (x1 - x0))} {y - 3} v6" for t in (0, 0.25, 0.5, 0.75, 1)))
        a, b = x0 + real * (x1 - x0), x0 + twin * (x1 - x0)
        out += path("cv-accent cv-pop", f"M{n(a)} {y} H{n(b)}") + circle("cv-dot", a, y, 4.2) + circle("cv-page", b, y, 4.2)
    return out


def natd():
    # two chatbots, one helpful and one deceptive, and the EEG recorded while people talk to them
    def bubble(x, y, w, h, tail, cls):
        r, d = 9, 1 if tail < x + w / 2 else -1
        return path(cls, f"M{x + r} {y} H{x + w - r} Q{x + w} {y} {x + w} {y + r} V{y + h - r} Q{x + w} {y + h} {x + w - r} {y + h} "
                    f"H{tail + 9 * (d > 0)} L{tail - 3 * d} {y + h + 9} L{tail - 9 * (d < 0)} {y + h} H{x + r} "
                    f"Q{x} {y + h} {x} {y + h - r} V{y + r} Q{x} {y} {x + r} {y} Z")

    out = path("cv-shade", "M36 22 h62 a9 9 0 0 1 9 9 v12 a9 9 0 0 1 -9 9 h-62 a9 9 0 0 1 -9 -9 v-12 a9 9 0 0 1 9 -9 Z")
    out += bubble(24, 16, 80, 30, 38, "cv-page") + path("cv-line", "M36 27 h56 M36 35 h36") + circle("cv-dot", 96, 22, 0)
    out += bubble(44, 62, 80, 30, 108, "cv-under") + bubble(44, 62, 80, 30, 108, "cv-soft") + bubble(44, 62, 80, 30, 108, "cv-accent")
    out += path("cv-line", "M56 73 h56 M56 81 h30")
    out += rect("cv-soft", 224, 12, 30, 96, 5)
    rng = random.Random(4)
    for k, y in enumerate((24, 48, 72, 96)):
        pts, phase = [], rng.random() * 6
        for x in range(152, 301, 3):
            burst = math.exp(-(((x - 152) / 148 - 0.59) ** 2) / 0.006) if k == 1 else 0
            v = 3 * math.sin(x / 6 + phase) + 1.8 * math.sin(x / 2.6 + phase * 2) + burst * 10 * math.sin(x / 2.1)
            pts.append((x, y + v))
        out += path("cv-accent cv-pop" if k == 1 else "cv-line", smooth(pts)) + circle("cv-dot cv-pop" if k == 1 else "cv-dotsoft", 144, y, 2.6)
    return out


def llm_personas():
    # a bench of five personas, their votes weighed, and a written ruling
    cx, base, rad = 112, 132, 96
    seats = [(cx + rad * math.cos(math.radians(a)), base + rad * math.sin(math.radians(a))) for a in (214, 241, 270, 299, 326)]
    out = path("cv-line", f"M{n(seats[0][0])} {n(seats[0][1])} A{rad} {rad} 0 0 1 {n(seats[-1][0])} {n(seats[-1][1])}")
    out += glow(cx, 78, 30)
    for i, (x, y) in enumerate(seats):
        out += circle("cv-page", x, y, 10) + circle("cv-dot" if i in (0, 2, 3) else "cv-dotsoft", x, y, 4)
    out += path("cv-accent", f"M{cx} 62 V102 M{cx - 15} 102 H{cx + 15} M{cx - 25} 72 L{cx + 25} 64") + circle("cv-dot", cx, 62, 2.6)
    for dx, y in ((-25, 72), (25, 64)):
        out += path("cv-accent", f"M{cx + dx - 9} {y + 15} L{cx + dx} {y} L{cx + dx + 9} {y + 15}")
        out += path("cv-fill", f"M{cx + dx - 11} {y + 15} a11 6.5 0 0 0 22 0 Z")
    out += path("cv-accent", "M204 60 H230")
    out += shaded(234, 20, 54, 80, 4)
    out += path("cv-line", "M243 32 h36 M243 41 h36 M243 50 h36 M243 59 h22 M243 86 h16")
    out += circle("cv-fill cv-pop", 273, 84, 7.5) + circle("cv-cut", 273, 84, 4)
    return out


def langtons_ant():
    # the real automaton: one ant on an empty grid, its first steps, and the path it has just walked
    cells, x, y, dx, dy = set(), 0, 0, 0, -1
    for _ in range(1040):
        if (x, y) in cells:
            cells.remove((x, y)); dx, dy = dy, -dx
        else:
            cells.add((x, y)); dx, dy = -dy, dx
        x, y = x + dx, y + dy
    xs = [c[0] for c in cells] + [x]
    ys = [c[1] for c in cells] + [y]
    s = 4
    assert max(ys) - min(ys) + 1 <= H / s - 2, "the ant pattern must fit the cover"
    ox = round((W / s - (max(xs) - min(xs) + 1)) / 2) - min(xs)
    oy = round((H / s - (max(ys) - min(ys) + 1)) / 2) - min(ys)
    grid = " ".join(f"M{gx} 0 V{H}" for gx in range(0, W + 1, s * 2)) + " " + " ".join(f"M0 {gy} H{W}" for gy in range(0, H + 1, s * 2))
    ax, ay = (x + ox) * s + s / 2, (y + oy) * s + s / 2
    out = path("cv-grid", grid) + glow(ax, ay, 26)
    # merge each row's neighbouring cells into one rectangle to keep the file small
    d = []
    for cy in sorted({c[1] for c in cells}):
        row = sorted(c[0] for c in cells if c[1] == cy)
        start = prev = row[0]
        for cx in row[1:] + [None]:
            if cx is None or cx != prev + 1:
                d.append(f"M{(start + ox) * s} {(cy + oy) * s}h{(prev - start + 1) * s}v{s}h-{(prev - start + 1) * s}z")
                start = cx
            prev = cx
    out += path("cv-fill", "".join(d))
    heading = math.degrees(math.atan2(dy, dx))
    out += circle("cv-under", ax, ay, 7) + circle("cv-accent cv-pop", ax, ay, 7) + group(f"translate({n(ax)} {n(ay)}) rotate({n(heading)})", path("cv-fill cv-pop", "M4 0 L-2.5 -3.2 L-1 0 L-2.5 3.2 Z"))
    return out


def degen_llms():
    # one chip wallet shared by a terminal game, a card table and a pixel overworld
    out = shaded(22, 22, 96, 70, 6) + path("cv-line", "M22 36 H118")
    out += circle("cv-dotsoft", 31, 29, 2) + circle("cv-dotsoft", 39, 29, 2) + circle("cv-dotsoft", 47, 29, 2)
    out += path("cv-accent", "M34 48 l8 6 l-8 6 M48 60 h14") + rect("cv-fill", 66, 51, 5, 10, 1)
    out += path("cv-line", "M34 72 h52 M34 81 h30")
    out += glow(168, 76, 34)
    for cx, count in ((150, 5), (186, 3)):
        top = 96 - (count - 1) * 9
        out += ellipse("cv-shade", cx + 3, 105, 17, 6)
        for k in range(count):
            y = 96 - k * 9
            out += path("cv-page", f"M{cx - 17} {y} v6 a17 6 0 0 0 34 0 v-6")
            out += path("cv-line", f"M{cx - 9} {y + 5.2} v6 M{cx} {y + 6} v6 M{cx + 9} {y + 5.2} v6")
        out += ellipse("cv-page", cx, top, 17, 6) + ellipse("cv-soft", cx, top, 17, 6) + ellipse("cv-accent", cx, top, 9.5, 3.2)
    out += group("rotate(-10 246 60)", shaded(224, 24, 46, 66, 6))
    pip = "M0 -11 L7.5 0 L0 11 L-7.5 0 Z"
    out += group("rotate(7 266 62)", shaded(244, 26, 46, 66, 6) + group("translate(267 59)", path("cv-fill cv-pop", pip))
                 + group("translate(252 36) scale(.36)", path("cv-fill", pip)) + group("translate(282 82) scale(.36)", path("cv-fill", pip)))
    return out


MOTIFS = {
    "wave-laboratory": wave_laboratory, "neuron-atlas": neuron_atlas, "digital-mailroom": digital_mailroom,
    "mailroom-ml": mailroom_ml, "mailroom-reloaded": mailroom_reloaded, "rvl-cdip-classifier": rvl_cdip_classifier,
    "mailroom-corpus-eda": mailroom_corpus_eda, "aeroglobe": aeroglobe, "mapreduce-reloaded": mapreduce_reloaded,
    "psychometric-digital-twin": psychometric_digital_twin, "natd": natd, "llm-personas": llm_personas,
    "langtons-ant": langtons_ant, "degen-llms": degen_llms,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, draw in MOTIFS.items():
        body = draw()
        (OUT / f"{slug}.svg").write_text(
            f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" focusable="false">{body}</svg>\n')
        print(f"{slug}.svg {len(body)} bytes")
