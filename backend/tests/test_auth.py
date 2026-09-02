
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_application
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import User
from app.security import hash_password

# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def app(test_db):
    app = create_application()
    
    # Override dependency to use test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.mark.asyncio
async def test_register_user(app):
    """Test that we can register a new user."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
                "full_name": "Test User",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@example.com"
        assert "hashed_password" not in data["user"]  # Never expose password hash

@pytest.mark.asyncio
async def test_login_user(app, test_db):
    """Test that we can login with correct credentials."""
    # Create a user directly in database
    user = User(
        email="login@example.com",
        hashed_password=hash_password("TestPass123"),
        full_name="Login Test",
    )
    test_db.add(user)
    test_db.commit()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": "TestPass123",
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

@pytest.mark.asyncio
async def test_login_wrong_password(app, test_db):
    """Test that login fails with wrong password."""
    user = User(
        email="wrong@example.com",
        hashed_password=hash_password("CorrectPass123"),
        full_name="Wrong Password Test",
    )
    test_db.add(user)
    test_db.commit()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "wrong@example.com",
                "password": "WrongPass123",
            }
        )
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user(app, test_db):
    """Test that we can get current user info with valid token."""
    # Create and login a user
    user = User(
        email="me@example.com",
        hashed_password=hash_password("TestPass123"),
        full_name="Me Test",
    )
    test_db.add(user)
    test_db.commit()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "me@example.com",
                "password": "TestPass123",
            }
        )
        token = login_response.json()["access_token"]
        
        # Use token to get user info
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "me@example.com"

@pytest.mark.asyncio
async def test_unauthorized_access(app):
    """Test that protected endpoint rejects missing token."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
