import os
import uuid
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = os.path.expanduser("~/.cipher_talk/storage.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Device(Base):
    __tablename__ = "device"
    device_id = Column(String, primary_key=True)
    public_key = Column(String, nullable=False)

class Contact(Base):
    __tablename__ = "contacts"
    contact_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    public_key = Column(String, nullable=False)
    session_key = Column(String, nullable=False)

Base.metadata.create_all(engine)

class LocalStorage:
    @staticmethod
    def save_device(device_id: str, public_key: str):
        session = Session()
        session.merge(Device(device_id=device_id, public_key=public_key))
        session.commit()
        session.close()

    @staticmethod
    def save_contact(contact_id, username, ip, port, public_key, session_key):
        session = Session()
        contact = Contact(
            contact_id=contact_id,
            username=username,
            ip=ip,
            port=port,
            public_key=public_key,
            session_key=session_key
        )
        session.merge(contact)
        session.commit()
        session.close()

    @staticmethod
    def load_private_key():
        from keystore import KeyStore
        return KeyStore.unseal("device_private")
