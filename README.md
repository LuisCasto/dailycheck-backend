# DailyCheck Backend

Backend para una aplicacion de seguimiento de habitos, construido con FastAPI, SQLAlchemy, PostgreSQL y Alembic.

Este `README` tiene dos objetivos:

1. Explicar como funciona el proyecto.
2. Explicar la sintaxis principal que aparece en el codigo para que puedas leerlo y modificarlo con mas seguridad.

## 1. Que hace este backend

La API permite:

- registrar usuarios
- iniciar sesion
- autenticar con JWT
- crear, listar, editar y eliminar habitos
- registrar si un habito se cumplio en una fecha
- guardar notas en los registros
- calcular estadisticas basicas

## 2. Tecnologias del proyecto

- `FastAPI`: framework para crear APIs en Python
- `SQLAlchemy`: ORM para trabajar con la base de datos desde clases Python
- `PostgreSQL`: base de datos relacional
- `Alembic`: migraciones de la base de datos
- `Pydantic`: validacion de datos de entrada y salida
- `bcrypt`: hash de contrasenas
- `python-jose`: manejo de tokens JWT
- `uvicorn`: servidor ASGI para ejecutar FastAPI

## 3. Estructura del proyecto

```text
dailycheck-backend/
├── app/
│   ├── core/
│   │   ├── auth.py
│   │   └── security.py
│   ├── models/
│   │   ├── user.py
│   │   ├── habit.py
│   │   └── habit_log.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── habits.py
│   │   └── logs.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── habit.py
│   │   └── habit_log.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── Procfile
├── requirements.txt
├── runtime.txt
└── .python-version
```

## 4. Como pensar este proyecto

Si sabes Python basico, esta es la idea mental correcta:

- `main.py` une toda la aplicacion
- `routers/` define las rutas HTTP
- `schemas/` valida lo que entra y lo que sale
- `models/` define las tablas
- `database.py` crea la conexion y sesiones
- `core/` guarda autenticacion y seguridad
- `alembic/` guarda cambios de estructura de la base de datos

## 5. Flujo general de una peticion

Ejemplo: crear un habito.

1. El frontend envia un `POST /api/habits`.
2. FastAPI recibe la peticion y la manda al router correcto.
3. `Depends(get_current_user)` valida el token.
4. `Depends(get_db)` crea una sesion de base de datos.
5. `HabitCreate` valida el JSON recibido.
6. Se crea un objeto `Habit`.
7. SQLAlchemy lo guarda.
8. FastAPI devuelve la respuesta usando `HabitOut`.

## 6. Sintaxis clave de FastAPI

### 6.1 Decoradores como `@router.get(...)`

En Python, un decorador empieza con `@` y modifica el comportamiento de una funcion.

Ejemplo del proyecto:

```python
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    ...
```

Eso significa:

"Cuando llegue un `POST` a `/login`, ejecuta esta funcion".

Las variantes mas comunes son:

- `@router.get(...)`
- `@router.post(...)`
- `@router.put(...)`
- `@router.patch(...)`
- `@router.delete(...)`

Cada una corresponde a un metodo HTTP.

### 6.2 Parametros tipados

Ejemplo:

```python
def login(data: UserLogin, db: Session = Depends(get_db)):
```

Aqui hay dos ideas:

- `data: UserLogin`
  Significa que `data` debe seguir la forma definida por el schema `UserLogin`.

- `db: Session`
  Significa que `db` sera una sesion SQLAlchemy.

El uso de `:` en Python indica el tipo esperado. A eso se le llama type hint.

### 6.3 `Depends(...)`

`Depends` es una pieza central de FastAPI.

Ejemplo:

```python
db: Session = Depends(get_db)
```

Esto significa:

"FastAPI, antes de ejecutar esta funcion, llama a `get_db()` y coloca el resultado en `db`".

En este proyecto se usa para dos cosas principales:

- obtener la sesion de base de datos
- obtener el usuario autenticado

Ejemplo:

```python
current_user: User = Depends(get_current_user)
```

### 6.4 `response_model`

Ejemplo:

```python
@router.post("/register", response_model=UserOut, status_code=201)
```

Esto significa:

