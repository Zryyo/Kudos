"""Source interface: where revisions/text/activity come from (mock fixtures or live Google APIs)."""

import json
import os
from typing import Optional, TypedDict


class Revision(TypedDict):
    id: str
    modifiedTime: str
    editor_email: str
    editor_name: str


class ActivityEvent(TypedDict):
    actor_permission_id: Optional[str]
    actor_email: Optional[str]
    timestamp: str


class MockSource:
    """Reads revisions, revision text, and activity from mock_api/ fixtures."""

    def __init__(self, mock_dir: str = "mock_api"):
        self.mock_dir = mock_dir

    def list_revisions(self) -> list[Revision]:
        path = os.path.join(self.mock_dir, "revisions_list.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        revisions: list[Revision] = []
        for rev in data["revisions"]:
            user = rev["lastModifyingUser"]
            revisions.append(
                {
                    "id": rev["id"],
                    "modifiedTime": rev["modifiedTime"],
                    "editor_email": user["emailAddress"],
                    "editor_name": user["displayName"],
                }
            )
        return revisions

    def get_revision_text(self, rev_id: str) -> str:
        path = os.path.join(self.mock_dir, f"revision_{rev_id}.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def get_activity(self) -> list[ActivityEvent]:
        # Activity events identify actors by permissionId, not email, so resolve
        # each one against the revisions list (the only place mock data ties
        # permissionId -> email) the same way the live source will have to.
        permission_id_to_email = {
            rev["lastModifyingUser"]["permissionId"]: rev["lastModifyingUser"]["emailAddress"]
            for rev in json.load(open(os.path.join(self.mock_dir, "revisions_list.json"), encoding="utf-8"))["revisions"]
        }

        path = os.path.join(self.mock_dir, "drive_activity.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        events: list[ActivityEvent] = []
        for activity in data["activities"]:
            actor = activity["actors"][0]
            person_name = actor["user"]["knownUser"]["personName"]  # "people/{permissionId}"
            permission_id = person_name.split("/", 1)[1]
            events.append(
                {
                    "actor_permission_id": permission_id,
                    "actor_email": permission_id_to_email.get(permission_id),
                    "timestamp": activity["timestamp"],
                }
            )
        return events


class LiveSource:
    """Same interface as MockSource, backed by the real Google Drive APIs. Fill in for Step 7."""

    def __init__(self, document_id: str):
        self.document_id = document_id

    def list_revisions(self) -> list[Revision]:
        raise NotImplementedError

    def get_revision_text(self, rev_id: str) -> str:
        raise NotImplementedError

    def get_activity(self) -> list[ActivityEvent]:
        raise NotImplementedError
