from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pyais import decode
import asyncio
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./ships_data.db"
Base = declarative_base()

class Ship(Base):
    __tablename__ = 'ships'
    mmsi = Column(Integer, primary_key=True, index=True)

class ShipData(Base):
    __tablename__ = 'ship_data'
    id = Column(Integer, primary_key=True, index=True)
    mmsi = Column(Integer, ForeignKey('ships.mmsi'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(String)  # Storing the decoded message as a string

# Database setup
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Other parts of your FastAPI application...

# Store additional attributes for each ship
ship_details = {}

async def read_ais_file():
    """Generator function to read AIS data file line by line."""
    with open('db/ais data.txt', 'r') as file:
        for line in file:
            yield line.strip()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async for line in read_ais_file():
        try:
            decoded_msg = decode(str.encode(line)).asdict()
        except:
            continue

        msg_type = decoded_msg.get('msg_type')
        if msg_type == 4:
            user_id = decoded_msg.get('mmsi')
            lat = decoded_msg.get('lat')
            lon = decoded_msg.get('lon')

            # Send user ID, latitude, and longitude as JSON
            await websocket.send_json({'id': user_id, 'lat': lat, 'lon': lon})

            # Database operation
            db = SessionLocal()
            ship = db.query(Ship).filter(Ship.mmsi == user_id).first()
            if not ship:
                ship = Ship(mmsi=user_id)
                db.add(ship)
            ship_data = ShipData(mmsi=user_id, data=str(decoded_msg))
            db.add(ship_data)
            db.commit()
            db.close()

            await asyncio.sleep(1)


# Add other endpoints or functions if needed
