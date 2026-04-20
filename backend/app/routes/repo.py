from fastapi import APIRouter
from app.schemas.repo import RepoRequest
from app.services.repo_service import clone_and_analyze

router = APIRouter()

@router.post("/repo/load")
def load_repo(request: RepoRequest):
    return clone_and_analyze(request.repo_url)