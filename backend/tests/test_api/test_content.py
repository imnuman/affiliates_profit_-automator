"""
Tests for content endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_content(client: AsyncClient, auth_headers, test_user):
    """Test creating content"""
    response = await client.post(
        "/api/v1/content",
        headers=auth_headers,
        json={
            "type": "blog_post",
            "title": "Test Blog Post",
            "body": "This is a test blog post content.",
            "status": "draft"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Blog Post"
    assert data["type"] == "blog_post"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_list_content(client: AsyncClient, auth_headers, test_user, db_session: AsyncSession):
    """Test listing user's content"""
    # Create some content first
    from app.models.content import Content

    content1 = Content(
        user_id=test_user.id,
        type="blog_post",
        title="Post 1",
        body="Content 1",
        status="draft"
    )
    content2 = Content(
        user_id=test_user.id,
        type="email",
        title="Email 1",
        body="Email content",
        status="published"
    )
    db_session.add_all([content1, content2])
    await db_session.commit()

    # List content
    response = await client.get(
        "/api/v1/content",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_content_by_id(client: AsyncClient, auth_headers, test_user, db_session: AsyncSession):
    """Test getting specific content"""
    from app.models.content import Content

    content = Content(
        user_id=test_user.id,
        type="blog_post",
        title="Test Post",
        body="Test content",
        status="draft"
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)

    response = await client.get(
        f"/api/v1/content/{content.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(content.id)
    assert data["title"] == "Test Post"


@pytest.mark.asyncio
async def test_update_content(client: AsyncClient, auth_headers, test_user, db_session: AsyncSession):
    """Test updating content"""
    from app.models.content import Content

    content = Content(
        user_id=test_user.id,
        type="blog_post",
        title="Original Title",
        body="Original content",
        status="draft"
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)

    response = await client.put(
        f"/api/v1/content/{content.id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "body": "Updated content",
            "status": "published"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "published"


@pytest.mark.asyncio
async def test_delete_content(client: AsyncClient, auth_headers, test_user, db_session: AsyncSession):
    """Test deleting content"""
    from app.models.content import Content

    content = Content(
        user_id=test_user.id,
        type="blog_post",
        title="To Delete",
        body="Content to delete",
        status="draft"
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)

    response = await client.delete(
        f"/api/v1/content/{content.id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/content/{content.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_access_other_users_content(client: AsyncClient, auth_headers, db_session: AsyncSession):
    """Test that users cannot access other users' content"""
    from app.models.user import User
    from app.models.content import Content
    from app.core.security import hash_password

    # Create another user
    other_user = User(
        email="other@example.com",
        password_hash=hash_password("OtherPassword123!"),
        full_name="Other User",
        tier="starter",
        status="active"
    )
    db_session.add(other_user)
    await db_session.flush()

    # Create content for other user
    other_content = Content(
        user_id=other_user.id,
        type="blog_post",
        title="Other's Post",
        body="Other's content",
        status="draft"
    )
    db_session.add(other_content)
    await db_session.commit()
    await db_session.refresh(other_content)

    # Try to access it with test_user's credentials
    response = await client.get(
        f"/api/v1/content/{other_content.id}",
        headers=auth_headers
    )

    assert response.status_code == 404  # Or 403 depending on implementation
