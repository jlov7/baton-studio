from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, required=True, help="Output directory (e.g., dist)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Minimal demo artifacts (placeholder; real demo will run simulated agents).
    now = datetime.now(timezone.utc).isoformat()

    (out_dir / "demo_mission.json").write_text(
        json.dumps(
            {
                "mission_id": "demo",
                "created_at": now,
                "title": "Demo mission: substrate-native coordination",
                "goal": "Show baton arbitration + world model invariants + causal provenance",
            },
            indent=2,
        )
    )

    (out_dir / "demo_atlas.json").write_text(
        json.dumps(
            {
                "note": "placeholder",
                "events": [],
            },
            indent=2,
        )
    )

    print(f"Wrote demo artifacts to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
