from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import eq

from src.core.domain.entities import Payment
from src.core.domain.entities.payment import PaymentStatus
from src.core.domain.repositories import PaymentRepository
from src.infra.database.persistent_models.order_persistent_model import OrderPersistentModel
from src.infra.database.persistent_models.payment_persistent_model import PaymentPersistentModel


class SQLAlchemyPaymentRepository(PaymentRepository):
    """Implementation of the PaymentRepository using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        """Initializes the SQLAlchemyOrderRepository with a given session.

        Args:
            session (Session): The SQLAlchemy session to use for database operations.
        """
        self._session = session

    def get_by_uuid(self, uuid: UUID) -> Payment | None:
        """Retrieves a payment by its UUID."""
        result: PaymentPersistentModel | None = (
            self._session.query(PaymentPersistentModel).filter_by(uuid=uuid).first()
        )

        return result.to_entity() if result else None

    def add(self, payment: Payment) -> Payment:
        """Adds a new payment to the repository."""
        db_payment = PaymentPersistentModel.from_entity(payment)

        self._session.add(db_payment)
        self._session.commit()
        self._session.refresh(db_payment)

        return db_payment.to_entity()

    def get_payment_status(self, order_uuid: UUID) -> PaymentStatus | None:
        """Retrieves the status of a payment by the order UUID."""
        stmt = (
            select(PaymentPersistentModel)
            .join(OrderPersistentModel, PaymentPersistentModel.order_id == OrderPersistentModel.id)
            .where(eq(OrderPersistentModel.uuid, order_uuid))
        )
        result = self._session.execute(stmt).scalar_one_or_none()
        return result.status if result else None

    def update_status(self, payment_id: int, status: PaymentStatus) -> Payment | None:
        """Updates the status of an existing payment in the repository."""
        db_payment: PaymentPersistentModel | None = (
            self._session.query(PaymentPersistentModel).filter_by(id=payment_id).first()
        )

        if db_payment is None:
            return None

        db_payment.status = status
        self._session.commit()
        self._session.refresh(db_payment)

        return db_payment.to_entity()


__all__ = ["SQLAlchemyPaymentRepository"]
