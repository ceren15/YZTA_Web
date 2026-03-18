from fastapi import APIRouter, Depends, Path, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from models import Todo
from database import SessionLocal
from typing import Annotated
from routers.auth import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todo",# Bütün endpointlerin başına auth koyuyor.
    tags=["Todo"],#FastAPI/docs da başlıklara isim verdik.
)

templates = Jinja2Templates(directory="templates") # templates klasöründeki dosyaları kullanmak için templates değişkenini oluşturduk.

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=6)
    complete: bool

def get_db():
    db = SessionLocal()
    try:
        yield db # yield return gibi görevi vardır.
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)] # get_current_user fonksiyonundan dönen değeri user_dependency olarak kullanacağız.

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND) # Kullanıcı giriş yapmamışsa login sayfasına yönlendirme yapar.
    redirect_response.delete_cookie("access_token") # Kullanıcının tokenını siler.
    return redirect_response

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get(
            'access_token'))  # Kullanıcının tokenını alarak get_current_user fonksiyonunu çağırıyoruz. Eğer token geçerliyse kullanıcı bilgilerini döndürecektir.
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(
            Todo.owner_id == user.get('id')).all()  # Kullanıcının todolarını veritabanından çekiyoruz.
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get(
            'access_token'))  # Kullanıcının tokenını alarak get_current_user fonksiyonunu çağırıyoruz. Eğer token geçerliyse kullanıcı bilgilerini döndürecektir.
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get(
            'access_token'))  # Kullanıcının tokenını alarak get_current_user fonksiyonunu çağırıyoruz. Eğer token geçerliyse kullanıcı bilgilerini döndürecektir.
        if user is None:
            return redirect_to_login()

        todo = db.query(Todo).filter(
            Todo.id == todo_id).first()  # Kullanıcının todolarını veritabanından çekiyoruz.
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})
    except:
        return redirect_to_login()



@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all() # veritabanındaki tüm bilgileri getirir.


@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first() # İki tane filter koyma sebebimiz birincisi id ye göre filtreleme yaparken ikincisi de o id ye sahip olantodo nun gerçekten o kullanıcıya ait olup olmadığını kontrol ediyoruz. Çünkü bir kullanıcı başka bir kullanıcınıntodo sunu görememeli ve erişememelidir.

    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")


@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = Todo(**todo_request.dict(), owner_id=user.get('id')) # buradatodooluşturuyoruz.
    db.add(todo)# add dedikten sonra commit demeliyiz.
    db.commit()


@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete

    db.add(todo)
    db.commit()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    """
    #db.query(Todo).filter(Todo.id == todo_id).delete() # Burada genelde sildiğinden emin olmak için bu satırı yazarlar ama gerek yoktur aşağıdaki gibi db.delete(todo) ve commit yazsak yeterli olacaktır.
    """
    db.delete(todo)
    db.commit()
