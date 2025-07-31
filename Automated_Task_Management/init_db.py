from app import create_app, db
from app.models import User, Task

app = create_app()

# This will create the tables based on your models
with app.app_context():
    db.create_all()
    print("Database tables created!")
