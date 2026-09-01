"""Development seed data. Run with: python -m app.seed"""

from datetime import UTC, datetime, timedelta

from .database import SessionLocal, engine, Base
from .models import User, Subject, Note, Deadline, DeadlineType


def seed_database():
    """Seed the database with sample data for development."""

    # Create tables if they don't exist (for fresh databases)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if we already have data
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # Create demo user
        demo_user = User(
            email="demo@studyvault.com",
            hashed_password="not-a-real-password-yet",  # We'll fix this Day 3
            full_name="Demo Student",
        )
        db.add(demo_user)
        db.flush()  # Get the user ID

        # Create subjects
        calculus = Subject(
            user_id=demo_user.id,
            name="Calculus II",
            code="SMA 210",
            color="#3B82F6",
        )
        data_structures = Subject(
            user_id=demo_user.id,
            name="Data Structures",
            code="CSC 211",
            color="#10B981",
        )
        db.add_all([calculus, data_structures])
        db.flush()

        # Create notes
        notes = [
            Note(
                subject_id=calculus.id,
                title="Integration by Parts",
                content="""# Integration by Parts
The formula is: ∫u dv = uv - ∫v du

**Key steps:**
1. Choose u and dv
2. Differentiate u to get du
3. Integrate dv to get v
4. Apply the formula

*Common trick:* Use LIATE rule for choosing u.""",
            ),
            Note(
                subject_id=calculus.id,
                title="Partial Fractions",
                content="""# Partial Fractions
Break rational functions into simpler fractions.

**Cases:**
- Linear factors (A/(x-a))
- Repeated linear factors
- Irreducible quadratic factors""",
            ),
            Note(
                subject_id=data_structures.id,
                title="Binary Search Trees",
                content="""# BST Properties
- Left subtree < root
- Right subtree > root
- Average case: O(log n) for search/insert/delete

**Traversals:**
- Inorder: sorted order
- Preorder: root first
- Postorder: children first""",
            ),
            Note(
                subject_id=data_structures.id,
                title="AVL Trees",
                content="""# AVL Trees
Self-balancing BST.

**Balance factor:** height(left) - height(right)
- Must be between -1 and 1
- Rotations restore balance after insert/delete""",
            ),
        ]
        db.add_all(notes)

        # Create deadlines
        now = datetime.now(UTC)
        deadlines = [
            Deadline(
                subject_id=calculus.id,
                title="Calculus Midterm Exam",
                due_date=now + timedelta(days=14),
                type=DeadlineType.EXAM,
                is_completed=False,
            ),
            Deadline(
                subject_id=calculus.id,
                title="Assignment: Integration Techniques",
                due_date=now + timedelta(days=7),
                type=DeadlineType.ASSIGNMENT,
                is_completed=False,
            ),
            Deadline(
                subject_id=data_structures.id,
                title="Project: Implement AVL Tree",
                due_date=now + timedelta(days=21),
                type=DeadlineType.PROJECT,
                is_completed=False,
            ),
            Deadline(
                subject_id=data_structures.id,
                title="Quiz: BST Operations",
                due_date=now + timedelta(days=3),
                type=DeadlineType.ASSIGNMENT,
                is_completed=False,
            ),
            Deadline(
                subject_id=calculus.id,
                title="Homework 3",
                due_date=now - timedelta(days=2),
                type=DeadlineType.ASSIGNMENT,
                is_completed=True,
            ),
        ]
        db.add_all(deadlines)

        db.commit()
        print("Database seeded successfully with demo data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
