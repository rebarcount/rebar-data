#!/usr/bin/env python3
"""Rebar quantity estimator for a rectangular grid (slab, wall or footing).

No third-party dependencies. Python 3.8+.

What it does
------------
Given a rectangle, a bar spacing, an edge clearance and a bar size, it works out:

  * how many bars run in each direction,
  * the cut length of each bar,
  * the total length of bar,
  * the total weight,
  * the number of stock bars you would have to buy, and the weight to order.

Formulas (documented on purpose - no hidden constants)
------------------------------------------------------
Let L = length, W = width, s = spacing, e = edge clearance (all in the same unit).

  usable length  Lu = L - 2e
  usable width   Wu = W - 2e
  bars across    nA = floor(Wu / s) + 1      # bars running along L, spread over W
  bars along     nB = floor(Lu / s) + 1      # bars running along W, spread over L
  cut length     each bar in group A = Lu ; each bar in group B = Wu
  total length   T  = nA * Lu + nB * Wu
  weight         M  = T * w                  # w = nominal unit weight of the bar
  pieces bought  p  = ceil(T / stock)  (if a stock length is given)
  weight to order   = p * stock * w

The layout model is the usual one for a rectangular mat: the first bar sits on the
edge clearance line and the last one sits inside the far edge, so the count is
floor(usable / spacing) + 1. Bar count is always rounded DOWN (you cannot buy a
fraction of a bar); the weight to order is therefore >= the theoretical weight.

Nominal unit weights are the standard published values for deformed bars
(ASTM A615 / A706 for the US sizes; 7850 kg/m3 steel density for the metric
sizes). They are the same numbers as in data/rebar-imperial.csv and
data/rebar-metric.csv in this repository.

Usage
-----
  python rebar_estimate.py --unit imperial --bar "#4" --length 24 --width 20 --spacing 1 --edge 0.25 --stock 20
  python rebar_estimate.py --unit metric --bar 16 --length 6 --width 7 --spacing 0.3 --edge 0.05 --stock 12

Outputs a short text report. Exit code 0.
"""

import argparse
import math
import sys

# Nominal unit weights. imperial: lb/ft keyed by bar designations.
# metric: kg/m keyed by nominal diameter in mm.
IMPERIAL = {
    "#3": 0.376, "#4": 0.668, "#5": 1.043, "#6": 1.502, "#7": 2.044,
    "#8": 2.670, "#9": 3.400, "#10": 4.303, "#11": 5.313, "#14": 7.650,
    "#18": 13.600,
}
METRIC = {10: 0.617, 12: 0.888, 16: 1.578, 20: 2.466, 25: 3.853,
          28: 4.834, 32: 6.313, 40: 9.865}

LEN_UNIT = {"imperial": "ft", "metric": "m"}
WT_UNIT = {"imperial": "lb", "metric": "kg"}


def estimate(length, width, spacing, edge, unit_weight, stock=None):
    """Return a dict with the quantities. Units are whatever you passed in."""
    lu = length - 2 * edge
    wu = width - 2 * edge
    if lu <= 0 or wu <= 0:
        raise ValueError("Edge clearance is larger than the slab - nothing left to reinforce.")
    if spacing <= 0:
        raise ValueError("Spacing must be greater than zero.")

    n_a = math.floor(wu / spacing) + 1   # bars running along the length
    n_b = math.floor(lu / spacing) + 1   # bars running along the width
    len_a = n_a * lu
    len_b = n_b * wu
    total_len = len_a + len_b
    weight = total_len * unit_weight

    pieces = None
    order_weight = None
    if stock and stock > 0:
        pieces = math.ceil(total_len / stock)
        order_weight = pieces * stock * unit_weight

    return {
        "bars_along_length": n_a,
        "bars_along_width": n_b,
        "cut_length_a": lu,
        "cut_length_b": wu,
        "length_group_a": len_a,
        "length_group_b": len_b,
        "total_length": total_len,
        "weight": weight,
        "pieces_to_buy": pieces,
        "weight_to_order": order_weight,
    }


def main():
    p = argparse.ArgumentParser(description="Rebar quantity estimator for a rectangular grid.")
    p.add_argument("--unit", choices=["imperial", "metric"], required=True)
    p.add_argument("--bar", required=True, help='Bar size: "#4" (imperial) or 16 (metric, mm)')
    p.add_argument("--length", type=float, required=True)
    p.add_argument("--width", type=float, required=True)
    p.add_argument("--spacing", type=float, required=True)
    p.add_argument("--edge", type=float, default=0.0, help="Edge clearance, default 0")
    p.add_argument("--stock", type=float, default=0.0,
                   help="Stock bar length, default 0 (= do not work out pieces)")
    a = p.parse_args()

    if a.unit == "imperial":
        key = a.bar if a.bar.startswith("#") else "#" + a.bar
        if key not in IMPERIAL:
            sys.exit("Unknown US bar size %r. Known: %s" % (a.bar, ", ".join(IMPERIAL)))
        uw = IMPERIAL[key]
        label = key
    else:
        try:
            key = int(a.bar)
        except ValueError:
            sys.exit("Metric bar size must be a whole number of millimetres.")
        if key not in METRIC:
            sys.exit("Unknown metric size %r. Known: %s" % (a.bar, ", ".join(map(str, sorted(METRIC)))))
        uw = METRIC[key]
        label = "%d mm" % key

    r = estimate(a.length, a.width, a.spacing, a.edge, uw, a.stock or None)
    lu_, wu_ = LEN_UNIT[a.unit], WT_UNIT[a.unit]

    print("Bar                 %s  (%g %s/%s)" % (label, uw, wu_, lu_))
    print("Grid                %g x %g %s, spacing %g %s, edge %g %s"
          % (a.length, a.width, lu_, a.spacing, lu_, a.edge, lu_))
    print("")
    print("Bars along length   %d  x %g %s" % (r["bars_along_length"], r["cut_length_a"], lu_))
    print("Bars along width    %d  x %g %s" % (r["bars_along_width"], r["cut_length_b"], lu_))
    print("Total bar length    %g %s" % (round(r["total_length"], 3), lu_))
    print("Total weight        %g %s" % (round(r["weight"], 2), wu_))
    if r["pieces_to_buy"]:
        print("Stock length        %g %s" % (a.stock, lu_))
        print("Bars to buy         %d" % r["pieces_to_buy"])
        print("Weight to order     %g %s" % (round(r["weight_to_order"], 2), wu_))


if __name__ == "__main__":
    main()
