from __future__ import annotations

from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from APP.Utils.Config.AppConfig import utcNow
from APP.CMS_BASICS.Course.CourseRepository import CourseRepository
from APP.CMS_extras.Communication.Meeting.Meeting import Meeting
from APP.CMS_extras.Communication.Meeting.MeetingDTO import MeetingDTO
from APP.CMS_extras.Communication.Meeting.MeetingJoinResponse import MeetingJoinResponse
from APP.CMS_extras.Communication.Messages.MeetingMessage import MeetingMessage
from APP.CMS_extras.Communication.Messages.MeetingMessageDTO import MeetingMessageDTO
from APP.CMS_extras.Communication.Messages.MeetingMessageRepository import MeetingMessageRepository
from APP.CMS_extras.Communication.Messages.MeetingMessageRequest import MeetingMessageRequest
from APP.CMS_extras.Communication.Meeting.MeetingMutationRequest import MeetingMutationRequest
from APP.CMS_extras.Communication.Meeting.MeetingParticipant import MeetingParticipant
from APP.CMS_extras.Communication.Meeting.MeetingParticipantDTO import MeetingParticipantDTO
from APP.CMS_extras.Communication.Meeting.MeetingParticipantRepository import MeetingParticipantRepository
from APP.CMS_extras.Communication.Meeting.MeetingProviderService import MeetingProviderService
from APP.CMS_extras.Communication.Meeting.MeetingRepository import MeetingRepository
from APP.CMS_BASICS.Login_resister.User import User
from APP.CMS_BASICS.Login_resister.UserRepository import UserRepository
from APP.Utils.Helpers import Helpers
from APP.Utils.Validators import Validators


