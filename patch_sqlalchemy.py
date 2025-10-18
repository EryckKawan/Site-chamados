#!/usr/bin/env python
"""
Script para aplicar um patch temporário no SQLAlchemy para compatibilidade com Python 3.13
"""
import os
import sys
import site
import re
from pathlib import Path

def find_sqlalchemy_langhelpers():
    """Encontra o arquivo langhelpers.py do SQLAlchemy"""
    # Tenta encontrar em site-packages
    for path in site.getsitepackages():
        langhelpers_path = Path(path) / "sqlalchemy" / "util" / "langhelpers.py"
        if langhelpers_path.exists():
            return langhelpers_path
    
    # Tenta encontrar em venv
    venv_path = Path(".venv")
    if venv_path.exists():
        lib_path = venv_path / "Lib" / "site-packages" / "sqlalchemy" / "util" / "langhelpers.py"
        if lib_path.exists():
            return lib_path
    
    return None

def apply_patch(file_path):
    """Aplica o patch no arquivo langhelpers.py"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup do arquivo original
    backup_path = str(file_path) + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backup criado em: {backup_path}")
    
    # Padrão para encontrar o método __init_subclass__ na classe TypingOnly
    pattern = r'def __init_subclass__\(cls, \*\*kw\):(.*?)if cls\.__module__ != "typing":(.*?)for name, obj in list\(cls\.__dict__\.items\(\)\):(.*?)if name not in \((.*?)\):(.*?)raise AssertionError'
    
    # Substitui os atributos permitidos para incluir __static_attributes__ e __firstlineno__
    replacement = r'def __init_subclass__(cls, **kw):\1if cls.__module__ != "typing":\2for name, obj in list(cls.__dict__.items()):\3if name not in (\4, "__static_attributes__", "__firstlineno__"):\5raise AssertionError'
    
    # Aplica a substituição
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Verifica se a substituição foi feita
    if new_content == content:
        print("Não foi possível aplicar o patch. O padrão não foi encontrado.")
        return False
    
    # Escreve o conteúdo modificado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("Procurando o arquivo langhelpers.py do SQLAlchemy...")
    langhelpers_path = find_sqlalchemy_langhelpers()
    
    if not langhelpers_path:
        print("Não foi possível encontrar o arquivo langhelpers.py do SQLAlchemy.")
        return 1
    
    print(f"Arquivo encontrado: {langhelpers_path}")
    
    print("Aplicando patch...")
    if apply_patch(langhelpers_path):
        print("Patch aplicado com sucesso!")
        print("\nAgora você pode executar o aplicativo com Python 3.13.")
        print("\nAtenção: Este é um patch temporário. Recomendamos atualizar para uma versão")
        print("do SQLAlchemy compatível com Python 3.13 assim que disponível.")
    else:
        print("Falha ao aplicar o patch.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())