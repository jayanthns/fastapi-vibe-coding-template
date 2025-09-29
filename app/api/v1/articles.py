from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.db.session import get_db
from app.middleware.trace import get_trace_id
from app.schemas.article import APIResponse, Article, ArticleCreate, ArticleUpdate
from app.services.article import article_service

router = APIRouter()


@router.post(
    "/", response_model=APIResponse[Article], status_code=status.HTTP_201_CREATED
)
async def create_article(payload: ArticleCreate, request: Request, db=Depends(get_db)):
    article = await article_service.create_article(db, payload)
    return APIResponse.create_with_trace_id(
        data=article,
        message="Article created successfully",
        status_code=201,
        trace_id=get_trace_id(request),
    )


@router.get("/{article_id}", response_model=APIResponse[Article])
async def get_article(article_id: int, request: Request, db=Depends(get_db)):
    article = await article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return APIResponse.create_with_trace_id(
        data=article,
        message="Article retrieved successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/", response_model=APIResponse[list[Article]])
async def list_articles(
    request: Request, skip: int = 0, limit: int = 100, db=Depends(get_db)
):
    articles = await article_service.list_articles(db, skip=skip, limit=limit)
    return APIResponse.create_with_trace_id(
        data=articles,
        message=f"Retrieved {len(articles)} articles",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.patch("/{article_id}", response_model=Article)
async def update_article(article_id: int, payload: ArticleUpdate, db=Depends(get_db)):
    article = await article_service.update_article(db, article_id, payload)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: int, db=Depends(get_db)):
    deleted = await article_service.delete_article(db, article_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return None
