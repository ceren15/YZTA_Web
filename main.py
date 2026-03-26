from .routers.auth import router as auth_router
from .routers.todo import router as todo_router
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
from fastapi import FastAPI, Request
from .models import Base
from .database import engine
import os
"""
Relative import, bir modülün aynı paket içindeki diğer modüllere erişmesini sağlar. Örneğin, from .routers.auth import router ifadesi, routers klasöründeki auth.py dosyasındaki router değişkenini içe aktarır. Bu sayede auth.py dosyasındaki router değişkenine main.py dosyasında erişebiliriz.
Bunu kullanmamamızın sebebi main.py dosyasının doğrudan çalıştırılabilir bir dosya olmasıdır. Eğer main.py dosyasını doğrudan çalıştırırsak, Python bu dosyayı __main__ olarak tanımlar ve relative importlar çalışmaz. Bu nedenle, main.py dosyasını çalıştırırken python -m main komutunu kullanarak main modülünü çalıştırmalıyız. Bu şekilde Python, main.py dosyasını bir modül olarak tanır ve relative importlar sorunsuz bir şekilde çalışır.
"""
app = FastAPI()

script_dir = os.path.dirname(__file__) # scriptin bulunduğu dizini alır.
st_abs_file_path = os.path.join(script_dir, "static/") # static klasörünün tam yolunu oluşturur.

app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static") # static dosyaları sunmak için kullanılır. Bu sayede static klasöründeki dosyalara erişebiliriz.

@app.get("/")
def read_root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND) # Ana sayfaya erişildiğinde otomatik olarak /docs sayfasına yönlendirme yapar. Bu sayede kullanıcılar API dokümantasyonuna kolayca erişebilirler.

app.include_router(auth_router)
app.include_router(todo_router)

Base.metadata.create_all(bind=engine) # ToDoGemini kalasörünün altında veri tabanı oluşturmamızı sağlıyor Base ve engine importlarını kullanarak bunu yaptık.
# terminalde uvicorn main:app --reload ile çalıştırdıktan sonra db miz oluşuyor ve bu db ye ilk yöntem olarak terminalde splite3 todoai_app.db yazarak veri tabanımızı çalıştırıyoruz daha sonrasında select*from todos; komutu ile içindekileri listeliyoruz eklemek istediğimizde ise INSERT INTO todos (title,description,priorty) VALUES ('test','test2',1); komutu ile girerek veri tabanımıza manuel ekleme yapıyoruz. Veritabanından çıkmak için .exit yazıyoruz.
# cls ile terminali temizleyebiliyoruz.




