"""
Entrypoint WSGI generico. La mayoria de hostings compartidos con soporte
Python (PythonAnywhere, Hostinger "Python App", Passenger/cPanel, etc.)
buscan una variable llamada `application`.

Render y Railway normalmente usan directamente `gunicorn app:app`
(ver Procfile), por lo que este archivo es opcional para esas plataformas,
pero no estorba.
"""
from app import app as application

if __name__ == "__main__":
    application.run()
