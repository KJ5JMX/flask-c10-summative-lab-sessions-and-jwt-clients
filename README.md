# Flask Notes API (JWT Authentication)

This project is a RESTful Flask API that provides user authentication using JWT and full CRUD functionality for user-owned notes. Notes are scoped per user and support pagination.

There is **no frontend**. All interaction is done via HTTP requests using tools such as `curl` or Postman.

---

## Features

- User signup and login
- Password hashing with bcrypt
- JWT-based authentication
- Protected routes
- Notes CRUD (Create, Read, Update, Delete)
- Notes scoped to the authenticated user
- Pagination support on notes index
- Proper validation and error handling

---

## Tech Stack

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-Bcrypt
- SQLite

---

## Project Structure

```
server/
├── app.py              # Main application with routes and business logic
├── models.py           # Database models (User, Note)
├── config.py           # Configuration (database, JWT, etc.)
├── seed.py             # Database seeding script (currently unused)
├── migrations/         # Alembic database migrations
├── Pipfile             # Python dependencies
└── Pipfile.lock        # Locked dependency versions
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/KJ5JMX/flask-c10-summative-lab-sessions-and-jwt-clients.git
cd flask-c10-summative-lab-sessions-and-jwt-clients/server
```

### 2. Install Dependencies

```bash
pipenv install
pipenv shell
```

### 3. Set Environment Variables

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export JWT_SECRET_KEY=super-secret-key
```

### 4. Initialize Database

```bash
flask db upgrade
```

### 5. Run the Server

```bash
python app.py
```

The server will be available at: `http://localhost:5555`

---

## API Endpoints

### Public Endpoints

#### GET `/`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### POST `/signup`
Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe"
}
```

**Validation:**
- Username and password are required
- Password must be at least 6 characters
- Username must be unique

**Example with curl:**
```bash
curl -X POST http://localhost:5555/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securepassword123"}'
```

#### POST `/login`
Authenticate and receive a JWT access token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:5555/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securepassword123"}'
```

---

### Protected Endpoints (Require JWT)

All protected endpoints require the `Authorization` header with the JWT token:
```
Authorization: Bearer <your_access_token>
```

#### GET `/me`
Get the current authenticated user's profile.

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe"
}
```

**Example with curl:**
```bash
curl -X GET http://localhost:5555/me \
  -H "Authorization: Bearer <your_access_token>"
```

#### GET `/notes`
Get all notes for the authenticated user with pagination support.

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `per_page` (optional, default: 10) - Number of notes per page

**Response (200 OK):**
```json
{
  "notes": [
    {
      "id": 1,
      "title": "My First Note",
      "content": "This is the content of my first note",
      "user_id": 1
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 1
}
```

**Example with curl:**
```bash
# Get first page with 10 notes
curl -X GET http://localhost:5555/notes \
  -H "Authorization: Bearer <your_access_token>"

# Get second page with 5 notes per page
curl -X GET "http://localhost:5555/notes?page=2&per_page=5" \
  -H "Authorization: Bearer <your_access_token>"
```

#### POST `/notes`
Create a new note.

**Request Body:**
```json
{
  "title": "My Note Title",
  "content": "This is the note content"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "My Note Title",
  "content": "This is the note content",
  "user_id": 1
}
```

**Validation:**
- Both title and content are required
- Both fields must not be empty after trimming whitespace

**Example with curl:**
```bash
curl -X POST http://localhost:5555/notes \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Note Title", "content": "This is the note content"}'
```

#### GET `/notes/<note_id>`
Get a specific note by ID (must belong to authenticated user).

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "My Note Title",
  "content": "This is the note content",
  "user_id": 1
}
```

**Example with curl:**
```bash
curl -X GET http://localhost:5555/notes/1 \
  -H "Authorization: Bearer <your_access_token>"
```

#### PATCH `/notes/<note_id>`
Update a specific note (must belong to authenticated user).

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content"
}
```

**Note:** You can update just the title, just the content, or both. At least one field must be provided.

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Title",
  "content": "Updated content",
  "user_id": 1
}
```

**Example with curl:**
```bash
# Update both title and content
curl -X PATCH http://localhost:5555/notes/1 \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", "content": "Updated content"}'

# Update only the title
curl -X PATCH http://localhost:5555/notes/1 \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

#### DELETE `/notes/<note_id>`
Delete a specific note (must belong to authenticated user).

**Response (204 No Content):**
No response body.

**Example with curl:**
```bash
curl -X DELETE http://localhost:5555/notes/1 \
  -H "Authorization: Bearer <your_access_token>"
```

---

## Testing the API

### Complete Workflow Example

1. **Sign up a new user:**
```bash
curl -X POST http://localhost:5555/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

2. **Login and save the token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:5555/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
```

3. **Create a note:**
```bash
curl -X POST http://localhost:5555/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Shopping List", "content": "Milk, Eggs, Bread"}'
```

4. **Get all notes:**
```bash
curl -X GET http://localhost:5555/notes \
  -H "Authorization: Bearer $TOKEN"
```

5. **Update a note:**
```bash
curl -X PATCH http://localhost:5555/notes/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Milk, Eggs, Bread, Butter"}'
```

6. **Delete a note:**
```bash
curl -X DELETE http://localhost:5555/notes/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Responses

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request` - Invalid input or validation error
- `401 Unauthorized` - Invalid credentials or missing/invalid token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "error": "Error message description"
}
```

---

## Database Models

### User
- `id` - Integer (Primary Key)
- `username` - String (Unique, Required)
- `password_hash` - String (Required)

### Note
- `id` - Integer (Primary Key)
- `title` - String (Required)
- `content` - Text (Required)
- `user_id` - Integer (Foreign Key to User)

---

## Security Features

- Passwords are hashed using bcrypt before storage
- JWT tokens are used for authentication
- Notes are scoped to the authenticated user
- Input validation on all user-provided data
- SQL injection protection via SQLAlchemy ORM

---

## Development Notes

- The database is SQLite by default (`app.db` in the server directory)
- Debug mode is enabled for development
- The server runs on port 5555
- JWT tokens do not expire by default (consider adding expiration in production)

---

## Troubleshooting

**Issue: "Module not found" errors**
- Make sure you're in the pipenv shell: `pipenv shell`
- Reinstall dependencies: `pipenv install`

**Issue: Database errors**
- Delete `app.db` and run `flask db upgrade` again
- Check that migrations exist in `migrations/versions/`

**Issue: JWT token not working**
- Make sure you're including the `Bearer` prefix in the Authorization header
- Verify the token hasn't been truncated when copying
- Check that JWT_SECRET_KEY environment variable matches between requests

---

## License

This project is for educational purposes.
