from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi_classification.models import case as case_model
from fastapi_classification.schemas import case as case_schema
from fastapi_classification.core.database import get_db
from fastapi_classification.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=case_schema.CaseOut)
def create_case(
    case: case_schema.CaseCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_case = case_model.Case(**case.model_dump(), created_by=user.id)
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@router.get("/", response_model=List[case_schema.CaseOut])
def list_cases(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(case_model.Case).offset(skip).limit(limit).all()

@router.get("/{case_id}", response_model=case_schema.CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    db_case = db.query(case_model.Case).filter(case_model.Case.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case

@router.put("/{case_id}", response_model=case_schema.CaseOut)
def update_case(case_id: int, case: case_schema.CaseUpdate, db: Session = Depends(get_db)):
    db_case = db.query(case_model.Case).filter(case_model.Case.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    for key, value in case.model_dump(exclude_unset=True).items():
        setattr(db_case, key, value)
    db.commit()
    db.refresh(db_case)
    return db_case