- la respuesta se va a serializar con `UserOut`
- FastAPI mostrara ese formato en la documentacion
- el codigo HTTP esperado sera `201`

`response_model` es muy util porque evita devolver datos sensibles por accidente, como `hashed_password`.

### 6.5 `status_code`

Ejemplo:

```python
status_code=201
```

Significa que si todo sale bien, la respuesta sera `201 Created`.

Otros codigos comunes:

- `200`: ok
- `201`: creado
- `204`: sin contenido
- `400`: error del cliente
- `401`: no autorizado
- `404`: no encontrado

## 7. `main.py`: punto de entrada

Archivo: [app/main.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/main.py)

Este archivo:

- crea la app FastAPI
- configura CORS
- registra los routers
- expone `/health`
- personaliza OpenAPI para usar Bearer token

Fragmento importante:

```python
app = FastAPI(title="DailyCheck API")
```

Eso crea la aplicacion principal.

Luego:

```python
app.include_router(auth.router)
app.include_router(habits.router)
app.include_router(logs.router)
```

Eso conecta las rutas definidas en otros archivos con la app principal.

## 8. CORS explicado simple

En [app/main.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/main.py) aparece:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://dailycheck-salsa.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Esto permite que el frontend haga peticiones al backend desde esos origenes.

Si no configuras CORS, el navegador puede bloquear la comunicacion aunque el backend este bien.

## 9. Variables de entorno y configuracion

Archivo: [app/config.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/config.py)

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
```

### Sintaxis a entender

- `class Settings(BaseSettings):`
  Define una clase que hereda de `BaseSettings`.

- `DATABASE_URL: str`
  Declara un atributo obligatorio de tipo texto.

- `ALGORITHM: str = "HS256"`
  Declara un atributo con valor por defecto.

La herencia se ve asi:

```python
class Hija(Padre):
    ...
```

Eso significa que `Hija` reutiliza el comportamiento de `Padre`.

En este caso, `Settings` hereda capacidades de `BaseSettings`, como leer variables del entorno.

## 10. Conexion a base de datos

Archivo: [app/database.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/database.py)

```python
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### Que significa cada linea

- `create_engine(...)`
  Crea el motor de conexion hacia la base.

- `sessionmaker(...)`
  Fabrica sesiones de base de datos.

- `declarative_base()`
  Crea la clase base para los modelos.

### Funcion generadora con `yield`

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Esto usa `yield`, que convierte la funcion en un generador.

Idea simple:

- entrega `db`
- cuando FastAPI termina de usarla, ejecuta el bloque `finally`
- ahi se cierra la sesion

`yield` se parece a `return`, pero permite "pausar" la funcion y continuar despues.

## 11. Modelos SQLAlchemy

Los modelos estan en:

- [app/models/user.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/models/user.py)
- [app/models/habit.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/models/habit.py)
- [app/models/habit_log.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/models/habit_log.py)

### Ejemplo de sintaxis de un modelo

```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
```

### Como leer esto

- `class User(Base):`
  `User` es una tabla modelada como clase Python.

- `__tablename__ = "users"`
  El nombre real de la tabla en PostgreSQL sera `users`.

- `id = Column(...)`
  Define una columna.

- `primary_key=True`
  Indica clave primaria.

- `nullable=False`
  No permite `NULL`.

### Relaciones

Ejemplo:

```python
habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
```

Eso significa:

- un usuario tiene muchos habitos
- la relacion inversa esta en `Habit.user`
- si se elimina el usuario, sus habitos pueden eliminarse tambien segun la configuracion

## 12. Schemas Pydantic

Los schemas estan en:

- [app/schemas/user.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/schemas/user.py)
- [app/schemas/habit.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/schemas/habit.py)
- [app/schemas/habit_log.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/schemas/habit_log.py)

### Ejemplo

```python
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
```

Esto define el formato esperado para registrar un usuario.

### Diferencia entre model y schema

- model SQLAlchemy: representa tabla
- schema Pydantic: representa datos que entran o salen por la API

### `Optional` y `Literal`

En `habit.py` aparece:

```python
from typing import Optional, Literal
```

`Optional[int]` significa:

