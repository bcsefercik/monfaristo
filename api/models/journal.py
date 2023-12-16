from models import TimeStampedBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.common import Symbol


class Transaction(TimeStampedBase):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbol.id"))
    symbol: Mapped["Symbol"] = relationship()
    price: Mapped[float] = mapped_column()
    count: Mapped[float] = mapped_column()
