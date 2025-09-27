from fastapi import APIRouter, Depends, HTTPException, status

from app.db.session import get_db
from app.schemas.article import Article, ArticleCreate, ArticleUpdate
from app.services.article import article_service

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(payload: ArticleCreate, db=Depends(get_db)):
    return await article_service.create_article(db, payload)


@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: int, db=Depends(get_db)):
    article = await article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )
    return article


@router.get("/", response_model=list[Article])
async def list_articles(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    return await article_service.list_articles(db, skip=skip, limit=limit)


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
