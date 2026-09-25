from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TeamReportOut, DirectReportOut, NetworkMemberOut
from app.services.hierarchy import get_team_report

router = APIRouter(prefix="/reports", tags=["Reporting"])


@router.get("/team", response_model=TeamReportOut)
async def get_my_team(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    direct, deeper = await get_team_report(db, current_user)

    direct_reports = [DirectReportOut.model_validate(d) for d in direct]
    network = [NetworkMemberOut.model_validate(d) for d in deeper]

    return TeamReportOut(
        direct_reports=direct_reports,
        network=network,
        total_team_size=len(direct_reports) + len(network),
    )
