from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, UploadFile

from baton_substrate.db import get_db
from baton_substrate.services import export_service

router = APIRouter(prefix="/missions", tags=["export"])


@router.post("/{mission_id}/export")
async def export_mission(mission_id: str) -> Response:
    async with get_db() as db:
        try:
            data = await export_service.export_mission_pack(db, mission_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={mission_id}.zip"},
    )


@router.post("/import")
async def import_mission(file: UploadFile) -> dict[str, str]:
    data = await file.read()
    async with get_db() as db:
        mission_id = await export_service.import_mission_pack(db, data)
    return {"mission_id": mission_id, "status": "imported"}