- puede ser `int`
- o puede ser `None`

`Literal["daily", "weekly", "monthly"]` significa:

- solo acepta uno de esos valores exactos

Ejemplo:

```python
FrequencyType = Literal["daily", "weekly", "monthly"]
```

Eso sirve para restringir mejor la entrada.

## 13. Routers del proyecto

### 13.1 Auth

Archivo: [app/routers/auth.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/auth.py)

Base: `/api/auth`

Endpoints:

- `POST /api/auth/register`
- `GET /api/auth/stats`
- `POST /api/auth/login`
- `GET /api/auth/me`

### 13.2 Habits

Archivo: [app/routers/habits.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/habits.py)

Base: `/api/habits`

Endpoints:

- `GET /api/habits`
- `POST /api/habits`
- `PUT /api/habits/{habit_id}`
- `DELETE /api/habits/{habit_id}`

### 13.3 Logs

Archivo: [app/routers/logs.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/logs.py)

Base: `/api/logs`

Endpoints:

- `GET /api/logs`
- `POST /api/logs`
- `GET /api/logs/stats/{habit_id}`
- `PATCH /api/logs/{log_id}/note`

## 14. Sintaxis comun dentro de los routers

### 14.1 Crear registros

```python
user = User(
    name=data.name,
    email=data.email,
    hashed_password=hash_password(data.password),
)
db.add(user)
db.commit()
db.refresh(user)
```

### Como leerlo

- `User(...)` crea una instancia del modelo
- `db.add(user)` la pone en la sesion
- `db.commit()` confirma en la base
- `db.refresh(user)` vuelve a leer valores actualizados

### 14.2 Consultar datos

```python
user = db.query(User).filter(User.email == data.email).first()
```

Lectura paso a paso:

- `db.query(User)` inicia una consulta sobre la tabla `users`
- `.filter(...)` agrega condicion
- `.first()` devuelve el primer resultado o `None`

### 14.3 Actualizar campos dinamicamente

En `habits.py` aparece:

```python
for field, value in data.model_dump(exclude_unset=True).items():
    setattr(habit, field, value)
```

Esto significa:

- convertir el schema a diccionario
- ignorar campos no enviados
- recorrer cada par `campo, valor`
- usar `setattr` para cambiar atributos del objeto

`setattr(objeto, "name", "nuevo")` equivale a escribir:

```python
objeto.name = "nuevo"
```

pero de forma dinamica.

## 15. Autenticacion y JWT

Archivo: [app/core/auth.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/core/auth.py)

### Crear token

```python
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### Sintaxis util aqui

- `-> str`
  Indica que la funcion devuelve un `str`.

- `data.copy()`
  Crea una copia del diccionario para no modificar el original.

- `to_encode.update({...})`
  Agrega o reemplaza claves dentro del diccionario.

### Obtener usuario autenticado

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
```

Esta funcion:

- toma el token desde el header `Authorization`
- lo decodifica
- saca el `sub`
- busca al usuario en la base

Si no encuentra un usuario valido, responde con `401`.

## 16. Seguridad de contrasenas

Archivo: [app/core/security.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/core/security.py)

```python
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```

### Sintaxis util aqui

- `.encode("utf-8")`
  Convierte texto a bytes.

- `.decode("utf-8")`
  Convierte bytes a texto.

Se usa porque `bcrypt` trabaja con bytes, no con strings normales.

## 17. Alembic explicado simple

Alembic sirve para controlar cambios en la estructura de la base de datos.

Ejemplo:

- hoy tu tabla `habits` no tiene `frequency`
- cambias el modelo
- creas una migracion
- Alembic aplica ese cambio a la base real

### Archivos importantes

- [alembic/env.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/alembic/env.py)
- [alembic/versions/528d1c3abfde_initial_tables.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/alembic/versions/528d1c3abfde_initial_tables.py)
- [alembic/versions/58d8cf90abee_add_frequency_to_habits.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/alembic/versions/58d8cf90abee_add_frequency_to_habits.py)

### `upgrade()` y `downgrade()`

En una migracion veras funciones como estas:

```python
def upgrade() -> None:
    ...

def downgrade() -> None:
    ...
```

