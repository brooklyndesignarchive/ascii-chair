# ascii chair

A Jean Prouvé Standard chair (Vitra), extracted from a CAD file and rendered as a rotating ASCII animation.

**[View it live](https://brooklyndesignarchive.github.io/ascii-chair/)** — drag horizontally to spin, vertically to tilt.

## How it works

1. The original `Standard_3D.dwg` (AutoCAD 2010) was converted to DXF with [LibreDWG](https://www.gnu.org/software/libredwg/)
2. `render.py` walks the block-insert hierarchy with [ezdxf](https://ezdxf.mozman.at/) and extracts the 3D meshes in world space — 4,398 vertices, 4,166 triangles
3. The mesh is embedded in `index.html`, where a small JavaScript software renderer draws it live: z-buffer triangle rasterization at 2× supersampling, Lambert shading mapped onto a 23-glyph brightness ramp

## Files

- `index.html` — the live ASCII viewer (self-contained, no dependencies)
- `render.py` — the original Python renderer / mesh-extraction pipeline
- `chair_spin.py` + `chair_frames.json` — terminal version: `python3 chair_spin.py`
