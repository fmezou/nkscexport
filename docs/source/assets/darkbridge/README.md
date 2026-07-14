# DarkBridge — Graphical Assets

Visual identity for **DarkBridge**, an open-source tool that migrates Nikon
sidecar files (`.nksc`, XMP sidecars) into [Darktable](https://www.darktable.org/)
workflows — so photographers can switch from Nikon's proprietary software
without losing their edits.

---

## Design concept

The mark depicts a **three-arch bridge** — a full central arch flanked by two
half-arches — drawn in a minimal technical line style. Dashed vertical hangers
(suspenders) reinforce the engineering aesthetic. Two filled endpoint dots mark
the two worlds being connected: **Nikon** (left) and **Darktable** (right).

The colour palette is intentionally aligned with the
**Read the Docs (RTD) Sphinx theme** so the logo slots naturally into project
documentation.

| Token | Hex | Role |
|---|---|---|
| Background | `#1a2332` | Card / avatar fill |
| Card border | `#2d4a6e` | Subtle frame |
| Arch / pylons | `#2d7dd2` | Main structural lines |
| Deck / endpoints | `#4a9eff` | Accent — RTD link blue |
| Suspenders | `#2d7dd2` at 63 % opacity | Dashed hangers |
| Ground bar | `#243447` | Base shadow |
| Wordmark "Dark" | `#e8f0fe` | Near-white |
| Wordmark "Bridge" | `#4a9eff` | RTD blue |
| Tagline / sub-labels | `#4a7a9b` | Muted steel-blue |
| DB monogram bg | `#1e3a5f` | Recessed pill |

---

## File inventory

```
darkbridge_assets/
│
├── darkbridge-logo.svg               Full logo — icon + wordmark, dark background
├── darkbridge-logo-transparent.svg   Full logo — icon + wordmark, transparent background
├── darkbridge-icon.svg               Icon only (no wordmark), dark background, square
│
├── darkbridge-avatar-16.png          GitHub avatar  16 × 16 px  — dark background
├── darkbridge-avatar-32.png          GitHub avatar  32 × 32 px  — dark background
├── darkbridge-avatar-64.png          GitHub avatar  64 × 64 px  — dark background
│
├── darkbridge-avatar-16-transparent.png   16 × 16 px — transparent background
├── darkbridge-avatar-32-transparent.png   32 × 32 px — transparent background
├── darkbridge-avatar-64-transparent.png   64 × 64 px — transparent background
│
├── favicon.ico                        Multi-resolution favicon (16 / 32 / 48 px)
│
├── LICENSE                            MIT License covering all graphical assets
├── FONTS.txt                          Typeface specification and licensing notes
└── README.md                          This file
```

---

## Usage

### GitHub organisation avatar
Upload `darkbridge-avatar-64.png` (opaque) as the GitHub organisation profile
picture. GitHub will scale it automatically for smaller contexts.

### Sphinx / Read the Docs
```python
# conf.py
html_logo   = "_static/darkbridge-logo.svg"
html_favicon = "_static/favicon.ico"
```

Copy both files into your `docs/_static/` folder.

### README badge / header
```markdown
![DarkBridge](https://raw.githubusercontent.com/<org>/darkbridge/main/assets/darkbridge-logo.svg)
```

### Background context guide

| Context | Recommended file |
|---|---|
| Dark background (GitHub dark mode, terminal) | `darkbridge-logo.svg` |
| Light / white background (docs, print) | `darkbridge-logo-transparent.svg` |
| Any coloured background | `*-transparent` variants |
| Browser favicon | `favicon.ico` |
| Small avatar (< 64 px) | PNG avatar at matching size |

### Minimum legible size
- Wordmark logo: **height ≥ 40 px**
- Icon-only mark: **16 px** (use the pre-rendered PNG, not the SVG, below 32 px)

### What **not** to do
- Do not recolour the arches outside the defined blue palette.
- Do not add drop shadows, gradients, or glow effects.
- Do not stretch the mark non-uniformly.
- Do not place the opaque-background variant on a differently coloured surface.
- Do not separate "Dark" from "Bridge" in the wordmark.

---

## Typeface

**Inter** by Rasmus Andersson — SIL Open Font License 1.1.
See [`FONTS.txt`](FONTS.txt) for weight breakdown and CSS snippets.

| Element | Weight |
|---|---|
| Wordmark "Dark" | Inter ExtraBold 800 |
| Wordmark "Bridge" | Inter Light 300 |
| Tagline / labels | Inter Regular 400 |
| DB monogram | Inter Bold 700 |

---

## Regenerating raster assets

PNG avatars are generated from the same parametric drawing routine used to
produce `darkbridge-icon.svg`. To regenerate at a new resolution:

```bash
# Using Inkscape (recommended for SVG fidelity)
inkscape --export-type=png --export-width=128 \
         --export-filename=darkbridge-avatar-128.png \
         darkbridge-icon.svg

# Using cairosvg (Python)
pip install cairosvg
cairosvg darkbridge-icon.svg -o darkbridge-avatar-128.png -W 128 -H 128
```

---

## License

All graphical assets in this directory are released under the **MIT License**.
See [`LICENSE`](LICENSE) for the full text.

The Inter typeface is not included here and is governed separately by the
[SIL Open Font License 1.1](https://scripts.sil.org/OFL).
