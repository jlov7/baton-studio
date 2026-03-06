from __future__ import annotations

import argparse
import asyncio
from pathlib import Path


async def _run(out_dir: Path) -> None:
    from baton_substrate.demo.simulator import run_demo
    from baton_substrate.db import get_db
    from baton_substrate.services import export_service

    mission_id = await run_demo(delay=0.0)
    print(f"Demo completed. Mission ID: {mission_id}")

    async with get_db() as db:
        pack_bytes = await export_service.export_mission_pack(db, mission_id)

    out_dir.mkdir(parents=True, exist_ok=True)
    pack_path = out_dir / f"{mission_id}.zip"
    pack_path.write_bytes(pack_bytes)
    print(f"Wrote mission pack to {pack_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, required=True, help="Output directory (e.g., dist)")
    args = parser.parse_args()
    asyncio.run(_run(Path(args.out)))


if __name__ == "__main__":
    main()
