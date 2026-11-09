#!/usr/bin/env python3
"""Publish this slice's training labels and query inputs into data/instances/.

For each fluid instance this writes the labelled design dataset (every base
hull and pairwise morph at the label angles of attack, i.e. the simulated "CFD
runs" a method may learn from, including their simulation error) and the
query inputs whose coefficients are scored.
Query ground truth is never written; it is recomputed at evaluation time.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval.train import hydro as H
from eval.train.evaluate import INSTANCES


def export(root: Path) -> None:
    for iid, seed in INSTANCES.items():
        inst = H.make_instance(seed)
        folder = root / iid
        folder.mkdir(parents=True, exist_ok=True)
        lines = ["shape_id,aoa_deg,cd,cl"]
        for sid, aoa, cd, cl in H.simulated_labels(seed, inst):
            lines.append(f"{sid},{aoa:g},{cd:.8g},{cl:.8g}")
        (folder / "labels.csv").write_text("\n".join(lines) + "\n")
        queries = [
            {"weights": q["weights"], "shape": [round(v, 8) for v in q["shape"]], "aoa_deg": q["aoa_deg"]}
            for q in H.query_inputs(iid)
        ]
        (folder / "queries.json").write_text(json.dumps({"instance": iid, "queries": queries}) + "\n")
        print(f"wrote {folder}: {len(lines) - 1} labels, {len(queries)} queries")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/instances")
    export(Path(parser.parse_args().root))


if __name__ == "__main__":
    main()
