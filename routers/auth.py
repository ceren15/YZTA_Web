from fastapi import APIRouter, Depends , HTTPException, Request
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal
from models import User
from passlib.context import CryptContext
#şifreleme yapmak için kütüphanedir.
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.templating import Jinja2Templates

# Routeri ayrı FastAPI de değilde aynı API da gözükmesini istediğimiz için router kullanıyoruz.
router = APIRouter(
    prefix="/auth",# Bütün endpointlerin başına auth koyuyor.
    tags=["Authentication"],#FastAPI/docs da başlıklara isim verdik.
)

templates = Jinja2Templates(directory="templates") # templates klasöründeki dosyaları kullanmak için templates değişkenini oluşturduk.

SECRET_KEY = "w6plreohmfzn9a3q0wly25pqm7kn4nbh8rdia4al1ila7dw1swb1jp95posuxif9"
ALGORITHM = "HS256"

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    payload = {'sub': username, 'id': user_id, 'role': role}
    expire = datetime.now(timezone.utc) + expires_delta # token kullanım süresi
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) # token oluşturma işlemi


def get_db():
    db = SessionLocal()
    try:
        yield db # yield return gibi görevi vardır.
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # şifreleme algoritması olarak bcrypt kullanıyoruz.
oath2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token") # token oluşturmak için kullanacağımız endpointi belirtiyoruz.
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel): # Bunu sınıfı token oluşturmak için kullanacağız. Çünkü token oluştururken bize access_token ve token_type bilgisi lazım olacak.
    access_token: str
    token_type: str
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]): # Bu fonsiyonu yazma amacımız tokenın geçerli olup olmadığını kontrol etmek ve token içindeki bilgileri almak. Bu fonksiyonu diğer endpointlerde kullanarak sadece doğrulanmış kullanıcıların erişmesini sağlayacağız.
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or ID is invalid")
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})







@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user_request: CreateUserRequest):
    user = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        is_active=True,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        phone_number=create_user_request.phone_number
    )
    db.add(user)
    db.commit()


@router.post("/token", response_model=Token)# token gerçek kullanıcıdan mı geliyor vs kontrolü için kullanılır.
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}
# JWT : JSON Web Token, kullanıcı doğrulama ve yetkilendirme işlemlerinde kullanılan bir standarttır. Kullanıcı giriş yaptıktan sonra, sunucu tarafından oluşturulan ve imzalanan bir token'ı istemciye gönderir. İstemci, bu token'ı sonraki isteklerde kimlik doğrulama için kullanır. JWT, kullanıcı bilgilerini güvenli bir şekilde taşımak için kullanılır ve genellikle "Bearer" token olarak adlandırılır.
















