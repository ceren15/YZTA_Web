from routers.auth import router as auth_router
from routers.todo import router as todo_router

from fastapi import FastAPI
from models import Base
from database import engine


app = FastAPI()

app.include_router(auth_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine) # ToDoGemini kalasörünün altında veri tabanı oluşturmamızı sağlıyor Base ve engine importlarını kullanarak bunu yaptık.
# terminalde uvicorn main:app --reload ile çalıştırdıktan sonra db miz oluşuyor ve bu db ye ilk yöntem olarak terminalde splite3 todoai_app.db yazarak veri tabanımızı çalıştırıyoruz daha sonrasında select*from todos; komutu ile içindekileri listeliyoruz eklemek istediğimizde ise INSERT INTO todos (title,description,priorty) VALUES ('test','test2',1); komutu ile girerek veri tabanımıza manuel ekleme yapıyoruz. Veritabanından çıkmak için .exit yazıyoruz.
# cls ile terminali temizleyebiliyoruz.




