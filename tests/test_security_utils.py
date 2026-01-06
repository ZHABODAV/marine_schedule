import pytest
import os
from pathlib import Path
from modules.security_utils import SecurityUtils

class TestSecurityUtils:
    
    def test_validate_path_valid(self, tmp_path):
        # Create a file in tmp_path
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        # Validate absolute path
        validated = SecurityUtils.validate_path(test_file, tmp_path)
        assert validated == test_file.resolve()
        
        # Validate relative path
        validated = SecurityUtils.validate_path("test.txt", tmp_path)
        assert validated == test_file.resolve()

    def test_validate_path_traversal(self, tmp_path):
        # Try to access parent directory
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            SecurityUtils.validate_path("../outside.txt", tmp_path)
            
        # Try absolute path outside base
        outside_file = tmp_path.parent / "outside.txt"
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            SecurityUtils.validate_path(outside_file, tmp_path)

    def test_validate_path_extensions(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        # Valid extension
        SecurityUtils.validate_path(test_file, tmp_path, allowed_extensions=['.txt'])
        
        # Invalid extension
        with pytest.raises(ValueError, match="Invalid file extension"):
            SecurityUtils.validate_path(test_file, tmp_path, allowed_extensions=['.json'])

    def test_validate_path_subdirectories(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "test.txt"
        test_file.touch()
        
        # Allowed subdirectories
        SecurityUtils.validate_path(test_file, tmp_path, allow_subdirectories=True)
        
        # Disallowed subdirectories
        with pytest.raises(ValueError, match="Subdirectories not allowed"):
            SecurityUtils.validate_path(test_file, tmp_path, allow_subdirectories=False)

    def test_create_backup(self, tmp_path):
        test_file = tmp_path / "data.json"
        test_file.write_text('{"key": "value"}')
        
        # Create backup
        backup_path = SecurityUtils.create_backup(test_file)
        assert backup_path is not None
        assert os.path.exists(backup_path)
        
        # Verify content
        assert Path(backup_path).read_text() == '{"key": "value"}'
        
        # Verify backup location (default .backups)
        assert Path(backup_path).parent.name == ".backups"

    def test_safe_write_file(self, tmp_path):
        test_file = tmp_path / "config.json"
        
        # Initial write
        SecurityUtils.safe_write_file(test_file, '{"version": 1}')
        assert test_file.read_text() == '{"version": 1}'
        
        # Overwrite with backup
        SecurityUtils.safe_write_file(test_file, '{"version": 2}')
        assert test_file.read_text() == '{"version": 2}'
        
        # Check if backup exists
        backups_dir = tmp_path / ".backups"
        assert backups_dir.exists()
        assert len(list(backups_dir.glob("config_*.json"))) == 1
