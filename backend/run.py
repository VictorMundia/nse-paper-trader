# This imports the app factory function that builds and configures our Flask application.
from app import create_app

# This creates one configured Flask app instance by calling our factory function.
app = create_app()

# This checks whether this file is being run directly from the terminal.
if __name__ == "__main__":
    # This starts the Flask development server on localhost and enables debug mode for development.
    app.run(host="127.0.0.1", port=5000, debug=True)