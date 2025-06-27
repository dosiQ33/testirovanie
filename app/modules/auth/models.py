from sqlalchemy import text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.common.models import BaseModel, str_uniq


class Role(BaseModel):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"


class User(BaseModel):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), default=1, server_default=text("1"))
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
