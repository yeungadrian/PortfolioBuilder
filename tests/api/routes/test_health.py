import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_healthcheck(async_client: AsyncClient) -> None:
    """Test healthcheck endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
