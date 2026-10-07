"""Refresh all data:  python -m vika_macro.update [yahoo fred worldbank valuations flows]"""
from __future__ import annotations

import logging
import sys

from .connectors import ALL


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    want = set(argv if argv is not None else sys.argv[1:])
    bad = 0
    for cls in ALL:
        c = cls()
        if want and c.name not in want:
            continue
        rec = c.run()
        print(f"{c.label:<16} {rec['status']:<8} series={rec['series']:<4} rows={rec['records']:<7} "
              f"last={rec['last_obs']}  {('; '.join(rec['errors'][:2]))[:120]}")
        bad += rec["status"] == "Error"
    return 0  # never fail the CI job just because one free source is down


if __name__ == "__main__":
    raise SystemExit(main())
