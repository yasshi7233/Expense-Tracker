# Root-level entry point exposing the Flask application instance
# Ensures backwards compatibility with gunicorn app:app, procfile, and direct scripts
import os
from app import create_app
from app.extensions import db
from app.models import User, Transaction

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Transaction': Transaction
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
