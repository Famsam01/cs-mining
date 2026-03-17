from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

Then your Render start command should be:
```
gunicorn wsgi: app
