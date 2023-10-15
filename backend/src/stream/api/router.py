from uuid import UUID
from fastapi import APIRouter, Depends, status
from typing import Annotated

from src.stream.domain.ports import (
    StreamUnitCommandServiceInterface,
    StreamUnitQueryServiceInterface,
    Actor,
)
from src.stream.api.models import PostStreamUnit, StreamUnit
from src.stream.api.exceptions import (
    STREAM_UNIT_ALREADY_EXIST,
    STREAM_UNIT_NOT_FOUND,
)
from src.stream.domain.exceptions import (
    InsufficientPermissionsToAddStreamUnit,
    StreamUnitAlreadyExists,
    InsufficientPermissionsToGetStreamUnits,
    StreamUnitNotFound,
)
from src.auth.authentication import get_authenticated_user
from src.core.api.exceptions import UNAUTHORIZED, FORBIDDEN
from src.core.api.models import ErrorMessageResponse
from src.core.api.models import EmptyResponse
from src.stream.domain.dtos import WriteStreamUnit, StreamUnitReadModel
from src.core.api.utils import make_response
from kink import di


router = APIRouter(prefix="/streams")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[StreamUnit],
    responses={
        UNAUTHORIZED.status_code: ErrorMessageResponse,
        FORBIDDEN.status_code: ErrorMessageResponse,
    },
)
@make_response(StreamUnit, status_code=status.HTTP_200_OK)
async def get_streams(
    actor: Annotated[Actor, Depends(get_authenticated_user)],
    query_service: Annotated[
        StreamUnitQueryServiceInterface,
        Depends(lambda: di[StreamUnitQueryServiceInterface]),
    ],
) -> list[StreamUnitReadModel]:
    try:
        return query_service.get_list(actor)
    except InsufficientPermissionsToGetStreamUnits:
        raise FORBIDDEN


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EmptyResponse,
    responses={
        UNAUTHORIZED.status_code: ErrorMessageResponse,
        FORBIDDEN.status_code: ErrorMessageResponse,
        STREAM_UNIT_ALREADY_EXIST.status_code: ErrorMessageResponse,
    },
)
@make_response(EmptyResponse, status_code=status.HTTP_201_CREATED)
async def post_stream_unit(
    stream_unit: PostStreamUnit,
    actor: Annotated[Actor, Depends(get_authenticated_user)],
    command_service: Annotated[
        StreamUnitCommandServiceInterface,
        Depends(lambda: di[StreamUnitCommandServiceInterface]),
    ],
) -> dict:
    write_stream_unit = WriteStreamUnit.from_post_stream_unit_model(
        stream_unit
    )

    try:
        command_service.add_stream_unit(actor, write_stream_unit)
    except InsufficientPermissionsToAddStreamUnit:
        raise FORBIDDEN

    except StreamUnitAlreadyExists:
        raise STREAM_UNIT_ALREADY_EXIST

    return {}


@router.get(
    "/owned",
    status_code=status.HTTP_200_OK,
    response_model=list[StreamUnit],
    responses={
        FORBIDDEN.status_code: ErrorMessageResponse,
        UNAUTHORIZED.status_code: ErrorMessageResponse,
    },
)
@make_response(StreamUnit)
async def get_owned_streams(
    actor: Annotated[Actor, Depends(get_authenticated_user)],
    query_service: Annotated[
        StreamUnitQueryServiceInterface,
        Depends(lambda: di[StreamUnitQueryServiceInterface]),
    ],
) -> list[StreamUnitReadModel]:
    try:
        return query_service.get_actor_stream_units(actor)
    except InsufficientPermissionsToGetStreamUnits:
        raise FORBIDDEN


@router.get(
    "/{stream_unit_id}",
    status_code=status.HTTP_200_OK,
    response_model=StreamUnit,
    responses={
        FORBIDDEN.status_code: ErrorMessageResponse,
        UNAUTHORIZED.status_code: ErrorMessageResponse,
        STREAM_UNIT_NOT_FOUND.status_code: ErrorMessageResponse,
    },
)
@make_response(StreamUnit)
async def get_stream_unit(
    stream_unit_id: UUID,
    actor: Annotated[Actor, Depends(get_authenticated_user)],
    query_service: Annotated[
        StreamUnitQueryServiceInterface,
        Depends(lambda: di[StreamUnitQueryServiceInterface]),
    ],
) -> StreamUnitReadModel:
    try:
        return query_service.get(actor, stream_unit_id)
    except InsufficientPermissionsToGetStreamUnits:
        raise FORBIDDEN
    except StreamUnitNotFound:
        raise STREAM_UNIT_NOT_FOUND
