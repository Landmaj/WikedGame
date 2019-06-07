from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Table,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: int = Column(BigInteger, primary_key=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow())
    modified_at: datetime = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


BaseModel = declarative_base(cls=Base)

page_links = Table(
    "page_links",
    BaseModel.metadata,
    Column("from_page", BigInteger, ForeignKey("wikipage.id")),
    Column("to_page", BigInteger, ForeignKey("wikipage.id")),
)


class WikiPage(BaseModel):
    page_id = Column(Integer, unique=True, nullable=False)
    title = Column(Text, unique=True, nullable=False)
    dump_date = Column(Date, nullable=False)

    url = Column(Text)
    hits = Column(Integer, default=0)

    links = relationship(
        "WikiPage",
        secondary="page_links",
        primaryjoin="WikiPage.id==page_links.c.from_page",
        secondaryjoin="WikiPage.id==page_links.c.to_page",
    )
