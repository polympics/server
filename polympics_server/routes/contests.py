"""Routes relating to art contests."""
from datetime import datetime
from typing import Any, Optional

from fastapi import Depends, File, HTTPException, Response, UploadFile

import peewee

from pydantic import BaseModel, constr

from .utils import Paginate, Scope, auth_assert, authenticate, server
from ..models import Contest, ContestState, Piece, Submission, Vote


class ContestCreateForm(BaseModel):
    """Form for creating a new contest."""

    title: constr(max_length=255)
    description: constr(max_length=2047)
    opens_at: datetime
    closes_at: datetime
    ends_at: datetime


class ContestUpdateForm(BaseModel):
    """Form for updating an existing contest."""

    title: Optional[constr(max_length=255)] = None
    description: Optional[constr(max_length=2047)] = None
    opens_at: Optional[datetime] = None
    closes_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class SubmissionForm(BaseModel):
    """Form for creating or updating a submission to a contest."""

    title: constr(max_length=255)


class PieceForm(BaseModel):
    """Form for adding a piece to a submission or editing a piece."""

    position: Optional[int] = None     # Defaults to the end.
    # Defaults to empty.
    caption: Optional[constr(max_length=255)] = None
    # Default from uploaded file.
    filename: Optional[constr(max_length=255)] = None


def get_own_submission(
        contest: Contest, scope: Scope = Depends(authenticate)) -> Submission:
    """Get the submission made by the authenticated user."""
    auth_assert(scope.account)
    submission = Submission.get_or_none(
        Submission.contest == contest, Submission.account == scope.account
    )
    if not submission:
        raise HTTPException(
            404, 'You do not have a submission to this contest.'
        )
    return submission


def get_own_piece(
        position: int,
        submission: Submission = Depends(get_own_submission)) -> Piece:
    """Get a piece made by the authenticated user."""
    piece = Piece.get_or_none(
        Piece.submission == submission, Piece.position == position
    )
    if not piece:
        raise HTTPException(404, 'No piece found in given position.')
    return piece


def contest_state_assert(contest: Contest, state: ContestState):
    """Make sure the contest is in a given state."""
    if contest.state != state:
        raise HTTPException(
            409, f'You may only do that when the contest is {state.value}.'
        )


@server.get('/contests', tags=['contests'])
async def get_contests() -> dict[str, Any]:
    """Get a list of all contests (not paginated)."""
    return {
        'contests': [
            contest.as_dict() for contest in
            Contest.select().order_by(-Contest.closes_at)
        ]
    }


