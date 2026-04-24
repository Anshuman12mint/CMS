from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from APP.Utils.Config.SecurityConfig import getCurrentUser
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.Utils.Database.DatabaseConfig import getDbSession
from APP.CMS_extras.Communication.Meeting.MeetingDTO import MeetingDTO
from APP.CMS_extras.Communication.Meeting.MeetingJoinResponse import MeetingJoinResponse
from APP.CMS_extras.Communication.Messages.MeetingMessageDTO import MeetingMessageDTO
from APP.CMS_extras.Communication.Messages.MeetingMessageRepository import MeetingMessageRepository
from APP.CMS_extras.Communication.Messages.MeetingMessageRequest import MeetingMessageRequest
from APP.CMS_extras.Communication.Meeting.MeetingMutationRequest import MeetingMutationRequest
from APP.CMS_extras.Communication.Meeting.MeetingParticipantRepository import MeetingParticipantRepository
from APP.CMS_extras.Communication.Meeting.MeetingProviderService import MeetingProviderService
from APP.CMS_extras.Communication.Meeting.MeetingRepository import MeetingRepository
from APP.CMS_extras.Communication.Meeting.MeetingService import MeetingService
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def getMeetingService(session: Session = Depends(getDbSession)) -> MeetingService:
    return MeetingService(
        session,
        MeetingRepository(session),
        MeetingParticipantRepository(session),
        MeetingMessageRepository(session),
        CourseRepository(session),
        UserRepository(session),
        MeetingProviderService(),
    )


@router.get("", response_model=list[MeetingDTO])
def getMeetings(
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> list[MeetingDTO]:
    return meetingService.getMeetings(currentUser)


@router.get("/{meetingId}", response_model=MeetingDTO)
def getMeeting(
    meetingId: int,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingDTO:
    return meetingService.getMeeting(meetingId, currentUser)


@router.post("", response_model=MeetingDTO, status_code=status.HTTP_201_CREATED)
def createMeeting(
    request: MeetingMutationRequest,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingDTO:
    return meetingService.createMeeting(request, currentUser)


@router.put("/{meetingId}", response_model=MeetingDTO)
def updateMeeting(
    meetingId: int,
    request: MeetingMutationRequest,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingDTO:
    return meetingService.updateMeeting(meetingId, request, currentUser)


@router.post("/{meetingId}/join", response_model=MeetingJoinResponse)
def joinMeeting(
    meetingId: int,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingJoinResponse:
    return meetingService.joinMeeting(meetingId, currentUser)


@router.get("/{meetingId}/messages", response_model=list[MeetingMessageDTO])
def getMessages(
    meetingId: int,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> list[MeetingMessageDTO]:
    return meetingService.getMessages(meetingId, currentUser)


@router.post("/{meetingId}/messages", response_model=MeetingMessageDTO, status_code=status.HTTP_201_CREATED)
def postMessage(
    meetingId: int,
    request: MeetingMessageRequest,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingMessageDTO:
    return meetingService.postMessage(meetingId, request, currentUser)


@router.post("/{meetingId}/leave", response_model=MeetingDTO)
def leaveMeeting(
    meetingId: int,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingDTO:
    return meetingService.leaveMeeting(meetingId, currentUser)


@router.post("/{meetingId}/end", response_model=MeetingDTO)
def endMeeting(
    meetingId: int,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> MeetingDTO:
    return meetingService.endMeeting(meetingId, currentUser)


@router.delete("/{meetingId}", status_code=status.HTTP_204_NO_CONTENT)
def deleteMeeting(
    meetingId: int,
    meetingService: MeetingService = Depends(getMeetingService),
    currentUser = Depends(getCurrentUser),
) -> Response:
    meetingService.deleteMeeting(meetingId, currentUser)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
