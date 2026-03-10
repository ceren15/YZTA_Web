from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todoai_app.db"
#SQLALCHEMY_DATABASE_URL = "postgresq1://user:password@postgresserver/db"

engine = create_engine( # nasıl bağlantı açacağına bakıyor
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread" : False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)#Veri tabanıyla bağlantı açıyor.

Base = declarative_base()# base i alıp modellerimizi oluşturmada kullanıyoruz.

