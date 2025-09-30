import os
from typing import List
from datetime import datetime, timedelta, timezone
from api.db.session import get_session
from api.db.config import DATABASE_URL
from timescaledb.utils import get_utc_now
from timescaledb.hyperfunctions import time_bucket
from sqlalchemy import func, case
from pprint import pprint
from sqlmodel import Session, select, update
from fastapi import APIRouter, Depends, HTTPException, Query
from .models import (EventModel,
                     EventListModel,
                     EventCreateModel,
                     EventBucketModel,
                     EventBucketListModel,
                     EventBucketByAgentsListModel,
                     )

router = APIRouter()

DEFAULT_PAGES = ["/home", "/about", "/contact", "/pricing"]

@router.get("/", response_model=EventBucketListModel)
def read_events(
                duration: str = Query(default="1 day"),
                pages: List[str] = Query(default=None),
                limit: int = Query(default=20),
                session: Session = Depends(get_session)):
    bucket = time_bucket(duration, EventModel.time)
    page_list = DEFAULT_PAGES if pages is None else pages

    group_by_query = (select(bucket.label("bucket"),
                            EventModel.page.label("page"),
                            func.count().label("visit_count"),
                            func.avg(EventModel.duration).label("avg_duration"),
                            func.max(EventModel.duration).label("max_duration"),
                            func.min(EventModel.duration).label("min_duration")
                            )
                    .where(
                        EventModel.page.in_(page_list)
                          )
                    .group_by(
                            bucket,
                            EventModel.page
                             )
                    .order_by(func.count(EventModel.page).desc()).limit(limit)
    )
    events = session.exec(group_by_query).all()
    return {
        "events": events,
        "event_count": len(events)
        }

@router.get("/read_events_by_agents", response_model=EventBucketByAgentsListModel)
def read_events_by_agents(duration: str = Query(default="1 day"),
                          limit: int = Query(default=20),
                          session: Session = Depends(get_session)):
    bucket = time_bucket(duration, EventModel.time)
    os_case = case(
        (EventModel.user_agent.ilike("%windows%"), "Windows"),
        (EventModel.user_agent.ilike("%iphone%"), "iPhone"),
        (EventModel.user_agent.ilike("%linux%"), "Linux"),
        (EventModel.user_agent.ilike("%android%"), "Android"),
        (EventModel.user_agent.ilike("%macintosh%"), "MacOS"),
        else_="Other"
    ).label("operating_system")
    group_by_query = (select(bucket.label("bucket"),
                            os_case,
                            EventModel.page.label("page"),
                            func.count().label("visit_count"),
                            func.avg(EventModel.duration).label("avg_duration"),
                            func.max(EventModel.duration).label("max_duration"),
                            func.min(EventModel.duration).label("min_duration")
                            )
                    .group_by(
                        bucket,
                        EventModel.user_agent,
                        EventModel.page
                        )
                    .order_by(EventModel.user_agent.desc()).limit(limit))
    events = session.exec(group_by_query).all()
    return {
        "events": events,
        "event_count": len(events)
        }

@router.get("/read_first_events/{limit}", response_model=EventListModel)
def read_first_events(limit: int, session: Session = Depends(get_session)):
    select_query = select(EventModel).order_by(EventModel.event_id.asc()).limit(limit)
    events = session.exec(select_query).all()
    return {
        "events": events,
        "event_count": len(events)
        }

@router.get("/read_last_events/{limit}", response_model=EventListModel)
def read_last_events(limit: int, session: Session = Depends(get_session)):
    select_query = select(EventModel).order_by(EventModel.event_id.desc()).limit(limit)
    events = session.exec(select_query).all()
    return {
        "events": events,
        "event_count": len(events)
        }

@router.get("/{event_id}", response_model=EventModel)
def read_event(event_id: int, session: Session = Depends(get_session)):
    select_query = select(EventModel).where(EventModel.id == event_id)
    event = session.exec(select_query).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/", response_model=EventModel)
def create_event(payload: EventCreateModel, session: Session = Depends(get_session)):
    data = payload.model_dump()
    event_obj = EventModel.model_validate(data)
    session.add(event_obj)
    session.commit()
    session.refresh(event_obj)
    return event_obj



