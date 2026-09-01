import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Note, Subject, User

# Create an in-memory SQLite database for testing
# This is fast and doesn't require a running PostgreSQL server
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_db():
    """Create a test database with tables."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


def test_create_user(test_db):
    """Test that we can create a user."""
    user = User(
        email="test@example.com",
        hashed_password="fakehash",
        full_name="Test User",
    )
    test_db.add(user)
    test_db.commit()

    # Query it back
    saved_user = test_db.query(User).filter(
        User.email == "test@example.com"
    ).first()
    assert saved_user is not None
    assert saved_user.full_name == "Test User"
    assert saved_user.id is not None


def test_user_subject_relationship(test_db):
    """Test the relationship between users and subjects."""
    user = User(
        email="reltest@example.com",
        hashed_password="fakehash",
        full_name="Relationship Test",
    )
    test_db.add(user)
    test_db.flush()

    subject = Subject(
        user_id=user.id,
        name="Physics",
        code="PHY 101",
    )
    test_db.add(subject)
    test_db.commit()

    # Access through relationship
    assert len(user.subjects) == 1
    assert user.subjects[0].name == "Physics"
    assert subject.user.email == "reltest@example.com"


def test_cascade_delete(test_db):
    """Test that deleting a user cascades to subjects."""
    user = User(
        email="cascade@example.com",
        hashed_password="fakehash",
        full_name="Cascade Test",
    )
    test_db.add(user)
    test_db.flush()

    subject = Subject(
        user_id=user.id,
        name="Chemistry",
        code="CHE 101",
    )
    test_db.add(subject)
    test_db.commit()

    # Delete the user
    test_db.delete(user)
    test_db.commit()

    # Subject should be gone too
    subjects = test_db.query(Subject).all()
    assert len(subjects) == 0


def test_note_updated_at(test_db):
    """Test that updated_at changes on update."""
    user = User(
        email="timestamp@example.com",
        hashed_password="fakehash",
        full_name="Timestamp Test",
    )
    test_db.add(user)
    test_db.flush()

    subject = Subject(
        user_id=user.id,
        name="Biology",
    )
    test_db.add(subject)
    test_db.flush()

    note = Note(
        subject_id=subject.id,
        title="Cell Division",
        content="Original content",
    )
    test_db.add(note)
    test_db.commit()

    original_updated_at = note.updated_at

    # Simulate time passing

    time.sleep(1)

    note.content = "Updated content"
    test_db.commit()
    test_db.refresh(note)

    assert note.updated_at != original_updated_at


def test_unique_email_constraint(test_db):
    """Test that duplicate emails are rejected."""
    user1 = User(
        email="unique@example.com",
        hashed_password="hash1",
        full_name="First User",
    )
    test_db.add(user1)
    test_db.commit()

    user2 = User(
        email="unique@example.com",  # Same email
        hashed_password="hash2",
        full_name="Second User",
    )
    test_db.add(user2)

    with pytest.raises(Exception):
        test_db.commit()
    test_db.rollback()
