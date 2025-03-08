from fastapi import APIRouter
from scehema import AnalyseBody



router = APIRouter()

@router.post("/analyse")
async def analyse(
    req_body: AnalyseBody,

) -> dict:
    

    return 