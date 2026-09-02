from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Subject, User
from ..schemas import SubjectCreate, SubjectResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=list[SubjectResponse])
async def list_subjects(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get all subjects for the current user."""
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).all()
    return subjects


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new subject for the current user."""
    new_subject = Subject(
        user_id=current_user.id,
        name=subject_data.name,
        code=subject_data.code,
        color=subject_data.color,
    )

    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    return new_subject
