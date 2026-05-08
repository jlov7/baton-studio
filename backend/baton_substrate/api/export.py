from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, UploadFile

from baton_substrate.config import settings
import baton_substrate.db.engine as db_engine
from baton_substrate.services import export_service

router = APIRouter(prefix="/missions", tags=["export"])


@router.post("/{mission_id}/export")
async def export_mission(mission_id: str) -> Response:
    async with db_engine.get_db() as db:
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
    if len(data) > settings.max_mission_pack_bytes:
        raise HTTPException(status_code=413, detail="Mission pack exceeds upload size limit")
    async with db_engine.get_db() as db:
        try:
            mission_id = await export_service.import_mission_pack(db, data)
        except export_service.DuplicateMissionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from e
        except export_service.MissionPackError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
    return {"mission_id": mission_id, "status": "imported"}
