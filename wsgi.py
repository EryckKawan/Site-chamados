"""
WSGI Entry Point para servidores de produção
"""
from app import app

if __name__ == "__main__":
    app.run()

