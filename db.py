from sqlalchemy import URL ,create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

url = URL.create("postgresql+psycopg2",username=settings.db_user, password=settings.db_password, host=settings.db_host, port=settings.db_port, database=settings.db_name)
engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)

url_read= URL.create("postgresql+psycopg2",username=settings. db_read_user, password=settings.db_read_password, host=settings.db_host, port=settings.db_port, database=settings.db_name)
engine_read = create_engine(url_read)
SessionLocal_read = sessionmaker(bind=engine_read)


