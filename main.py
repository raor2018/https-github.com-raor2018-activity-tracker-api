#FastAPI
#main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine, Column,Integer, String, JSON, Datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from kafka import KafkaProducer
import json

#DBSetup

DATABASE_URL = "sqlite:///./activity.db"

#I am using POSTGRESQL for production purposes

engine = create_engine(DATABASE_URL, 
connct_args = {"check_thread":False})

SessionLocal = sessionmaker(bind = engine)
Base = declarative_base()

#Allowed Event types
Valid_Events = {"page_view","button_click","form_submit"}

#The Model

class Activity(Base):
    __tablename__ = "activities"
    id = Column(String,primary_key = True, default = lambda, str(uuid4()))
    user = Column(String, nullable = False)
    event_type = Column(String,nullable = False)
    timestamp = Column(Datetime, default = datetime.utcnow())
    page = Column(String)
    browser = Column(String)
    payload = Column(JSON)
    metadata = Column(JSON)

Base.metadata.create_all(bind = engine)

#KafkaSetup

KAFKA_TOPIC = "user_activity"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
producer = KafkaProducer(KAFKA_BOOTSTRAP_SERVERS,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))



#Pydantic Schema

class ActivityEvent(BaseModel):
    user:str
    event_type:str
    timestamp:Optional[datetime] = Field(default_factory = datetime.utcnow())
    page = Optional[str]
    browser = Optional[str]
    payload:Optional[Dict] = {}
    metadata:Optional[Dict] = {}
    
#FastAPI app
app = FastAPI()

@app.post("/user/{username}/activity")
def record_activity(username:str = Path(...,
description = "Username who performed the activity"),
event: ActivityEvent = ...):
    if event.event_type not in Valid_Events:
        raise HTTPException(status_code = 400,
        detail = "Invalid event type")
    activity_dict ={
    "user":username,
    "event_type":event.event_type,
    "timestamp":str(event.timestamp),
    "page":event.page,
    "browser":event.browser,
    "payload":event.payload,
    "metadata":event.metadata
    }
    
    db = SessionLocal()
    activity = Activity(user = username, **event.dict())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    db.close()
    
    #Send to Kafka
    producer.send(KAFKA_TOPIC, 
    value = activity_dict)
    producer.flush()
    
    return {
    "message": "activity recorded"
    }
