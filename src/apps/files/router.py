"""
FastAPI router for Files API endpoints.
"""

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import PlainTextResponse, StreamingResponse

from src.apps.files.schemas import FileSuccessSchema, LinearDataResponseSchema
from src.apps.files.service import FileService
from src.core.logging import get_logger
from src.core.schemas import APIResponse
from src.middleware.trace import get_trace_id

router = APIRouter()


@router.post("/upload/linear", response_model=APIResponse[LinearDataResponseSchema])
async def upload_linear_file(
    request: Request,
    file: UploadFile = File(..., description="CSV or JSON file to upload"),
):
    """
    Uploads a linear data file (CSV or JSON), validates size (25KB limit),
    and returns the top 10 records.
    """
    logger = get_logger(request)
    logger.info(f"Uploading linear file: {file.filename}")

    # Validate size
    FileService.validate_file_size(file, limit_kb=25)

    # Get file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    # Parse file
    data = await FileService.parse_linear_file(file)

    response_data = LinearDataResponseSchema(
        message="File uploaded and parsed successfully.",
        filename=file.filename or "unknown",
        total_rows=len(data),
        preview_rows=data,
        human_readable_size=FileService.get_human_readable_size(file_size),
    )

    logger.info(
        f"Linear file uploaded successfully: {file.filename}, " f"rows: {len(data)}"
    )

    return APIResponse.create_with_trace_id(
        data=response_data,
        message="File uploaded and parsed successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.post("/upload/generic", response_model=APIResponse[FileSuccessSchema])
async def upload_generic_file(
    request: Request,
    file: UploadFile = File(..., description="Any file to upload"),
):
    """
    Uploads any file, validates size (25KB limit), and returns success.
    """
    logger = get_logger(request)
    logger.info(f"Uploading generic file: {file.filename}")

    # Validate size
    FileService.validate_file_size(file, limit_kb=25)

    # Get file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    response_data = FileSuccessSchema(
        message="File uploaded successfully.",
        filename=file.filename or "unknown",
        size=file_size,
        human_readable_size=FileService.get_human_readable_size(file_size),
    )

    logger.info(
        f"Generic file uploaded successfully: {file.filename}, "
        f"size: {file_size} bytes"
    )

    return APIResponse.create_with_trace_id(
        data=response_data,
        message="File uploaded successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/download/{filename}", response_class=PlainTextResponse)
async def download_file(request: Request, filename: str):
    """
    Downloads a dummy file of 25KB.
    """
    logger = get_logger(request)
    logger.info(f"Downloading file: {filename}")

    content = FileService.get_file_content(filename, size_kb=25)

    return PlainTextResponse(
        content=content,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/stream/{filename}")
async def stream_file(request: Request, filename: str):
    """
    Streams a dummy file of 25KB.
    """
    logger = get_logger(request)
    logger.info(f"Streaming file: {filename}")

    stream_generator = FileService.get_file_stream(filename, size_kb=25)

    return StreamingResponse(
        stream_generator,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/preview/{filename}", response_class=PlainTextResponse)
async def preview_file(request: Request, filename: str):
    """
    Previews the content of a dummy file (25KB).
    """
    logger = get_logger(request)
    logger.info(f"Previewing file: {filename}")

    content = FileService.get_file_content(filename, size_kb=25)

    return PlainTextResponse(content=content)
