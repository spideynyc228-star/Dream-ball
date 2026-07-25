# Deployment

For production, set `DEBUG=False`, configure a unique `SECRET_KEY`, set `ALLOWED_HOSTS`, and use PostgreSQL. Run migrations before serving traffic.

Serve static files through the selected deployment platform and use a persistent media storage service for uploaded student photos. Restrict Django Admin to authorised school staff and enable HTTPS.