@server.post('/contests/new', status_code=201, tags=['contests'])
async def create_contest(
        data: ContestCreateForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a new contest."""
    auth_assert(scope.manage_contests)
    if not (data.opens_at < data.closes_at < data.ends_at):
        raise HTTPException(
            422, 'Open, close and end date must be in that order.'
        )
    return Contest.create(
        title=data.title,
        description=data.description,
        opens_at=data.opens_at,
        closes_at=data.closes_at,
        ends_at=data.ends_at
    ).as_dict()


@server.get('/contests/{contest}', tags=['contests'])
async def get_contest(contest: Contest) -> dict[str, Any]:
    """Get a contest by ID."""
    return contest.as_dict()


@server.delete('/contests/{contest}', status_code=204, tags=['contests'])
async def delete_contest(
        contest: Contest,
        scope: Scope = Depends(authenticate)) -> Response:
    """Delete a contest by ID."""
    auth_assert(scope.manage_contests)
    contest.delete_instance()
    return Response(status_code=204)


@server.patch('/contests/{contest}', tags=['contests'])
async def update_contest(
        contest: Contest,
        data: ContestUpdateForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Update a contest's details by ID."""
    auth_assert(scope.manage_contests)
    if not (
            (data.opens_at or contest.opens_at)
            < (data.closes_at or contest.closes_at)
            < (data.ends_at or contest.ends_at)):
        raise HTTPException(
            422, 'Open, close and end date must be in that order.'
        )
    if data.title:
        contest.title = data.title
    if data.description:
        contest.description = data.description
    if data.opens_at:
        contest.opens_at = data.opens_at
    if data.closes_at:
        contest.closes_at = data.closes_at
    if data.ends_at:
        contest.ends_at = data.ends_at
    contest.save()
    return contest.as_dict()


@server.get('/contests/{contest}/submissions', tags=['contests'])
async def get_contest_submissions(
        contest: Contest,
        paginate: Paginate = Depends(Paginate),
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get a paginated list of submissions for a contest.

    Vote count and author will only be included if you have
    the manage_contest_submissions permission or the contest has ended.
    """
    ended = contest.state == ContestState.ENDED
    if ended:
        vote_count = peewee.fn.COUNT(Vote.id).alias('vote_count')
        query = Submission.select(vote_count).join(
            Vote, peewee.JOIN.LEFT_OUTER
        ).group_by(Submission).order_by(vote_count)
    else:
        # Seed by ID to make pagination consistent.
        query = Submission.select(
            peewee.fn.SETSEED(scope.id)
        ).order_by(peewee.fn.RAND())
    return paginate(
        query.where(Submission.contest == contest),
        votes_and_author=scope.manage_contest_submissions or ended
    )


@server.post('/contests/{contest}/my_submission', tags=['contests'])
async def create_submission(
        contest: Contest,
        data: SubmissionForm,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Create a submission to a contest."""
    auth_assert(scope.make_contest_submissions)
    contest_state_assert(contest, ContestState.OPEN)
    if contest.get_account_submission(scope.account):
        raise HTTPException(
            409, 'You already have a submission to this contest.'
        )
    return Submission.create(
        contest=contest,
        account=scope.account,
        title=data.title
    ).as_dict()


@server.patch('/contests/{contest}/my_submission', tags=['contests'])
async def update_submission(
        data: SubmissionForm,
        submission: Submission = Depends(
            get_own_submission)) -> dict[str, Any]:
    """Update submission metadata."""
    contest_state_assert(submission.contest, ContestState.OPEN)
    submission.title = data.title
    submission.save()
    return submission.as_dict()


@server.get('/contests/{contest}/my_submission', tags=['contests'])
async def get_own_submission(
        submission: Submission = Depends(
            get_own_submission)) -> dict[str, Any]:
    """Get your own submission to a contest."""
    return submission.as_dict()


@server.delete(
    '/contests/{contest}/my_submission',
    status_code=204,
    tags=['contests']
)
async def delete_own_submission(
        submission: Submission = Depends(
            get_own_submission)) -> dict[str, Any]:
    """Delete your own submission to a contest."""
    contest_state_assert(submission.contest, ContestState.OPEN)
    submission.delete_instance()
    return Response(status_code=204)


@server.post(
    '/contests/{contest}/my_submission/pieces/new',
    tags=['contests']
)
async def create_piece(
        data: PieceForm,
        submission: Submission = Depends(
            get_own_submission)) -> dict[str, Any]:
    """Add a piece to your submission.

    Note that the piece will not be visible until a file is added.
    """
    contest_state_assert(submission.contest, ContestState.OPEN)
    max_position = Piece.select().where(
        Piece.submission == submission
    ).count()
    if not data.position:
        position = max_position
    else:
        if data.position > max_position:
            raise HTTPException(
                422,
                'Position must be no more than the current number of pieces.'
            )
        if data.position < max_position:
            Piece.update(position=Piece.position + 1).where(
                Piece.submission == submission,
                Piece.position >= data.position
            ).execute()
    Piece.create(
        submission=submission,
        position=position,
        caption=data.caption or '',
        filename=data.filename,
    )
    return submission.as_dict()


@server.patch(
    '/contests/{contest}/my_submission/piece/{position}',
    tags=['contests']
)
async def update_piece(
        data: PieceForm,
        piece: Piece = Depends(get_own_piece)) -> dict[str, Any]:
    """Edit metadata for a piece in your submission."""
    contest_state_assert(piece.submission.contest, ContestState.OPEN)
    if data.caption:
        piece.caption = data.caption
    if data.filename:
        piece.filename = data.filename
    if data.position:
        max_position = Piece.select().where(
            Piece.submission == piece.submission
        ).count() - 1
        if data.position > max_position:
            raise HTTPException(
                422, 'Position less than the current number of pieces.'
            )
        if data.position > piece.position:
            Piece.update(position=Piece.position - 1).where(
                Piece.submission == piece.submission,
                Piece.position > piece.position,
                Piece.position <= data.position
            ).execute()
        elif data.position < piece.position:
            Piece.update(position=Piece.position + 1).where(
                Piece.submission == piece.submission,
                Piece.position < piece.position,
                Piece.position >= data.position
            ).execute()
        piece.position = data.position
    piece.save()
    return piece.submission.as_dict()


@server.put(
    '/contests/{contest}/my_submission/piece/{position}/file',
    tags=['contests']
)
async def set_piece_file(
        file: UploadFile = File(),
        piece: Piece = Depends(get_own_piece)) -> dict[str, Any]:
    """Set the file associated with a piece."""
    contest_state_assert(piece.submission.contest, ContestState.OPEN)
    piece.mime_type = file.content_type
    piece.filename = file.filename[-255:]
    piece.data = await file.read()
    piece.save()


@server.delete(
    '/contests/{contest}/my_submission/piece/{position}',
    tags=['contests']
)
async def delete_piece(
        piece: Piece = Depends(get_own_piece)) -> dict[str, Any]:
    """Delete a piece from your submission."""
    contest_state_assert(piece.submission.contest, ContestState.OPEN)
    piece = Piece.get_or_none(
        Piece.submission == piece.submission, Piece.position == piece.position
    )
    if not piece:
        raise HTTPException(404, 'No piece found in given position.')
    Piece.update(position=Piece.position - 1).where(
        Piece.submission == piece.submission,
        Piece.position > piece.position
    ).execute()
    piece.delete_instance()
    return piece.submission.as_dict()


@server.get('/submissions/{submission}', tags=['contests'])
async def get_submission(
        submission: Submission,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Get a submission by ID.

    Vote count and author will only be included if you have
    the manage_contest_submissions permission or the contest has ended.
    """
    return submission.as_dict(votes_and_author=(
        scope.manage_contest_submissions
        or submission.contest.state == ContestState.ENDED
    ))


@server.delete('/submissions/{submission}', tags=['contests'])
async def delete_submission(
        submission: Submission,
        scope: Scope = Depends(authenticate)) -> Response:
    """Delete a submission by ID.

    This requires the manage_contest_submissions permission. To delete
    your own submission, do `DELETE /contests/{contest}/my_submission`.
    """
    auth_assert(scope.manage_contest_submissions)
    submission.delete_instance()
    return Response(status_code=204)


@server.post(
    '/submissions/{submission}/vote', status_code=204, tags=['contests']
)
async def place_submission_vote(
        submission: Submission,
        scope: Scope = Depends(authenticate)) -> Response:
    """Place a vote on a submission."""
    contest_state_assert(submission.contest, ContestState.CLOSED)
    # Only accounts can have vote_contest_submissions, so we don't need
    # to check it's an account.
    auth_assert(scope.vote_contest_submissions)
    Vote.create(submission=submission, account=scope.account)
    return Response(status_code=204)


@server.delete('/submissions/{submission}/vote', tags=['contests'])
async def remove_submission_vote(
        submission: Submission,
        scope: Scope = Depends(authenticate)) -> dict[str, Any]:
    """Remove a vote from a submission."""
    contest_state_assert(submission.contest, ContestState.CLOSED)
    # Allow people to remove their vote even if they no longer have voting
    # permissions - check only that it's an account.
    auth_assert(scope.account)
    vote = Vote.get_or_none(
        Vote.submission == submission, Vote.account == scope.account
    )
    if not vote:
        raise HTTPException(404, 'You have not voted for this submission.')
    vote.delete_instance()
    return Response(status_code=204)


@server.get(
    '/uploads/pieces/{piece}/{filename}',
    response_class=Response,
    tags=['uploads']
)
async def get_piece_file(piece: Piece, filename: str) -> Response:
    """Get the file for a piece on a submission."""
    return Response(content=bytes(piece.data), media_type=piece.mime_type)
