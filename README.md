# Language Learning App - Backend

A FastAPI-based backend for a Language Learning Application with user authentication, role-based access control, and subscription management.

## Features

- **Authentication**: JWT-based authentication with access and refresh tokens
- **User Management**: Two user roles - `User` and `Admin`
- **Subscription System**: Premium subscription management with monthly/yearly plans
- **Clean Architecture**: Well-organized codebase following clean architecture principles
- **API Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **Flash Cards**: Store bilingual words and example sentences
- **Questions**: Multiple-choice questions with answers stored as array index (0->A, 1->B, etc.)
- **Question Sets**: Organize questions into sets with visibility types (normal/premium)

## Project Structure

```
app/
├── domain/                    # Domain layer (entities, repositories)
│   ├── entities/              # Domain entities (User, Subscription, Question, QuestionSet)
│   └── repositories/          # Repository interfaces
├── application/               # Application layer (use cases, services)
│   ├── dto/                   # Data Transfer Objects
│   ├── services/              # Business logic services
│   └── use_cases/             # Use case implementations
├── infrastructure/            # Infrastructure layer
│   ├── config/                # Configuration settings
│   ├── database/              # Database models and implementations
│   └── security/              # Security utilities (JWT, password hashing)
└── presentation/              # Presentation layer
    ├── api/                   # API endpoints
    │   ├── endpoints/         # Route handlers
    │   └── v1/                # API version 1 router
    └── middleware/            # Middleware (auth)
```

## Tech Stack

- **Framework**: FastAPI (0.115.0)
- **Pydantic**: v2.9.2 (Python 3.13 compatible)
- **Database**: SQLite3 (configurable for PostgreSQL)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Documentation**: Swagger UI / ReDoc

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd language-learning-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and get tokens | No |

### Users

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/v1/users/me` | Get current user info | Yes | Any |
| GET | `/api/v1/users/` | List all users | Yes | Admin |
| GET | `/api/v1/users/{id}` | Get user by ID | Yes | Admin/Owner |
| PUT | `/api/v1/users/{id}` | Update user | Yes | Admin/Owner |
| DELETE | `/api/v1/users/{id}` | Delete user | Yes | Admin |
| PATCH | `/api/v1/users/{id}/activate` | Activate user | Yes | Admin |
| PATCH | `/api/v1/users/{id}/deactivate` | Deactivate user | Yes | Admin |
| PATCH | `/api/v1/users/{id}/role` | Change user role | Yes | Admin |

### Subscriptions

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/api/v1/subscriptions/my-subscription` | Get my subscription | Yes | Any |
| GET | `/api/v1/subscriptions/` | List all subscriptions | Yes | Admin |
| GET | `/api/v1/subscriptions/status/active` | List active subscriptions | Yes | Admin |
| GET | `/api/v1/subscriptions/{id}` | Get subscription by ID | Yes | Admin/Owner |
| POST | `/api/v1/subscriptions/` | Create subscription | Yes | Admin |
| POST | `/api/v1/subscriptions/subscribe` | Subscribe or update plan | Yes | Any |
| POST | `/api/v1/subscriptions/{id}/cancel` | Cancel subscription | Yes | Admin/Owner |
| POST | `/api/v1/subscriptions/{id}/renew` | Renew subscription | Yes | Admin |

### Flash Cards

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/v1/flashcards/` | Create flash card | Yes | Any |
| GET | `/api/v1/flashcards/` | List flash cards | Yes | Any |
| GET | `/api/v1/flashcards/{id}` | Get flash card by ID | Yes | Any |
| PUT | `/api/v1/flashcards/{id}` | Update flash card | Yes | Creator/Admin |
| DELETE | `/api/v1/flashcards/{id}` | Delete flash card | Yes | Creator/Admin |
| GET | `/api/v1/flashcards/me/created` | List my flash cards | Yes | Any |
| GET | `/api/v1/flashcards/admin/all` | List all flash cards | Yes | Admin |

### Questions

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/v1/questions/` | Create question | Yes | Admin |
| GET | `/api/v1/questions/` | List questions (no answers) | Yes | Any |
| GET | `/api/v1/questions/{id}` | Get question (no answer) | Yes | Any |
| GET | `/api/v1/questions/{id}/answer` | Get answer (letter + text) | Yes | Admin |
| PUT | `/api/v1/questions/{id}` | Update question | Yes | Admin |
| DELETE | `/api/v1/questions/{id}` | Delete question | Yes | Admin |
| GET | `/api/v1/questions/me/created` | List my questions | Yes | Admin |

### Question Sets

| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| POST | `/api/v1/question-sets/` | Create question set | Yes | Admin |
| GET | `/api/v1/question-sets/` | List all question sets | Yes | Any |
| GET | `/api/v1/question-sets/{id}` | Get question set by ID | Yes | Any |
| GET | `/api/v1/question-sets/type/{type}` | List sets by type (normal/premium) | Yes | Any |
| PUT | `/api/v1/question-sets/{id}` | Update question set | Yes | Admin |
| DELETE | `/api/v1/question-sets/{id}` | Delete question set | Yes | Admin |
| POST | `/api/v1/question-sets/{id}/questions` | Add question to set | Yes | Admin |
| DELETE | `/api/v1/question-sets/{id}/questions/{qid}` | Remove question from set | Yes | Admin |
| GET | `/api/v1/question-sets/{id}/questions` | Get questions in set | Yes | Any |

## Question System

### Answer Index Format

Questions store answers as array indices (0, 1, 2, ...) which map to letters:
- 0 → A
- 1 → B
- 2 → C
- 3 → D
- etc.

This provides:
- Validation: Answer index cannot exceed the number of choices
- Compact storage: Store integer instead of full string
- Letter display: Automatically convert to A, B, C, D for display

### Question Sets

Question Sets allow organizing questions into collections with visibility control:

**Set Types:**
- `normal` - Available to all users
- `premium` - Available to premium subscribers only

**Features:**
- Add/remove questions from sets
- Filter sets by type
- Get question count per set
- Many-to-many relationship (questions can be in multiple sets)

### Example Question Creation

```json
{
  "prompt": "What is the capital of France?",
  "choices": ["London", "Paris", "Berlin", "Madrid"],
  "answer_index": 1
}
```

The answer_index `1` corresponds to "B" (Paris).

### Example Question Response

```json
{
  "id": 1,
  "prompt": "What is the capital of France?",
  "choices": [
    {"letter": "A", "text": "London"},
    {"letter": "B", "text": "Paris"},
    {"letter": "C", "text": "Berlin"},
    {"letter": "D", "text": "Madrid"}
  ],
  "created_by": 1,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Example Answer Response

```json
{
  "id": 1,
  "answer_letter": "B",
  "answer_text": "Paris"
}
```

## User Roles

### User
- Can view and update their own profile
- Can manage their own subscriptions
- Can subscribe to premium plans
- Can view normal question sets
- Can view premium question sets (if subscribed)

### Admin
- Full access to all user management endpoints
- Can create, update, delete any user
- Can manage all subscriptions
- Can change user roles
- Can create and manage questions
- Can create and manage question sets
- Can view question answers

## Testing with Swagger

1. Open Swagger UI at `http://localhost:8000/docs`
2. Register a new user using `POST /api/v1/auth/register`
3. Login using `POST /api/v1/auth/login` with the registered credentials
4. Click the "Authorize" button at the top of the page
5. Enter the access token (format: `Bearer <token>`)
6. Now you can test authenticated endpoints

### Creating an Admin User (Dev Seed)

A development admin user is automatically created on startup along with sample questions, question sets, and flashcards:

- **Email**: `admin@example.com`
- **Username**: `admin`
- **Password**: `admin123`

You can use these credentials to log in via Swagger or `/api/v1/auth/login`.

If you prefer to update an existing user manually, here's an example:

```python
# In Python shell or script
from app.infrastructure.database import SessionLocal
from app.infrastructure.database.models import UserModel
from app.domain.entities.user import UserRole

db = SessionLocal()
user = db.query(UserModel).filter(UserModel.email == "admin@example.com").first()
user.role = UserRole.ADMIN
db.commit()
```

## Database

The application uses SQLite by default. The database file `language_learning.db` is created in the project root directory.

To switch to PostgreSQL later, update the `DATABASE_URL` in the settings:

```python
# app/infrastructure/config/settings.py
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

## Configuration

Environment variables can be set in a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./language_learning.db
```

## Security Notes

- Change the default `SECRET_KEY` in production
- Use HTTPS in production
- Configure CORS appropriately for your frontend domain
- Store sensitive configuration in environment variables

## Troubleshooting

### Python 3.13+ Compatibility

This project uses **Pydantic v2** (2.9.2) which is fully compatible with Python 3.13+. If you encounter errors like:

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

This is due to using an older version of Pydantic v1 that is incompatible with Python 3.13. The `requirements.txt` has been updated to use Pydantic v2 which fixes this issue.

**Key differences in Pydantic v2:**
1. Use `model_config = ConfigDict(from_attributes=True)` instead of `class Config: orm_mode = True`
2. Use `.model_dump()` instead of `.dict()` for model serialization
3. Import `BaseSettings` from `pydantic_settings` instead of `pydantic`

### Database Issues

If you get database errors on first run, the tables should be created automatically. If not, you can create them manually:

```python
from app.infrastructure.database import engine, Base
Base.metadata.create_all(bind=engine)
```

### Port Already in Use

If port 8000 is already in use, you can specify a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

## Future Enhancements

- Email verification
- Password reset functionality
- Payment integration for subscriptions
- Lesson/content management
- Progress tracking
- Analytics dashboard
- Question filtering by difficulty
- Quiz/test mode for question sets
- Time limits for questions
