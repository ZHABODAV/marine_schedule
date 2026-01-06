import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Union

logger = logging.getLogger(__name__)

class SecurityUtils:
    """
    Security utilities for path validation and file operations.
    """

    @staticmethod
    def validate_path(
        path: Union[str, Path], 
        base_dir: Union[str, Path], 
        allowed_extensions: Optional[List[str]] = None,
        allow_subdirectories: bool = True
    ) -> Path:
        """
        Validate that a path is safe and within the expected base directory.
        
        Args:
            path: The path to validate (relative or absolute)
            base_dir: The directory the path must be contained within
            allowed_extensions: List of allowed file extensions (e.g., ['.json', '.csv'])
            allow_subdirectories: Whether to allow paths in subdirectories of base_dir
            
        Returns:
            Path: The resolved, absolute path
            
        Raises:
            ValueError: If the path is invalid or unsafe
        """
        try:
            # Convert to Path objects
            if isinstance(path, str):
                path = Path(path)
            if isinstance(base_dir, str):
                base_dir = Path(base_dir)
            
            # Resolve base directory to absolute path
            base_dir = base_dir.resolve()
            
            # Handle absolute vs relative input paths
            if path.is_absolute():
                # If absolute, check if it starts with base_dir
                # We use resolve() to handle symlinks and .. components
                resolved_path = path.resolve()
            else:
                # If relative, join with base_dir and resolve
                resolved_path = (base_dir / path).resolve()
            
            # Check if the resolved path is within the base directory
            # is_relative_to was added in Python 3.9. For compatibility, we can use string comparison
            try:
                resolved_path.relative_to(base_dir)
            except ValueError:
                raise ValueError(f"Path traversal attempt detected: {path} is outside {base_dir}")
            
            # If subdirectories are not allowed, check that the parent is exactly the base_dir
            if not allow_subdirectories and resolved_path.parent != base_dir:
                raise ValueError(f"Subdirectories not allowed: {path}")
            
            # Check extensions if provided
            if allowed_extensions:
                # Normalize extensions to lowercase
                allowed = [ext.lower() for ext in allowed_extensions]
                if resolved_path.suffix.lower() not in allowed:
                    raise ValueError(f"Invalid file extension: {resolved_path.suffix}. Allowed: {allowed}")
            
            return resolved_path
            
        except Exception as e:
            # Re-raise ValueErrors, wrap others
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid path: {e}")

    @staticmethod
    def create_backup(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None, max_backups: int = 5) -> Optional[str]:
        """
        Create a timestamped backup of a file.
        
        Args:
            file_path: Path to the file to back up
            backup_dir: Directory to store backups (defaults to file's directory or .backups subdir)
            max_backups: Maximum number of backups to keep for this file
            
        Returns:
            str: Path to the backup file, or None if source doesn't exist
        """
        try:
            source = Path(file_path).resolve()
            if not source.exists():
                return None
            
            # Determine backup directory
            if backup_dir:
                target_dir = Path(backup_dir).resolve()
            else:
                # Default to a .backups folder in the same directory
                target_dir = source.parent / ".backups"
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.stem}_{timestamp}{source.suffix}"
            backup_path = target_dir / backup_name
            
            # Perform copy
            shutil.copy2(source, backup_path)
            logger.info(f"Created backup of {source.name} at {backup_path}")
            
            # Cleanup old backups
            SecurityUtils._cleanup_old_backups(source, target_dir, max_backups)
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed for {file_path}: {e}")
            # We don't raise here to avoid breaking the main flow, but we log it
            return None

    @staticmethod
    def _cleanup_old_backups(source_file: Path, backup_dir: Path, max_backups: int):
        """Helper to remove old backups."""
        try:
            # Find all backups for this file
            # Pattern: filename_YYYYMMDD_HHMMSS.ext
            glob_pattern = f"{source_file.stem}_*{source_file.suffix}"
            backups = list(backup_dir.glob(glob_pattern))
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remove excess
            if len(backups) > max_backups:
                for old_backup in backups[max_backups:]:
                    try:
                        old_backup.unlink()
                        logger.debug(f"Removed old backup: {old_backup.name}")
                    except Exception as e:
                        logger.warning(f"Failed to remove old backup {old_backup.name}: {e}")
                        
        except Exception as e:
            logger.warning(f"Error cleaning up backups: {e}")

    @staticmethod
    def safe_write_file(file_path: Union[str, Path], content: str, mode: str = 'w', encoding: str = 'utf-8') -> bool:
        """
        Safely write to a file with backup and atomic write (if possible).
        
        Args:
            file_path: Path to write to
            content: Content to write
            mode: Write mode ('w' or 'a')
            encoding: File encoding
            
        Returns:
            bool: True if successful
        """
        try:
            path = Path(file_path).resolve()
            
            # Create backup if file exists and we are overwriting (mode 'w')
            if path.exists() and 'w' in mode:
                SecurityUtils.create_backup(path)
            
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # For atomic write, we write to a temp file then rename
            # Only applicable for 'w' mode
            if 'w' in mode:
                temp_path = path.with_suffix(f"{path.suffix}.tmp")
                with open(temp_path, mode, encoding=encoding) as f:
                    f.write(content)
                
                # Atomic replace
                temp_path.replace(path)
            else:
                # Append mode just writes directly
                with open(path, mode, encoding=encoding) as f:
                    f.write(content)
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise
