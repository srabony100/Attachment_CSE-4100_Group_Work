from sqlalchemy.orm import Session

from app.models.entities import AdminActivityLog


class ActivityLogService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        admin_user_id: int,
        action_type: str,
        target_entity_type: str,
        target_entity_id: str | None,
        description: str,
    ) -> AdminActivityLog:
        entry = AdminActivityLog(
            admin_user_id=admin_user_id,
            action_type=action_type,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            description=description,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
