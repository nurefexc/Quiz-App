# Quiz Website - Flask Application

A multi-language quiz website with admin interface, built with Flask.

## Features

- **Multi-language support**: English and Hungarian (easily extensible for more languages)
- **Admin interface**: Create and manage quizzes, events, and teams
- **Team management**: Users can join teams with configurable maximum sizes
- **Quiz system**: Multiple choice questions with scoring
- **Event management**: Schedule quiz events with start/end times
- **Docker support**: Easy deployment with Docker Compose

## Project Structure

```
FlaskProject/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   ├── main/                # Main routes
│   ├── auth/                # Authentication routes
│   ├── admin/               # Admin interface
│   ├── quiz/                # Quiz functionality
│   └── templates/           # HTML templates
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image
├── docker-compose.yml      # Docker Compose configuration
└── run.py                   # Application entry point
```

## Setup Instructions

### Local Development

1. **Clone the repository**
   ```bash
   cd FlaskProject
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

5. **Compile translations**
   ```bash
   pybabel compile -d app/translations
   ```

6. **Create an admin user**
   Run Python and execute:
   ```python
   from app import create_app, db
   from app.models import User

   app = create_app()
   with app.app_context():
       admin = User(username='admin', email='admin@example.com', is_admin=True)
       admin.set_password('your-password')
       db.session.add(admin)
       db.session.commit()
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

   The app will be available at `http://localhost:5000`

### Docker Deployment

1. **Build and run with Docker Compose (Demo Mode)**
   ```bash
   docker-compose up --build
   ```

   By default, this runs in **demo mode** which automatically loads sample data including:
   - Admin user (username: `admin`, password: `admin123`)
   - 5 regular users (username: `user1`-`user5`, password: `user123`)
   - A sample quiz with 5 questions
   - An active event
   - 3 teams with users assigned

   The app will be available at `http://localhost:5000`

2. **Run without demo mode (clean installation)**
   ```bash
   DEMO_MODE=false docker-compose up --build
   ```

3. **Create an admin user (if not using demo mode)**
   ```bash
   docker-compose exec web python
   ```
   Then run:
   ```python
   from app import create_app, db
   from app.models import User

   app = create_app()
   with app.app_context():
       admin = User(username='admin', email='admin@example.com', is_admin=True)
       admin.set_password('your-password')
       db.session.add(admin)
       db.session.commit()
   ```

## Usage

### For Admin Users

1. Log in with admin credentials
2. Go to the **Admin** dashboard
3. **Create a Quiz**: Add title and description
4. **Add Questions**: Add multiple choice questions with options and correct answers
5. **Create an Event**: Schedule a quiz event with start/end times
6. **Create Teams**: Set up teams with maximum member limits
7. **Activate Event**: Toggle the event status to active when ready

### For Regular Users

1. Register an account
2. Browse active events on the home page
3. Join a team for an event
4. Start the quiz when the event is active
5. Answer questions and earn points for your team

## Adding New Languages

1. Extract translatable strings:
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   ```

2. Create a new translation catalog:
   ```bash
   pybabel init -i messages.pot -d app/translations -l <language_code>
   ```

3. Edit the translation file in `app/translations/<language_code>/LC_MESSAGES/messages.po`

4. Compile the translations:
   ```bash
   pybabel compile -d app/translations
   ```

## Database Models

- **User**: User accounts with admin flag
- **Quiz**: Quiz containers with title and description
- **Question**: Multiple choice questions with options
- **Event**: Scheduled quiz events with timeframes
- **Team**: Teams with member limits and scores
- **Answer**: User answers with scoring

## Configuration

Edit `config.py` to customize:
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: Database connection string
- `LANGUAGES`: Available languages
- `BABEL_DEFAULT_LOCALE`: Default language

## Security Notes

- Change the `SECRET_KEY` in production
- Use a production database (PostgreSQL recommended)
- Enable HTTPS in production
- Review and update dependencies regularly

## License

This project is provided as-is for educational purposes.
