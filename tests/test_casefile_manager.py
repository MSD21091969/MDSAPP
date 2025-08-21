import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.CasefileManagement.models.casefile import Casefile
from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.core.models.ontology import Role

@pytest.fixture
def mock_db_manager():
    """Fixture for a mocked DatabaseManager."""
    mock = MagicMock(spec=DatabaseManager)
    mock.load_casefile = AsyncMock()
    mock.save_casefile = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_create_casefile(mock_db_manager):
    """
    Tests that a casefile can be created.
    """
    # Arrange
    casefile_manager = CasefileManager(db_manager=mock_db_manager)
    test_name = "Test Casefile"
    test_description = "A test casefile."
    test_user_id = "user-123"

    # Act
    new_casefile = await casefile_manager.create_casefile(
        name=test_name,
        description=test_description,
        user_id=test_user_id
    )

    # Assert
    assert new_casefile.name == test_name
    assert new_casefile.description == test_description
    assert new_casefile.owner_id == test_user_id
    assert new_casefile.acl[test_user_id] == Role.ADMIN
    mock_db_manager.save_casefile.assert_called_once_with(new_casefile)

@pytest.mark.asyncio
async def test_grant_access(mock_db_manager):
    """
    Tests that access can be granted to a user.
    """
    # Arrange
    casefile_manager = CasefileManager(db_manager=mock_db_manager)
    casefile_id = "case-123"
    admin_user_id = "admin-user"
    user_to_grant = "user-to-grant"
    role_to_grant = Role.WRITER

    # Create a mock casefile and set it as the return value for load_casefile
    mock_casefile = Casefile(
        id=casefile_id,
        name="Test Case",
        description="Test case for access grant",
        owner_id=admin_user_id,
        acl={admin_user_id: Role.ADMIN}
    )
    mock_db_manager.load_casefile.return_value = mock_casefile

    # Act
    updated_casefile = await casefile_manager.grant_access(
        casefile_id=casefile_id,
        user_id_to_grant=user_to_grant,
        role=role_to_grant,
        current_user_id=admin_user_id
    )

    # Assert
    mock_db_manager.load_casefile.assert_called_once_with(casefile_id)
    assert updated_casefile.acl[user_to_grant] == role_to_grant
    mock_db_manager.save_casefile.assert_called_once_with(updated_casefile)

@pytest.mark.asyncio
async def test_grant_access_permission_denied(mock_db_manager):
    """
    Tests that a non-admin user cannot grant access.
    """
    # Arrange
    casefile_manager = CasefileManager(db_manager=mock_db_manager)
    casefile_id = "case-123"
    owner_user_id = "owner-user"
    non_admin_user_id = "non-admin-user"
    user_to_grant = "user-to-grant"
    role_to_grant = Role.WRITER

    mock_casefile = Casefile(
        id=casefile_id,
        name="Test Case",
        description="Test case for access grant",
        owner_id=owner_user_id,
        acl={owner_user_id: Role.ADMIN, non_admin_user_id: Role.READER}
    )
    mock_db_manager.load_casefile.return_value = mock_casefile

    # Act & Assert
    with pytest.raises(PermissionError):
        await casefile_manager.grant_access(
            casefile_id=casefile_id,
            user_id_to_grant=user_to_grant,
            role=role_to_grant,
            current_user_id=non_admin_user_id
        )
    mock_db_manager.save_casefile.assert_not_called()