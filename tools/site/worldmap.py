"""Write img/world-land.svg (country shapes, used as a mask so the land shows soil) and
img/world-borders.svg (thin country borders on top), from Natural Earth 1:110m countries
(public domain) via world-atlas 2.0.2 (countries-110m.json). Equirectangular, 84N to 58S.
Usage: python3 tools/site/worldmap.py path/to/countries-110m.json"""
import json, sys

LAT_N, LAT_S, W = 84.0, -58.0, 1000.0
H = W * (LAT_N - LAT_S) / 360.0


def xy(lon, lat):
    return (lon + 180.0) / 360.0 * W, (LAT_N - lat) / (LAT_N - LAT_S) * H


def main(src):
    t = json.load(open(src))
    sc, tr = t["transform"]["scale"], t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts += p if not pts else p[1:]
        return pts

    paths = []
    for g in t["objects"]["countries"]["geometries"]:
        if g.get("properties", {}).get("name") == "Antarctica" or not g.get("arcs"):
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        d = []
        for poly in polys:
            for r in poly:
                pts = [xy(lon, lat) for lon, lat in ring(r)]
                # drop rings that wrap the antimeridian badly (tiny slivers)
                if max(p[0] for p in pts) - min(p[0] for p in pts) > W * .9:
                    continue
                d.append("M" + "L".join("%.1f,%.1f" % p for p in pts) + "Z")
        if d:
            paths.append("".join(d))
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">' % (W, round(H))
    open("img/world-land.svg", "w").write(head + '<path fill="#000" d="%s"/></svg>' % "".join(paths))
    open("img/world-borders.svg", "w").write(head + '<path fill="none" stroke="#F4F1EA" stroke-width=".7" stroke-linejoin="round" d="%s"/></svg>' % "".join(paths))
    print("viewBox", W, round(H))


if __name__ == "__main__":
    main(sys.argv[1])
