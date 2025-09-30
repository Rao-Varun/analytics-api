from ipaddress import ip_address
import sqlmodel
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, SQLModel
from timescaledb import TimescaleModel
from timescaledb.utils import get_utc_now


class EventModel(TimescaleModel, table=True):
    page: str = Field(index=True)
    user_agent: Optional[str] = Field(default="", index=True)
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)

    __chunk_time_interval__ = 'INTERVAL 1 day'
    __drop_after__ = 'INTERVAL 3 months'

class EventListModel(SQLModel):
    events: List[EventModel]
    event_count: int

class EventCreateModel(SQLModel):
    page: str = Field(index=True)
    user_agent: Optional[str] = Field(default="", index=True)
    ip_address: Optional[str] = Field(default="", index=True)
    referrer: Optional[str] = Field(default="", index=True)
    session_id: Optional[str] = Field(index=True)
    duration: Optional[int] = Field(default=0)



class EventBucketModel(SQLModel):
    bucket: datetime
    page: str
    visit_count: int
    avg_duration: float
    max_duration: int
    min_duration: int

class EventBucketListModel(SQLModel):
    events: List[EventBucketModel]
    event_count: int


class EventBucketByAgentsModel(SQLModel):
    bucket: datetime
    operating_system: str
    page: str
    visit_count: int
    avg_duration: float
    max_duration: int
    min_duration: int

class EventBucketByAgentsListModel(SQLModel):
    events: List[EventBucketByAgentsModel]
    event_count: int
