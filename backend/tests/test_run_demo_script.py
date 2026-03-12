from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from types import SimpleNamespace

from baton_substrate.scripts import run_demo as run_demo_script


async def test_run_demo_writes_stable_demo_pack_name(
    tmp_path,
    monkeypatch,
) -> None:
    async def fake_run_demo(delay: float = 0.0) -> str:
        assert delay == 0.0
        return "mis_demo"

    @asynccontextmanager
    async def fake_get_db():
        yield object()

    async def fake_export_mission_pack(_db: object, mission_id: str) -> bytes:
        assert mission_id == "mis_demo"
        return b"demo-pack"

    monkeypatch.setitem(
        sys.modules,
        "baton_substrate.demo.simulator",
        SimpleNamespace(run_demo=fake_run_demo),
    )
    monkeypatch.setitem(
        sys.modules,
        "baton_substrate.db",
        SimpleNamespace(get_db=fake_get_db),
    )
    monkeypatch.setitem(
        sys.modules,
        "baton_substrate.services",
        SimpleNamespace(
            export_service=SimpleNamespace(export_mission_pack=fake_export_mission_pack),
        ),
    )

    await run_demo_script._run(tmp_path)

    assert (tmp_path / "demo_pack.zip").read_bytes() == b"demo-pack"
    assert list(tmp_path.glob("mis_*.zip")) == []