- `upgrade()` aplica el cambio
- `downgrade()` lo revierte

### `env.py`

Ese archivo conecta Alembic con tu app:

- toma `DATABASE_URL`
- carga `Base.metadata`
- ejecuta migraciones online u offline

## 18. Comandos utiles

### Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Instalar dependencias

```powershell
pip install -r requirements.txt
```

### Configurar variables de entorno

Crea un archivo `.env` en la raiz:

```env
DATABASE_URL=postgresql://usuario:password@host:puerto/dbname
SECRET_KEY=tu_clave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Aplicar migraciones

```powershell
alembic upgrade head
```

### Levantar servidor en local

```powershell
uvicorn app.main:app --reload
```

### Crear una nueva migracion

```powershell
alembic revision --autogenerate -m "descripcion del cambio"
```

## 19. Documentacion automatica de FastAPI

Si ejecutas la app, puedes entrar a:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

`/docs` es especialmente util para aprender porque:

- muestra todos los endpoints
- muestra los schemas
- deja probar requests desde el navegador

## 20. Ejemplos de uso

### Registrar usuario

`POST /api/auth/register`

```json
{
  "name": "Axel",
  "email": "axel@example.com",
  "password": "123456"
}
```

### Login

`POST /api/auth/login`

```json
{
  "email": "axel@example.com",
  "password": "123456"
}
```

Respuesta:

```json
{
  "access_token": "TOKEN",
  "token_type": "bearer"
}
```

### Crear habito

`POST /api/habits`

Header:

```text
Authorization: Bearer TOKEN
```

Body:

```json
{
  "name": "Tomar agua",
  "description": "Mantenerme hidratado",
  "category": "Salud",
  "icon": "agua",
  "daily_task": "Beber 2 litros",
  "target_value": 2,
  "unit": "litros",
  "frequency": "daily",
  "times_per_period": 1
}
```

### Registrar cumplimiento de habito

`POST /api/logs`

```json
{
  "habit_id": "UUID_DEL_HABITO",
  "date": "2026-04-24",
  "note": "Cumplido antes de las 8 pm"
}
```

## 21. Despliegue en Render

El archivo [Procfile](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/Procfile) contiene:

```text
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Eso significa:

1. Render aplica migraciones.
2. Luego arranca la API.

Archivos importantes para el deploy:

- [runtime.txt](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/runtime.txt)
- [.python-version](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/.python-version)
- [Procfile](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/Procfile)

Actualmente Python esta fijado a `3.12.0`.

## 22. Problemas conocidos en el codigo actual

Hay dos detalles importantes que conviene que conozcas:

- en varios mensajes aparecen caracteres mal codificados, por ejemplo `HÃ¡bito`
- en [app/routers/logs.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/logs.py) el endpoint `GET /api/logs/stats/{habit_id}` tiene un problema de flujo: el `return StatsOut(...)` quedo mal ubicado y asi no responde como deberia

## 23. Orden recomendado para estudiar el backend

Si quieres aprender leyendo el codigo, sigue este orden:

1. [app/main.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/main.py)
2. [app/config.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/config.py)
3. [app/database.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/database.py)
4. [app/models/user.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/models/user.py), [habit.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/models/habit.py) y [habit_log.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/models/habit_log.py)
5. [app/schemas/user.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/schemas/user.py), [habit.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/schemas/habit.py) y [habit_log.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/schemas/habit_log.py)
6. [app/routers/auth.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/auth.py)
7. [app/core/auth.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/core/auth.py)
8. [app/routers/habits.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/habits.py)
9. [app/routers/logs.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/app/routers/logs.py)
10. [alembic/env.py](/C:/Users/axel_/OneDrive/Escritorio/dailycheck-backend/alembic/env.py)
11. migraciones en `alembic/versions/`

## 24. Resumen final

Si recuerdas solo 4 ideas, que sean estas:

1. FastAPI usa routers, decoradores y `Depends`.
2. Pydantic valida los datos que entran y salen.
3. SQLAlchemy representa tablas como clases Python.
4. Alembic versiona cambios de la base de datos.

Con eso ya puedes empezar a leer, mantener y ampliar este backend con bastante control.
