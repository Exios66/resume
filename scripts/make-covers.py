#!/usr/bin/env python3
"""Draw the project cover motifs in partials/covers/.

Run from the repository root: python3 scripts/make-covers.py
Each motif pictures a project's subject. None of them plots data. They draw with shared classes
(cv-*) that styles.css colours from the theme, so they carry no colours and no ids.
"""
import math
import pathlib
import random

W, H = 320, 120
OUT = pathlib.Path(__file__).resolve().parent.parent / "partials" / "covers"


def n(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def el(tag, cls, **a):
    attrs = "".join(f' {k.replace("_", "-")}="{n(v) if isinstance(v, (int, float)) else v}"' for k, v in a.items())
    return f'<{tag} class="{cls}"{attrs}/>'


def path(cls, d):
    return el("path", cls, d=d)


def circle(cls, x, y, r):
    return el("circle", cls, cx=x, cy=y, r=r)


def rect(cls, x, y, w, h, rx=0):
    return el("rect", cls, x=x, y=y, width=w, height=h, rx=rx)


def poly(pts, close=False):
    return "M" + " L".join(f"{n(x)} {n(y)}" for x, y in pts) + (" Z" if close else "")


def page(x, y, w=40, h=52, lines=4):
    out = rect("cv-page", x, y, w, h, 4)
    for k in range(lines):
        out += path("cv-line", f"M{n(x + 7)} {n(y + 11 + k * 9)} h{n((w - 14) * (0.55 if k == lines - 1 else 1))}")
    return out


def pill(x, y, w=66, h=24, line=0.55):
    return rect("cv-page", x, y, w, h, 6) + path("cv-line", f"M{n(x + 12)} {n(y + h / 2)} h{n((w - 24) * line)}")


def branch(x0, y0, x1, y1, cls="cv-accent"):
    mid = (x0 + x1) / 2
    return path(cls, f"M{n(x0)} {n(y0)} C{n(mid + 6)} {n(y0)} {n(mid - 6)} {n(y1)} {n(x1)} {n(y1)}")


def wave_laboratory():
    def surf(y0, parts):
        return lambda x: y0 + sum(a * math.sin(2 * math.pi * x / lam + ph) for a, lam, ph in parts)

    def band(fn, line_cls):
        pts = [(x, round(fn(x), 1)) for x in range(-4, W + 8, 4)]
        d = poly(pts)
        return path("cv-soft", d + f" L{W + 4} {H} L-4 {H} Z") + path(line_cls, d)

    swell = surf(60, [(8, 176, 0.5), (2.2, 62, 1.7)])
    out = ""
    # sun on the horizon, with a broken column of light under it
    out += circle("cv-line", 250, 34, 15) + path("cv-line cv-faint", "M0 49.5 H226 M274 49.5 H320")
    # ship: hull, deckhouse, funnel, container stack and foremast, pitched to the slope of the swell
    sx = 112
    slope = (swell(sx + 6) - swell(sx - 6)) / 12
    ship = (
        path("cv-fill", "M-36 -9 H37 Q33 -1 24 2 H-28 Q-34 -2 -36 -9 Z")
        + path("cv-fill", "M-31 -9 V-24 H-19 V-9 Z M-27 -24 V-30 H-22 V-24 Z")
        + path("cv-page", "M-15 -9 V-16 H-4 V-9 M-4 -16 H7 V-9 M7 -16 H18 V-9 M-15 -16 V-23 H-4 V-16 M-4 -23 H7 V-16")
        + path("cv-accent", "M28 -9 V-19 M-36 -9 H37")
    )
    out += f'<g transform="translate({sx} {n(swell(sx) + 1)}) rotate({n(math.degrees(math.atan(slope)) * 0.45)})">{ship}</g>'
    out += band(swell, "cv-accent")
    out += band(surf(78, [(4.5, 96, 2.4), (1.4, 37, 0.3)]), "cv-line")
    out += band(surf(93, [(2.6, 54, 1.1), (0.9, 23, 2.6)]), "cv-line")
    out += band(surf(105, [(1.4, 30, 0.2), (0.5, 13, 1.2)]), "cv-line cv-faint")
    return out


def neuron_atlas():
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
    out += path("cv-line", " ".join(f"M{act[i][0]} {act[i][1]} L{act[j][0]} {act[j][1]}" for i, j in sorted(edges)))
    for i, (x, y) in enumerate(act):
        out += circle("cv-dot", x, y, 4 if i % 3 == 0 else 3)
    x, y = min(act, key=lambda p: abs(p[0] - 160) + abs(p[1] - 60))
    return out + circle("cv-accent", x, y, 9)


def digital_mailroom():
    out = rect("cv-page", 34, 38, 44, 58, 4) + rect("cv-page", 42, 30, 44, 58, 4) + page(50, 22, 44, 58)
    out += path("cv-accent", "M100 51 H138") + circle("cv-dot", 146, 51, 7)
    for y, line in ((24, 0.9), (60, 0.6), (96, 0.75)):
        out += branch(153, 51, 212, y) + pill(214, y - 12, line=line)
    return out


def mailroom_ml():
    x0, y0, s = 44, 102, 84
    gate = x0 + 0.7 * s
    out = path("cv-line cv-faint", f"M{x0} {y0 - s} V{y0} H{x0 + s}")
    out += path("cv-line cv-dash", f"M{x0} {y0} L{x0 + s} {y0 - s}")
    out += rect("cv-soft", gate, y0 - s, x0 + s - gate, s)
    pts = [(x0 + t * s, y0 - (t + 0.26 * math.sin(math.pi * t) * (1 - t)) * s) for t in (0.08, 0.22, 0.36, 0.5, 0.64, 0.78, 0.92)]
    out += path("cv-accent", poly(pts)) + "".join(circle("cv-dot", x, y, 3) for x, y in pts)
    out += path("cv-accent cv-dash", f"M{n(gate)} {y0} v-{s}")
    jx = x0 + s + 26
    out += path("cv-accent", f"M{x0 + s + 4} 60 H{jx - 7}") + circle("cv-dot", jx, 60, 7)
    for y, line in ((36, 0.9), (84, 0.6)):
        out += branch(jx + 7, 60, jx + 58, y) + pill(jx + 60, y - 13, 72, 26, line)
    return out


def mailroom_reloaded():
    # agents run in a fixed order; one step escalates; every decision lands in the audit log
    out = page(26, 22, 36, 46, 3)
    xs = (96, 136, 176, 216)
    out += path("cv-accent", f"M66 45 H{xs[0] - 9}")
    for i, x in enumerate(xs):
        out += circle("cv-page", x, 45, 9) + circle("cv-dot", x, 45, 3.5)
        if i < 3:
            out += path("cv-accent", f"M{x + 9} 45 H{xs[i + 1] - 9}")
        out += path("cv-line cv-dash", f"M{x} 54 V{80 + i * 0}")
    out += path("cv-accent", f"M{xs[3] + 9} 45 H246") + pill(248, 33, 46, 24, 0.9)
    out += path("cv-accent cv-dash", f"M{xs[2]} 36 V20 H246") + rect("cv-page", 248, 9, 46, 20, 10)
    out += circle("cv-dot", 259, 19, 3)
    out += rect("cv-page", 80, 80, 152, 28, 5)
    for i, x in enumerate(xs):
        out += circle("cv-dot", x, 89, 2.2) + path("cv-line", f"M{x - 10} 99 h{(20, 14, 20, 16)[i]}")
    return out


def rvl_cdip_classifier():
    # a scanned page, a vision model, sixteen classes with one chosen
    x, y = 34, 20
    out = rect("cv-page", x, y, 58, 78, 4) + rect("cv-soft", x + 8, y + 9, 42, 22)
    out += path("cv-line", f"M{x + 8} {y + 31} l12 -12 l9 8 l8 -7 l13 11")
    for k in range(4):
        out += path("cv-line", f"M{x + 8} {y + 42 + k * 9} h{(42, 42, 34, 22)[k]}")
    out += path("cv-accent", "M100 59 H126")
    out += path("cv-accent", "M130 59 Q152 37 174 59 Q152 81 130 59 Z") + circle("cv-dot", 152, 59, 6.5)
    out += path("cv-accent", "M178 59 H204")
    for r in range(4):
        for c in range(4):
            cls = "cv-fill" if (r, c) == (1, 2) else "cv-page"
            out += rect(cls, 210 + c * 21, 19 + r * 21, 16, 16, 3)
    return out


def mailroom_corpus_eda():
    # documents from several public sources, gathered into one audited dataset
    out = ""
    docs = [(22, 14, 0), (58, 8, 1), (40, 46, 2), (78, 40, 0), (24, 78, 1), (64, 76, 2)]
    for x, y, k in docs:
        out += rect("cv-page", x, y, 22, 28, 3)
        out += path("cv-line", f"M{x + 5} {y + 8} h12 M{x + 5} {y + 14} h{(12, 8, 10)[k]} M{x + 5} {y + 20} h{(7, 12, 5)[k]}")
    for y0 in (26, 60, 92):
        out += branch(104, y0, 168, 60, "cv-accent" if y0 == 60 else "cv-line")
    cx, w, top = 204, 34, 30
    for i in range(3):
        y = top + i * 22
        out += path("cv-page", f"M{cx - w} {y} v16 a{w} 9 0 0 0 {2 * w} 0 v-16")
    out += el("ellipse", "cv-page", cx=cx, cy=top, rx=w, ry=9)
    out += el("ellipse", "cv-soft", cx=cx, cy=top, rx=w, ry=9)
    out += circle("cv-fill", 272, 60, 15) + path("cv-tick", "M264.5 60.5 l5 5 l9 -10.5")
    out += path("cv-accent", "M240 60 H255")
    return out


def aeroglobe():
    cx, cy, r = 160, 62, 47
    out = circle("cv-soft", cx, cy, r) + circle("cv-accent", cx, cy, r)
    for rx in (16, 33):
        out += el("ellipse", "cv-line cv-faint", cx=cx, cy=cy, rx=rx, ry=r)
    out += path("cv-line cv-faint", f"M{cx} {cy - r} V{cy + r}")
    for dy in (-27, 0, 27):
        half = math.sqrt(r * r - dy * dy)
        out += path("cv-line cv-faint", f"M{n(cx - half)} {cy + dy} Q{cx} {cy + dy + 9} {n(cx + half)} {cy + dy}")
    routes = [((38, 84), (148, 44), -46), ((132, 78), (286, 40), -40), ((176, 34), (262, 92), 22), ((60, 30), (124, 58), -14)]
    for (x0, y0), (x1, y1), lift in routes:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + lift
        out += path("cv-accent cv-dash", f"M{x0} {y0} Q{n(mx)} {n(my)} {x1} {y1}")
        out += circle("cv-dot", x0, y0, 3) + circle("cv-dot", x1, y1, 3)
    # one aircraft on the longest route
    out += '<g transform="translate(212 44) rotate(-12) scale(1.35)">' + path("cv-fill", "M9 0 L-5 -2.2 L-8 -8 L-10 -8 L-8.5 -2 L-12 -1.5 L-13.5 -4 L-15 -4 L-14 0 L-15 4 L-13.5 4 L-12 1.5 L-8.5 2 L-10 8 L-8 8 L-5 2.2 Z") + "</g>"
    return out


def mapreduce_reloaded():
    # input splits, map workers, the shuffle, reduce workers, one output
    ys4 = (22, 47, 72, 97)
    ys2 = (40, 80)
    out = ""
    for y in ys4:
        out += rect("cv-page", 26, y - 9, 34, 18, 4) + path("cv-line", f"M34 {y} h18")
        out += path("cv-accent", f"M60 {y} H98") + circle("cv-page", 108, y, 9) + circle("cv-dot", 108, y, 3.5)
    for i, y in enumerate(ys4):
        for j, y2 in enumerate(ys2):
            out += branch(117, y, 196, y2, "cv-accent" if (i + j) % 2 == 0 else "cv-line")
    for y2 in ys2:
        out += circle("cv-page", 206, y2, 10) + circle("cv-dot", 206, y2, 4)
        out += branch(216, y2, 254, 60)
    out += rect("cv-page", 256, 44, 40, 32, 5) + path("cv-line", "M265 54 h22 M265 60 h22 M265 66 h14")
    return out


def psychometric_digital_twin():
    # a respondent, a persona built to answer as them, and their answers side by side on survey scales
    def person(x, cls):
        return circle(cls, x, 42, 13) + path(cls, f"M{x - 26} 98 a26 26 0 0 1 52 0")

    out = person(54, "cv-page") + person(266, "cv-accent cv-dash")
    rows = ((30, 0.30, 0.52), (48, 0.62, 0.50), (66, 0.45, 0.70), (84, 0.78, 0.60), (102, 0.22, 0.40))
    x0, x1 = 104, 216
    for y, real, twin in rows:
        out += path("cv-line", f"M{x0} {y} H{x1}")
        for t in (0, 0.25, 0.5, 0.75, 1):
            out += path("cv-line cv-faint", f"M{n(x0 + t * (x1 - x0))} {y - 3} v6")
        a, b = x0 + real * (x1 - x0), x0 + twin * (x1 - x0)
        out += path("cv-accent", f"M{n(a)} {y} H{n(b)}") + circle("cv-dot", a, y, 4) + circle("cv-page", b, y, 4)
    return out


def natd():
    # two chatbots, one helpful and one deceptive, and the EEG recorded while people talk to them
    def bubble(x, y, cls, flip):
        tail = f"M{x + 14} {y + 28} l-6 10 l14 -10" if not flip else f"M{x + 62} {y + 28} l6 10 l-14 -10"
        return rect(cls, x, y, 76, 28, 9) + path(cls, tail) + path("cv-line", f"M{x + 12} {y + 10} h52 M{x + 12} {y + 18} h34")

    out = bubble(24, 16, "cv-page", False) + bubble(40, 66, "cv-accent cv-dash", True)
    rng = random.Random(4)
    for k, y in enumerate((24, 46, 68, 90)):
        pts, phase = [], rng.random() * 6
        for x in range(146, 300, 2):
            t = (x - 146) / 154
            burst = math.exp(-((t - 0.58) ** 2) / 0.012) if k == 1 else 0
            v = 3.2 * math.sin(x / 5.5 + phase) + 2 * math.sin(x / 2.3 + phase * 2) + burst * 9 * math.sin(x / 1.9)
            pts.append((x, y + v))
        out += path("cv-accent" if k == 1 else "cv-line", poly(pts))
        out += circle("cv-dot", 140, y, 2.4)
    out += rect("cv-soft", 222, 12, 30, 92, 4)
    return out


def llm_personas():
    # a bench of personas, their votes, and a written ruling
    cx, cy = 118, 104
    out = ""
    seats = []
    for i in range(5):
        a = math.radians(200 + i * 35)
        seats.append((cx + 78 * math.cos(a), cy + 78 * math.sin(a) * 0.95))
    for i, (x, y) in enumerate(seats):
        out += circle("cv-page", x, y, 10) + circle("cv-fill" if i in (0, 1, 3) else "cv-dotsoft", x, y, 4)
    # scales
    out += path("cv-accent", f"M{cx} {cy - 44} V{cy - 4} M{cx - 14} {cy - 4} H{cx + 14} M{cx - 26} {cy - 36} L{cx + 26} {cy - 44}")
    for dx, dy in ((-26, -36), (26, -44)):
        out += path("cv-accent", f"M{cx + dx - 10} {cy + dy + 16} L{cx + dx} {cy + dy} L{cx + dx + 10} {cy + dy + 16}")
        out += path("cv-fill", f"M{cx + dx - 11} {cy + dy + 16} a11 7 0 0 0 22 0 Z")
    out += path("cv-accent", "M206 60 H232")
    out += page(236, 22, 52, 76, 5) + circle("cv-fill", 276, 86, 7)
    return out


def langtons_ant():
    # the real automaton: one ant, the first few hundred steps from an empty grid
    cells, x, y, dx, dy = set(), 0, 0, 0, -1
    for _ in range(900):
        if (x, y) in cells:
            cells.remove((x, y)); dx, dy = dy, -dx
        else:
            cells.add((x, y)); dx, dy = -dy, dx
        x, y = x + dx, y + dy
    xs = [c[0] for c in cells] + [x]
    ys = [c[1] for c in cells] + [y]
    s = 5
    assert max(ys) - min(ys) + 1 <= H / s - 2, 'the ant pattern must fit the cover'
    ox = round((W / s - (max(xs) - min(xs) + 1)) / 2) - min(xs)
    oy = round((H / s - (max(ys) - min(ys) + 1)) / 2) - min(ys)
    out = path("cv-grid", " ".join(f"M{gx} 0 V{H}" for gx in range(0, W + 1, s * 2)) + " " + " ".join(f"M0 {gy} H{W}" for gy in range(0, H + 1, s * 2)))
    out += path("cv-fill", " ".join(f"M{(cx + ox) * s} {(cy + oy) * s}h{s}v{s}h-{s}z" for cx, cy in sorted(cells)))
    ax, ay = (x + ox) * s + s / 2, (y + oy) * s + s / 2
    return out + circle("cv-page", ax, ay, 6.5) + circle("cv-dot", ax, ay, 2.6)


def degen_llms():
    # one chip wallet shared by a terminal game, a card table and a pixel overworld
    out = rect("cv-page", 24, 22, 92, 68, 6) + path("cv-line", "M24 36 H116")
    out += circle("cv-dotsoft", 33, 29, 2) + circle("cv-dotsoft", 41, 29, 2) + circle("cv-dotsoft", 49, 29, 2)
    out += path("cv-accent", "M36 50 l8 6 l-8 6 M50 62 h14") + path("cv-line", "M36 76 h46")
    for i, (cx, count) in enumerate(((150, 5), (184, 3))):
        for k in range(count):
            y = 92 - k * 9
            out += path("cv-page", f"M{cx - 16} {y} v6 a16 6 0 0 0 32 0 v-6")
            out += el("ellipse", "cv-page", cx=cx, cy=y, rx=16, ry=6)
        out += el("ellipse", "cv-soft", cx=cx, cy=92 - (count - 1) * 9, rx=16, ry=6)
        out += circle("cv-dot", cx, 92 - (count - 1) * 9, 2.2)
    out += '<g transform="rotate(-9 244 60)">' + rect("cv-page", 222, 24, 46, 66, 6) + "</g>"
    out += '<g transform="rotate(8 262 62)">' + rect("cv-page", 240, 26, 46, 66, 6)
    out += path("cv-fill", "M263 44 l9 13 l-9 13 l-9 -13 Z") + circle("cv-dot", 247, 34, 2) + circle("cv-dot", 279, 84, 2) + "</g>"
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
