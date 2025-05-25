# SimpleBoard

A simple message board built with FastAPI.

## Features

- User registration and login (JWT authentication)
- Post, update, and delete messages (only by the author)
- View all messages or a single message
- RESTful API design
- SQLite database (default)

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/SimpleBoard.git
   cd SimpleBoard
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   - Copy `app/dev/local.env.template` to `app/dev/local.env` and edit as needed.
   - (For tests) Copy `tests/dev/localtest.env.template` to `tests/dev/localtest.env` and edit as needed.

### Running the App

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### API Endpoints

#### User

- `POST /register` - Register a new user
- `POST /login` - Login and get JWT tokens
- `POST /refresh` - Refresh JWT tokens
- `DELETE /delete` - Delete current user (requires authentication)

#### Message

- `GET /messages` - Get all messages
- `GET /message/{message_id}` - Get a single message
- `POST /message` - Create a message (requires authentication)
- `PATCH /message/{message_id}` - Update a message (requires authentication, only author)
- `DELETE /message/{message_id}` - Delete a message (requires authentication, only author)

### Running Tests

```bash
pytest
```

## License

MIT License