class MeetingService:
    STATUS_SCHEDULED = "Scheduled"
    STATUS_LIVE = "Live"
    STATUS_ENDED = "Ended"
    AUDIENCE_OPEN = "Open"
    AUDIENCE_COURSE = "Course"
    AUDIENCE_INVITE_ONLY = "InviteOnly"
    PARTICIPANT_ROLE_HOST = "Host"
    PARTICIPANT_ROLE_PARTICIPANT = "Participant"

    def __init__(
        self,
        session: Session,
        meetingRepository: MeetingRepository,
        meetingParticipantRepository: MeetingParticipantRepository,
        meetingMessageRepository: MeetingMessageRepository,
        courseRepository: CourseRepository,
        userRepository: UserRepository,
        meetingProviderService: MeetingProviderService,
    ) -> None:
        self.session = session
        self.meetingRepository = meetingRepository
        self.meetingParticipantRepository = meetingParticipantRepository
        self.meetingMessageRepository = meetingMessageRepository
        self.courseRepository = courseRepository
        self.userRepository = userRepository
        self.meetingProviderService = meetingProviderService

    def getMeetings(self, currentUser: User) -> list[MeetingDTO]:
        meetings = self.meetingRepository.findAllByOrderByScheduledStartAtDescCreatedAtDesc()
        return [self.toDto(meeting, currentUser) for meeting in meetings if self.canViewMeeting(currentUser, meeting)]

    def getMeeting(self, meetingId: int, currentUser: User) -> MeetingDTO:
        meeting = self.findMeeting(meetingId)
        self.ensureCanView(currentUser, meeting)
        return self.toDto(meeting, currentUser)

    def createMeeting(self, request: MeetingMutationRequest, currentUser: User) -> MeetingDTO:
        self.ensureCanCreate(currentUser)
        meeting = Meeting()
        meeting.provider = self.meetingProviderService.provider()
        meetingCode = self.generateMeetingCode()
        meeting.meetingCode = meetingCode
        meeting.roomName = self.generateUniqueRoomName(meetingCode)
        meeting.status = self.STATUS_SCHEDULED
        meeting.createdBy = currentUser
        meeting.createdByUserId = currentUser.userId
        self.apply(meeting, request)
        savedMeeting = self.meetingRepository.save(meeting)
        self.saveHost(savedMeeting, currentUser)
        self.syncExplicitParticipants(savedMeeting, currentUser, request.participantUserIds)
        return self.getMeeting(savedMeeting.meetingId, currentUser)

    def updateMeeting(self, meetingId: int, request: MeetingMutationRequest, currentUser: User) -> MeetingDTO:
        meeting = self.findMeeting(meetingId)
        self.ensureCanManage(currentUser, meeting)
        Validators.require(meeting.status != self.STATUS_ENDED, "Ended meetings cannot be updated")
        self.apply(meeting, request)
        self.meetingRepository.save(meeting)
        self.syncExplicitParticipants(meeting, currentUser, request.participantUserIds)
        return self.getMeeting(meetingId, currentUser)

    def deleteMeeting(self, meetingId: int, currentUser: User) -> None:
        meeting = self.findMeeting(meetingId)
        self.ensureCanManage(currentUser, meeting)
        self.meetingParticipantRepository.deleteByMeetingMeetingId(meetingId)
        self.meetingRepository.delete(meeting)

    def joinMeeting(self, meetingId: int, currentUser: User) -> MeetingJoinResponse:
        meeting = self.findMeeting(meetingId)
        self.ensureCanJoin(currentUser, meeting)
        Validators.require(meeting.status != self.STATUS_ENDED, "Meeting has already ended")

        participant = self.meetingParticipantRepository.findByMeetingMeetingIdAndUserUserId(meetingId, currentUser.userId)
        if participant is None:
            participant = self.createAttendanceParticipant(meeting, currentUser)

        now = utcNow()
        participant.joinedAt = now
        participant.leftAt = None
        self.meetingParticipantRepository.save(participant)

        if meeting.status == self.STATUS_SCHEDULED:
            meeting.status = self.STATUS_LIVE
            if meeting.startedAt is None:
                meeting.startedAt = now
            self.meetingRepository.save(meeting)

        return self.meetingProviderService.toJoinResponse(
            meeting,
            currentUser,
            participant.role,
            self.resolveDisplayName(currentUser),
        )

    def getMessages(self, meetingId: int, currentUser: User) -> list[MeetingMessageDTO]:
        meeting = self.findMeeting(meetingId)
        self.ensureCanView(currentUser, meeting)
        return [self.toMessageDto(message) for message in self.meetingMessageRepository.findByMeetingMeetingIdOrderByCreatedAtAsc(meetingId)]

    def postMessage(self, meetingId: int, request: MeetingMessageRequest, currentUser: User) -> MeetingMessageDTO:
        meeting = self.findMeeting(meetingId)
        self.ensureCanJoin(currentUser, meeting)
        Validators.require(meeting.status != self.STATUS_ENDED, "Meeting has already ended")
        Validators.requireText(request.messageText, "messageText")

        participant = self.meetingParticipantRepository.findByMeetingMeetingIdAndUserUserId(meetingId, currentUser.userId)
        if participant is None:
            participant = self.createAttendanceParticipant(meeting, currentUser)
        if participant.joinedAt is None:
            participant.joinedAt = utcNow()
        participant.leftAt = None
        self.meetingParticipantRepository.save(participant)

        message = MeetingMessage()
        message.meeting = meeting
        message.meetingId = meeting.meetingId
        message.user = currentUser
        message.userId = currentUser.userId
        message.messageText = request.messageText.strip()
        return self.toMessageDto(self.meetingMessageRepository.save(message))

    def leaveMeeting(self, meetingId: int, currentUser: User) -> MeetingDTO:
        meeting = self.findMeeting(meetingId)
        self.ensureCanView(currentUser, meeting)
        participant = self.meetingParticipantRepository.findByMeetingMeetingIdAndUserUserId(meetingId, currentUser.userId)
        if participant is not None:
            participant.leftAt = utcNow()
            self.meetingParticipantRepository.save(participant)
        return self.getMeeting(meetingId, currentUser)

    def endMeeting(self, meetingId: int, currentUser: User) -> MeetingDTO:
        meeting = self.findMeeting(meetingId)
        self.ensureCanManage(currentUser, meeting)
        now = utcNow()
        meeting.status = self.STATUS_ENDED
        if meeting.startedAt is None:
            meeting.startedAt = now
        meeting.endedAt = now
        self.meetingRepository.save(meeting)
        return self.getMeeting(meetingId, currentUser)

    def apply(self, meeting: Meeting, request: MeetingMutationRequest) -> None:
        Validators.requireText(request.title, "title")
        Validators.require(request.scheduledStartAt is not None, "scheduledStartAt is required")
        Validators.require(
            request.scheduledEndAt is None or request.scheduledEndAt >= request.scheduledStartAt,
            "scheduledEndAt must be after scheduledStartAt",
        )

        courseCode = Helpers.trimToNull(request.courseCode)
        if courseCode is not None and self.courseRepository.findById(courseCode) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        meeting.title = Helpers.trimToNull(request.title)  # type: ignore[assignment]
        meeting.description = Helpers.trimToNull(request.description)
        meeting.courseCode = courseCode
        meeting.audienceType = self.resolveAudienceType(courseCode, request.participantUserIds)
        meeting.scheduledStartAt = request.scheduledStartAt
        meeting.scheduledEndAt = request.scheduledEndAt

    def findMeeting(self, meetingId: int | None) -> Meeting:
        meeting = self.meetingRepository.findById(meetingId)
        if meeting is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        return meeting

    def ensureCanCreate(self, user: User) -> None:
        if not self.canCreateMeetings(user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin, teacher, or staff users can create meetings")

    def ensureCanManage(self, currentUser: User, meeting: Meeting) -> None:
        if not self.canManageMeeting(currentUser, meeting):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to manage this meeting")

    def ensureCanView(self, currentUser: User, meeting: Meeting) -> None:
        if not self.canViewMeeting(currentUser, meeting):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this meeting")

    def ensureCanJoin(self, currentUser: User, meeting: Meeting) -> None:
        if not self.canJoinMeeting(currentUser, meeting):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to join this meeting")

    def canCreateMeetings(self, user: User) -> bool:
        role = self.normalizeUserRole(user)
        return role in {"ADMIN", "TEACHER", "STAFF"}

    def canManageMeeting(self, currentUser: User, meeting: Meeting) -> bool:
        return self.isAdmin(currentUser) or meeting.createdByUserId == currentUser.userId

    def canViewMeeting(self, currentUser: User, meeting: Meeting) -> bool:
        if self.canManageMeeting(currentUser, meeting):
            return True
        if self.meetingParticipantRepository.existsByMeetingMeetingIdAndUserUserId(meeting.meetingId, currentUser.userId):
            return True
        if meeting.audienceType == self.AUDIENCE_OPEN:
            return True
        return (
            meeting.audienceType == self.AUDIENCE_COURSE
            and currentUser.student is not None
            and meeting.courseCode is not None
            and meeting.courseCode.lower() == (currentUser.student.courseCode or "").lower()
        )

    def canJoinMeeting(self, currentUser: User, meeting: Meeting) -> bool:
        if meeting.status == self.STATUS_ENDED:
            return self.canManageMeeting(currentUser, meeting) or self.meetingParticipantRepository.existsByMeetingMeetingIdAndUserUserId(meeting.meetingId, currentUser.userId)
        return self.canViewMeeting(currentUser, meeting)

    def isAdmin(self, user: User) -> bool:
        return self.normalizeUserRole(user) == "ADMIN"

    def normalizeUserRole(self, user: User) -> str:
        return (user.role or "").strip().upper()

    def resolveAudienceType(self, courseCode: str | None, participantUserIds: list[int] | None) -> str:
        if courseCode is not None:
            return self.AUDIENCE_COURSE
        return self.AUDIENCE_OPEN if not Helpers.distinctList(participantUserIds) else self.AUDIENCE_INVITE_ONLY

    def generateMeetingCode(self) -> str:
        for _ in range(10):
            code = "MEET-" + uuid4().hex[:8].upper()
            if not self.meetingRepository.existsByMeetingCode(code):
                return code
        raise RuntimeError("Unable to generate a unique meeting code")

    def generateUniqueRoomName(self, meetingCode: str) -> str:
        roomName = self.meetingProviderService.generateRoomName(meetingCode)
        if not self.meetingRepository.existsByRoomName(roomName):
            return roomName
        return f"{roomName}-{uuid4().hex[:6].lower()}"

    def saveHost(self, meeting: Meeting, host: User) -> None:
        participant = MeetingParticipant()
        participant.meeting = meeting
        participant.meetingId = meeting.meetingId
        participant.user = host
        participant.userId = host.userId
        participant.role = self.PARTICIPANT_ROLE_HOST
        participant.invited = True
        self.meetingParticipantRepository.save(participant)

    def syncExplicitParticipants(self, meeting: Meeting, currentUser: User, participantUserIds: list[int] | None) -> None:
        self.meetingParticipantRepository.deleteByMeetingMeetingIdAndRoleAndInvited(
            meeting.meetingId,
            self.PARTICIPANT_ROLE_PARTICIPANT,
            True,
        )
        for userId in Helpers.distinctList(participantUserIds):
            if currentUser.userId == userId:
                continue
            participantUser = self.userRepository.findById(userId)
            if participantUser is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            participant = self.meetingParticipantRepository.findByMeetingMeetingIdAndUserUserId(meeting.meetingId, userId)
            if participant is None:
                participant = MeetingParticipant()
            participant.meeting = meeting
            participant.meetingId = meeting.meetingId
            participant.user = participantUser
            participant.userId = participantUser.userId
            participant.role = self.PARTICIPANT_ROLE_PARTICIPANT
            participant.invited = True
            self.meetingParticipantRepository.save(participant)

    def createAttendanceParticipant(self, meeting: Meeting, user: User) -> MeetingParticipant:
        participant = MeetingParticipant()
        participant.meeting = meeting
        participant.meetingId = meeting.meetingId
        participant.user = user
        participant.userId = user.userId
        participant.role = self.PARTICIPANT_ROLE_PARTICIPANT
        participant.invited = False
        return participant

    def toDto(self, meeting: Meeting, currentUser: User) -> MeetingDTO:
        participants = self.meetingParticipantRepository.findByMeetingMeetingIdOrderByCreatedAtAsc(meeting.meetingId)
        participantDtos = [self.toParticipantDto(participant) for participant in participants]
        viewerRole = next((participant.role for participant in participants if participant.userId == currentUser.userId), None)
        return MeetingDTO(
            meetingId=meeting.meetingId,
            title=meeting.title,
            description=meeting.description,
            provider=meeting.provider,
            meetingCode=meeting.meetingCode,
            roomName=meeting.roomName,
            joinUrl=self.meetingProviderService.buildJoinUrl(meeting.roomName),
            status=meeting.status,
            audienceType=meeting.audienceType,
            courseCode=meeting.courseCode,
            scheduledStartAt=meeting.scheduledStartAt,
            scheduledEndAt=meeting.scheduledEndAt,
            startedAt=meeting.startedAt,
            endedAt=meeting.endedAt,
            hostUserId=meeting.createdByUserId,
            hostUsername=meeting.createdBy.username if meeting.createdBy is not None else None,
            viewerRole=viewerRole,
            canManage=self.canManageMeeting(currentUser, meeting),
            canJoin=self.canJoinMeeting(currentUser, meeting),
            createdAt=meeting.createdAt,
            participants=participantDtos,
        )

    def toParticipantDto(self, participant: MeetingParticipant) -> MeetingParticipantDTO:
        user = participant.user
        return MeetingParticipantDTO(
            userId=user.userId if user is not None else participant.userId,
            username=user.username if user is not None else None,
            displayName=self.resolveDisplayName(user) if user is not None else None,
            role=participant.role,
            invited=participant.invited,
            joinedAt=participant.joinedAt,
            leftAt=participant.leftAt,
        )

    def toMessageDto(self, message: MeetingMessage) -> MeetingMessageDTO:
        user = message.user
        return MeetingMessageDTO(
            messageId=message.messageId,
            meetingId=message.meetingId,
            userId=user.userId if user is not None else message.userId,
            username=user.username if user is not None else None,
            displayName=self.resolveDisplayName(user) if user is not None else None,
            messageText=message.messageText,
            createdAt=message.createdAt,
        )

    def resolveDisplayName(self, user: User | None) -> str | None:
        if user is None:
            return None
        if user.student is not None:
            return Helpers.fullName(user.student.firstName, user.student.lastName)
        return user.username
