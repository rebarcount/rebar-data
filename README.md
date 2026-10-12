# rebar-data

Reinforcing bar (rebar) sizes, nominal weights and areas, plus a small command-line
estimator for rectangular rebar grids. Plain CSV and Python, no dependencies.

## Why this exists

Estimating rebar always starts from the same small table: bar designation, nominal
diameter, weight per unit length, cross-sectional area. That table is published in
several places but rarely as a machine-readable file you can drop into a script or a
spreadsheet. This repository is that file, plus the arithmetic that usually comes
next.

## Contents

| Path | What it is |
| --- | --- |
| `data/rebar-imperial.csv` | US bar sizes #3 – #18: diameter, lb/ft, weight of 20 ft and 40 ft bars, area, bars per ton |
| `data/rebar-metric.csv` | Metric sizes 10 – 40 mm: kg/m, weight of a 12 m bar, area, bars per tonne |
| `tools/rebar_estimate.py` | Command-line estimator for a rectangular grid (slab, wall or footing) |

### `data/rebar-imperial.csv`

| Column | Meaning |
| --- | --- |
| `bar` | US bar designation. The number is the diameter in eighths of an inch, so #4 = 4/8 in = 1/2 in |
| `nominal_diameter_in` | Nominal diameter in inches |
| `weight_lb_per_ft` | Nominal weight in pounds per foot |
| `weight_lb_20ft_bar` | Weight of one 20 ft stock bar |
| `weight_lb_40ft_bar` | Weight of one 40 ft stock bar |
| `area_in2` | Nominal cross-sectional area in square inches |
| `bars_per_ton_40ft` | Whole 40 ft bars per short ton (2,000 lb), rounded down |

### `data/rebar-metric.csv`

| Column | Meaning |
| --- | --- |
| `size_mm` | Nominal diameter in millimetres |
| `weight_kg_per_m` | Nominal weight in kilograms per metre |
| `weight_kg_12m_bar` | Weight of one 12 m stock bar |
| `area_mm2` | Nominal cross-sectional area in square millimetres |
| `bars_per_tonne_12m` | Whole 12 m bars per tonne (1,000 kg), rounded down |

## The estimator

```
python tools/rebar_estimate.py --unit imperial --bar "#4" \
    --length 24 --width 20 --spacing 1 --edge 0.25 --stock 20
```

```
Bar                 #4  (0.668 lb/ft)
Grid                24 x 20 ft, spacing 1 ft, edge 0.25 ft

Bars along length   20  x 23.5 ft
Bars along width    24  x 19.5 ft
Total bar length    938 ft
Total weight        626.58 lb
Stock length        20 ft
Bars to buy         47
Weight to order     627.92 lb
```

Metric works the same way:

```
python tools/rebar_estimate.py --unit metric --bar 16 \
    --length 6 --width 7 --spacing 0.3 --edge 0.05 --stock 12
```

### The formulas it uses

With `L` = length, `W` = width, `s` = spacing and `e` = edge clearance:

```
usable length  Lu = L - 2e
usable width   Wu = W - 2e
bars across    nA = floor(Wu / s) + 1     # bars running along L
bars along     nB = floor(Lu / s) + 1     # bars running along W
total length   T  = nA * Lu + nB * Wu
weight         M  = T * w                 # w = nominal unit weight
bars to buy    p  = ceil(T / stock)
weight to order   = p * stock * w
```

The first bar sits on the edge clearance line and the last one falls inside the far
edge, which is why the count is `floor(usable / spacing) + 1`. Bar counts are rounded
down and bars-to-buy is rounded up, so the weight to order is always at least the
theoretical weight.

## Where the numbers come from

* US sizes: standard nominal values for deformed bars to ASTM A615 / A706.
* Metric sizes: nominal diameter with the standard density of steel, 7,850 kg/m³.
  (The common shortcut `d²/162` gives kg/m for `d` in mm; it agrees to about 0.1%.)

These are **nominal** values. Mill tolerance, deformation pattern and coating all move
the real weight a little, and stock lengths vary by supplier and region. For a
purchase order, use the figures your yard actually stocks.

## Also available

A browser version of this calculation, with a full cut list and metric/imperial
switching, runs at <https://rebarcount.com>.

## Cite this dataset

If you use these tables, please cite the Zenodo archive:

> rebarcount. (2026). *Rebar size, weight and area dataset (imperial #3–#18 and metric 10–40 mm)*. Zenodo. https://doi.org/10.5281/zenodo.23332321

## License

MIT. See `LICENSE`.
