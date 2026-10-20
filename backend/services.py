from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def salvar(db, registro):
    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro
    except IntegrityError as exc:
        db.rollback()
        codigo = getattr(exc.orig, "pgcode", None)
        if codigo == "23503":
            raise HTTPException(404, "Cidade não encontrada") from exc
        if codigo == "23505":
            raise HTTPException(409, "Registro duplicado") from exc
        raise
