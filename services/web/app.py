"""App entry point."""
from project import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False, host='0.0.0.0')
