from uuid import UUID

from clean_python import ValueObject


class LizardTask(ValueObject):
    id: UUID
    status: str
    result: str | None = None
    detail: str | None = None

    def is_pending(self) -> bool:
        """Check if the task is still pending."""
        return self.status in {"PENDING", "STARTED", "RETRY"}

    def is_success(self) -> bool:
        return self.status == "SUCCESS"

    def is_failed(self) -> bool:
        return not (self.is_pending() or self.is_success())
