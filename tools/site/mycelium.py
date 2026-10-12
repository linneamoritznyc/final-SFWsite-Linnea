"""Draw a branching hyphal network as SVG paths. Each path carries data-s (when it
starts growing, 0..1, set by how far right it starts) so js/site.js can grow the
network from left to right as the reader scrolls.
Usage: python3 tools/site/mycelium.py SEED WIDTH HEIGHT > fragment.svg"""
import math, random, sys


def network(seed=7, W=1600, H=260, roots=3):
    rnd = random.Random(seed)
    segs, tips = [], []

    def seg(x, y, ang, w, depth, leader, lane=None):
        if len(segs) > 150:
            return
        pts = [(x, y)]
        n = rnd.randint(5, 8) if leader else rnd.randint(3, 7) - min(depth, 3)
        for _ in range(max(n, 2)):
            ang += rnd.uniform(-.32, .32)
            if leader:
                ang = max(-.6, min(.6, ang * .85 + (lane - y) * .004))  # leaders head right, near their lane
            step = rnd.uniform(22, 36) if leader else rnd.uniform(14, 26)
            x += math.cos(ang) * step
            y += math.sin(ang) * step
            if y < 10 or y > H - 10:
                ang = -ang
                y = max(10, min(H - 10, y))
            pts.append((x, y))
        x0 = pts[0][0]
        d = "M%.0f,%.0f" % pts[0]
        for i in range(1, len(pts) - 1):
            mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            d += " Q%.0f,%.0f %.0f,%.0f" % (pts[i][0], pts[i][1], mx, my)
        d += " L%.0f,%.0f" % pts[-1]
        segs.append((d, w, x0))
        # side branches
        if depth < 4:
            for i in range(1, len(pts)):
                if rnd.random() < (.45 if leader else .3):
                    bx, by = pts[i]
                    side = rnd.choice([-1, 1])
                    seg(bx, by, ang + side * rnd.uniform(.5, 1.2), max(w * .6, .6), depth + 1, False)
        if leader and x < W:
            seg(x, y, ang, max(w * .97, 1.4), depth, True, lane)
        elif not leader and rnd.random() < .5:
            tips.append((x, y, x))

    for r in range(roots):
        lane = H * (r + .5) / roots
        seg(-10, lane + rnd.uniform(-20, 20), rnd.uniform(-.25, .25), 2.2, 0, True, lane)

    out = ['<svg class="mycelium__svg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">' % (W, H)]
    for d, w, x0 in segs:
        out.append('<path d="%s" pathLength="1" stroke-width="%.2f" data-s="%.3f"/>' % (d, w, max(0, min(1, x0 / W))))
    for x, y, x0 in tips:
        if 0 < x < W and 0 < y < H:
            out.append('<circle cx="%.0f" cy="%.0f" r="2.4" data-s="%.3f"/>' % (x, y, max(0, min(.98, x0 / W + .04))))
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    print(network(int(a[0]) if a else 7, int(a[1]) if len(a) > 1 else 1600, int(a[2]) if len(a) > 2 else 260))
