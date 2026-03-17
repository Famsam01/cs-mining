from app import create_app

app = create_app()
```

Then update your Render start command to:
```
gunicorn wsgi: app
