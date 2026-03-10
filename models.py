from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todo(Base):# Bu Base modelimizi database.py nin içinden çağırıyoruz çünkü sql deki tablolarımızı oluşturmaktan sorumludur bu class.
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)#önceliklendirme
    complete = Column(Boolean, default=False) #Tamamlanıp tamamlanmadığı(0-1)
    owner_id = Column(Integer, ForeignKey('users.id'))
    #Her kullanıcının kendine özeltodo su olması için eşleştirmemiz gerekiyor.
    #Veri tabanına sonradan eklemek sıkıntılıdır migration işlemleriyle bunu hallederiz ama şimdilik veri tabanımızda çok az veri olduğunsan silip tekrardan çalıştırıyoruz.


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)