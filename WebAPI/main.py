from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# FastAPI app
app = FastAPI()

# Security scheme
security = HTTPBearer()

# Security settings
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



# Fake database
users_db = {}
products = {}

# Models
class User(BaseModel):
    username: str
    password: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class Product(BaseModel):
    name: str
    price: float
    stock: int

class LoginData(BaseModel):
    username: str
    password: str

# Password hashing and verification
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token creation
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Geçersiz kimlik doğrulama")
        return users_db[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz token")

# User registration
@app.post("/register")
def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kayıtlı.")
    users_db[user.username] = {"username": user.username, "email": user.email, "password": hash_password(user.password)}
    access_token = create_access_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"username": user.username, "email": user.email, "access_token": access_token}

# User login
@app.post("/login", response_model=Token)
def login(login_data: LoginData = Body(...)):
    user = users_db.get(login_data.username)
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")
    access_token = create_access_token({"sub": user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Delete account
@app.delete("/account")
def delete_account(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    if username in users_db:
        del users_db[username]
        user_products = [k for k, v in products.items() if v["owner"] == username]
        for product_id in user_products:
            del products[product_id]
        return {"message": "Hesap ve ilgili ürünler silindi"}
    raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

# User profile
@app.get("/profile")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "email": current_user["email"]}

# Product CRUD operations
@app.post("/products/{product_id}")
def create_product(product_id: int, product: Product, current_user: dict = Depends(get_current_user)):
    if product_id in products:
        raise HTTPException(status_code=400, detail="Bu ID zaten kullanılıyor.")
    products[product_id] = {"owner": current_user["username"], **product.dict()}
    return {"message": "Ürün eklendi", "product": products[product_id]}

@app.get("/products/")
def get_products(current_user: dict = Depends(get_current_user)):
    return {k: v for k, v in products.items() if v["owner"] == current_user["username"]}

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product, current_user: dict = Depends(get_current_user)):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    if products[product_id]["owner"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="Bu ürünü güncelleme yetkiniz yok.")
    products[product_id].update(product.dict())
    return {"message": "Ürün güncellendi", "product": products[product_id]}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, current_user: dict = Depends(get_current_user)):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    if products[product_id]["owner"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="Bu ürünü silme yetkiniz yok.")
    del products[product_id]
    return {"message": "Ürün silindi"}