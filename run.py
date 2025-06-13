import os
from dotenv import load_dotenv

from flask_migrate import Migrate
from app import init_app
from app.models import db  # Make sure this exists and imports db

load_dotenv()

# Create Flask app using factory
app = init_app()

# Attach Flask-Migrate
migrate = Migrate(app, db)

# Run the app if executed directly
if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 8080)))