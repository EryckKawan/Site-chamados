# Solução para o Erro do SQLAlchemy com Python 3.13

## Problema

Ao executar o aplicativo com Python 3.13, ocorre o seguinte erro:

```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly but has additional attributes {'__static_attributes__', '__firstlineno__'}.
```

Este erro ocorre devido a mudanças no sistema de tipos do Python 3.13 que são incompatíveis com a versão atual do SQLAlchemy instalada.

## Solução 1: Downgrade do Python

A solução mais simples é usar uma versão anterior do Python que seja compatível com o SQLAlchemy:

1. Instale o Python 3.11 ou 3.12
2. Crie um novo ambiente virtual com a versão compatível
3. Instale as dependências novamente

```
python3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Solução 2: Atualizar o SQLAlchemy

Se você precisa usar o Python 3.13, atualize o SQLAlchemy para a versão mais recente:

1. Atualize o SQLAlchemy:
```
pip install --upgrade sqlalchemy
```

2. Atualize o arquivo requirements.txt:
```
sqlalchemy>=2.0.27
```

## Solução 3: Patch temporário (não recomendado para produção)

Se as soluções acima não funcionarem, você pode aplicar um patch temporário:

1. Localize o arquivo `langhelpers.py` na instalação do SQLAlchemy:
```
C:\Users\[seu-usuario]\AppData\Local\Programs\Python\Python313\Lib\site-packages\sqlalchemy\util\langhelpers.py
```

2. Edite o método `__init_subclass__` na classe `TypingOnly` para ignorar os atributos problemáticos:

```python
def __init_subclass__(cls, **kw):
    if cls.__module__ != "typing":
        for name, obj in list(cls.__dict__.items()):
            if name not in ("__module__", "__dict__", "__weakref__", 
                           "__doc__", "__annotations__", "__qualname__",
                           "__static_attributes__", "__firstlineno__"):
                raise AssertionError(
                    f"Class {cls!r} directly inherits TypingOnly but "
                    f"has additional attributes {set(cls.__dict__) - "
                    f"{'__module__', '__dict__', '__weakref__', '__doc__', "
                    f"'__annotations__', '__qualname__', '__static_attributes__', '__firstlineno__'}}."
                )
```

## Recomendação

A solução mais segura e recomendada é a **Solução 1** (usar Python 3.11 ou 3.12) ou a **Solução 2** (atualizar o SQLAlchemy), pois o patch manual pode causar outros problemas e será perdido se o pacote for reinstalado.