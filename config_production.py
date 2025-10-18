"""
Configuração para Ambiente de Produção
"""
import os
import secrets

class Config:
    """Configurações base"""
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Banco de Dados
    # Para SQLite (desenvolvimento/pequeno)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chamados_ti.db'
    
    # Para PostgreSQL (produção - descomente e configure)
    # SQLALCHEMY_DATABASE_URI = 'postgresql://usuario:senha@localhost/chamados_ti'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    DEBUG = False  # NUNCA True em produção!
    TESTING = False
    
    # Sessão
    SESSION_COOKIE_SECURE = True  # Apenas HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload (se implementar anexos)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chamados_ti.db'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    # Usar PostgreSQL em produção
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chamados_ti.db'

# Selecionar configuração baseado no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

