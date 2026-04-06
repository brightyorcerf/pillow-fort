import pytest
from sqlalchemy import text
from auth_domain.infrastructure.persistence.database import (
    init_engine,
    get_session_factory,
    shutdown_engine
)
from auth_domain.config.settings import Settings

pytestmark = pytest.mark.asyncio

async def test_db_session_connectivity():
    """
    Tests that we can initialize the database engine,
    create a session factory, and execute a simple query 
    against the active database.
    """
    print("1. Fetching config from .env...")
    settings = Settings()
    print(f" -> Found database URL: {settings.database_url[:20]}...")
    
    print("2. Initializing the DB engine...")
    init_engine(settings.database_url)
    
    try:
        print("3. Getting session factory...")
        session_factory = get_session_factory()
        
        print("4. Creating session and checking connection...")
        async with session_factory() as session:
            async with session.begin():
                result = await session.execute(text("SELECT 1;"))
                row = result.scalar()
                
                assert row == 1, f"Database responded with unexpected value: {row}"
                print("✅ CONNECTION SUCCESSFUL! (Received '1' from database)")
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")
        raise
    finally:
        print("5. Shutting down engine...")
        await shutdown_engine()

if __name__ == "__main__":
    import asyncio
    print("Starting manual test run...")
    asyncio.run(test_db_session_connectivity())
