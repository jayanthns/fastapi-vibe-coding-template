from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.db.session import get_db_with_trace_id
from app.middleware.trace import get_request_logger, get_trace_id
from app.schemas.article import APIResponse, Article, ArticleCreate, ArticleUpdate
from app.services.article import article_service

router = APIRouter()


@router.post(
    "/", response_model=APIResponse[Article], status_code=status.HTTP_201_CREATED
)
async def create_article(
    payload: ArticleCreate, request: Request, db=Depends(get_db_with_trace_id)
):
    logger = get_request_logger(request)
    logger.info(f"Creating article: {payload.title}")

    article = await article_service.create_article(db, payload)

    logger.info(f"Article created successfully with ID: {article.id}")
    return APIResponse.create_with_trace_id(
        data=article,
        message="Article created successfully",
        status_code=201,
        trace_id=get_trace_id(request),
    )


@router.get("/{article_id}", response_model=APIResponse[Article])
async def get_article(
    article_id: int, request: Request, db=Depends(get_db_with_trace_id)
):
    logger = get_request_logger(request)
    logger.info(f"Retrieving article with ID: {article_id}")

    article = await article_service.get_article(db, article_id)
    if not article:
        logger.warning(f"Article not found with ID: {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    logger.info(f"Article retrieved successfully: {article.title}")
    return APIResponse.create_with_trace_id(
        data=article,
        message="Article retrieved successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/", response_model=APIResponse[list[Article]])
async def list_articles(
    request: Request, skip: int = 0, limit: int = 100, db=Depends(get_db_with_trace_id)
):
    logger = get_request_logger(request)
    logger.info(f"Listing articles - skip: {skip}, limit: {limit}")

    articles = await article_service.list_articles(db, skip=skip, limit=limit)

    logger.info(f"Retrieved {len(articles)} articles")
    return APIResponse.create_with_trace_id(
        data=articles,
        message=f"Retrieved {len(articles)} articles",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.patch("/{article_id}", response_model=Article)
async def update_article(
    article_id: int,
    payload: ArticleUpdate,
    request: Request,
    db=Depends(get_db_with_trace_id),
):
    logger = get_request_logger(request)
    logger.info(f"Updating article with ID: {article_id}")

    article = await article_service.update_article(db, article_id, payload)
    if not article:
        logger.warning(f"Article not found for update with ID: {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    logger.info(f"Article updated successfully: {article.title}")
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int, request: Request, db=Depends(get_db_with_trace_id)
):
    logger = get_request_logger(request)
    logger.info(f"Deleting article with ID: {article_id}")

    deleted = await article_service.delete_article(db, article_id)
    if not deleted:
        logger.warning(f"Article not found for deletion with ID: {article_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    logger.info(f"Article deleted successfully with ID: {article_id}")
    return None
