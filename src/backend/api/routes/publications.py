from fastapi import APIRouter
from backend.core.deps import CurrentUser, DbSession
from backend.schemas.publication import PublicationCreate, PublicationUpdate, PublicationResponse
from backend.services import publication_service

router = APIRouter()


@router.get("/", response_model=list[PublicationResponse])
async def list_publications(db: DbSession, _: CurrentUser):
    return await publication_service.list_publications(db)


@router.get("/{pub_id}", response_model=PublicationResponse)
async def get_publication(pub_id: int, db: DbSession, _: CurrentUser):
    return await publication_service.get_publication(db, pub_id)


@router.post("/", response_model=PublicationResponse, status_code=201)
async def create_publication(data: PublicationCreate, db: DbSession, _: CurrentUser):
    return await publication_service.create_publication(db, data)


@router.put("/{pub_id}", response_model=PublicationResponse)
async def update_publication(pub_id: int, data: PublicationUpdate, db: DbSession, _: CurrentUser):
    return await publication_service.update_publication(db, pub_id, data)


@router.delete("/{pub_id}", status_code=204)
async def delete_publication(pub_id: int, db: DbSession, _: CurrentUser):
    await publication_service.delete_publication(db, pub_id)
