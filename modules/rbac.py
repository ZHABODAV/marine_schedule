"""modules.rbac

Role-Based Access Control (RBAC) Module.

Security notes:
- Passwords are hashed using `bcrypt` when available.
- Legacy SHA-256 password hashes are supported for backward compatibility and
  will be upgraded to the preferred scheme on successful login.
- Session tokens are random and have an expiry (enforced).
- A small in-memory login rate limiter mitigates brute-force attempts.

This is a lightweight RBAC implementation intended for local deployments. For a
production system, consider:
- persistent session store
- centralized audit logging
- IP-based rate limiting at the edge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import uuid

try:
    import bcrypt  # type: ignore
except Exception:  # noqa: BLE001
    bcrypt = None


class Permission(Enum):
    """System permissions."""

    # Vessel permissions
    VIEW_VESSELS = "view_vessels"
    CREATE_VESSELS = "create_vessels"
    EDIT_VESSELS = "edit_vessels"
    DELETE_VESSELS = "delete_vessels"

    # Voyage permissions
    VIEW_VOYAGES = "view_voyages"
    CREATE_VOYAGES = "create_voyages"
    EDIT_VOYAGES = "edit_voyages"
    DELETE_VOYAGES = "delete_voyages"
    APPROVE_VOYAGES = "approve_voyages"

    # Schedule permissions
    VIEW_SCHEDULES = "view_schedules"
    CREATE_SCHEDULES = "create_schedules"
    EDIT_SCHEDULES = "edit_schedules"
    DELETE_SCHEDULES = "delete_schedules"
    PUBLISH_SCHEDULES = "publish_schedules"

    # Financial permissions
    VIEW_FINANCIALS = "view_financials"
    EDIT_FINANCIALS = "edit_financials"
    APPROVE_BUDGETS = "approve_budgets"

    # Report permissions
    VIEW_REPORTS = "view_reports"
    EXPORT_REPORTS = "export_reports"

    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    SYSTEM_SETTINGS = "system_settings"


class UserRole(Enum):
    """Predefined user roles."""

    ADMIN = "admin"
    OPERATIONS_MANAGER = "operations_manager"
    SCHEDULER = "scheduler"
    FINANCE_MANAGER = "finance_manager"
    VIEWER = "viewer"
    PORT_AGENT = "port_agent"


@dataclass
class Role:
    """User role with permissions."""

    role_id: str
    role_name: str
    description: str
    permissions: Set[Permission]
    created_at: datetime = field(default_factory=datetime.now)

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a specific permission."""

        return permission in self.permissions

    def to_dict(self) -> Dict:
        """Convert role to dictionary."""

        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "description": self.description,
            "permissions": [p.value for p in self.permissions],
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class User:
    """System user."""

    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[Role]
    full_name: str
    department: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    session_token: Optional[str] = None
    token_expires: Optional[datetime] = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission through any role."""

        return any(role.has_permission(permission) for role in self.roles)

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""

        return any(role.role_name == role_name for role in self.roles)

    def get_permissions(self) -> Set[Permission]:
        """Get all permissions from all roles."""

        permissions: Set[Permission] = set()
        for role in self.roles:
            permissions.update(role.permissions)
        return permissions

    def to_dict(self, include_sensitive: bool = False) -> Dict:
        """Convert user to dictionary."""

        data: Dict[str, object] = {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "department": self.department,
            "is_active": self.is_active,
            "roles": [role.role_name for role in self.roles],
            "permissions": [p.value for p in self.get_permissions()],
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data["password_hash"] = self.password_hash
            data["session_token"] = self.session_token
            data["token_expires"] = self.token_expires.isoformat() if self.token_expires else None

        return data


@dataclass
class AuditLog:
    """Audit log entry."""

    log_id: str
    user_id: str
    username: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: Optional[str] = None
    details: Optional[Dict] = None
    success: bool = True

    def to_dict(self) -> Dict:
        """Convert audit log to dictionary."""

        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "details": self.details,
            "success": self.success,
        }


class RBACManager:
    """Manages role-based access control."""

    def __init__(self, data_dir: str = "data/rbac"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Thread-safety (Flask can be multi-threaded)
        self._lock = threading.RLock()

        # Security knobs (env-overridable)
        self._token_ttl = timedelta(hours=float(os.getenv("RBAC_TOKEN_TTL_HOURS", "8")))
        self._max_failed_logins = int(os.getenv("RBAC_MAX_FAILED_LOGINS", "10"))
        self._failed_login_window = timedelta(
            seconds=int(os.getenv("RBAC_FAILED_LOGIN_WINDOW_SEC", str(15 * 60)))
        )

        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.audit_logs: List[AuditLog] = []

        # username -> [(timestamp, ip)]
        self._failed_logins: Dict[str, List[Tuple[datetime, str]]] = {}

        self._initialize_default_roles()
        self._load_users()

    # =====================
    # Roles
    # =====================

    def _initialize_default_roles(self):
        """Initialize default system roles."""

        # Admin role - full permissions
        self.roles[UserRole.ADMIN.value] = Role(
            role_id=UserRole.ADMIN.value,
            role_name="Administrator",
            description="Full system access",
            permissions=set(Permission),
        )

        # Operations Manager - manage operations
        self.roles[UserRole.OPERATIONS_MANAGER.value] = Role(
            role_id=UserRole.OPERATIONS_MANAGER.value,
            role_name="Operations Manager",
            description="Manage vessel operations and schedules",
            permissions={
                Permission.VIEW_VESSELS,
                Permission.EDIT_VESSELS,
                Permission.VIEW_VOYAGES,
                Permission.CREATE_VOYAGES,
                Permission.EDIT_VOYAGES,
                Permission.APPROVE_VOYAGES,
                Permission.VIEW_SCHEDULES,
                Permission.CREATE_SCHEDULES,
                Permission.EDIT_SCHEDULES,
                Permission.DELETE_SCHEDULES,
                Permission.PUBLISH_SCHEDULES,
                Permission.VIEW_REPORTS,
                Permission.EXPORT_REPORTS,
            },
        )

        # Scheduler - schedule voyages
        self.roles[UserRole.SCHEDULER.value] = Role(
            role_id=UserRole.SCHEDULER.value,
            role_name="Scheduler",
            description="Create and edit schedules",
            permissions={
                Permission.VIEW_VESSELS,
                Permission.VIEW_VOYAGES,
                Permission.CREATE_VOYAGES,
                Permission.EDIT_VOYAGES,
                Permission.VIEW_SCHEDULES,
                Permission.CREATE_SCHEDULES,
                Permission.EDIT_SCHEDULES,
                Permission.VIEW_REPORTS,
            },
        )

        # Finance Manager - financial oversight
        self.roles[UserRole.FINANCE_MANAGER.value] = Role(
            role_id=UserRole.FINANCE_MANAGER.value,
            role_name="Finance Manager",
            description="Manage financial aspects",
            permissions={
                Permission.VIEW_VESSELS,
                Permission.VIEW_VOYAGES,
                Permission.VIEW_SCHEDULES,
                Permission.VIEW_FINANCIALS,
                Permission.EDIT_FINANCIALS,
                Permission.APPROVE_BUDGETS,
                Permission.VIEW_REPORTS,
                Permission.EXPORT_REPORTS,
            },
        )

        # Viewer - read-only access
        self.roles[UserRole.VIEWER.value] = Role(
            role_id=UserRole.VIEWER.value,
            role_name="Viewer",
            description="Read-only access",
            permissions={
                Permission.VIEW_VESSELS,
                Permission.VIEW_VOYAGES,
                Permission.VIEW_SCHEDULES,
                Permission.VIEW_REPORTS,
            },
        )

        # Port Agent - port-specific operations
        self.roles[UserRole.PORT_AGENT.value] = Role(
            role_id=UserRole.PORT_AGENT.value,
            role_name="Port Agent",
            description="Port operations access",
            permissions={
                Permission.VIEW_VESSELS,
                Permission.VIEW_VOYAGES,
                Permission.VIEW_SCHEDULES,
                Permission.VIEW_REPORTS,
            },
        )

    # =====================
    # Persistence
    # =====================

    def _load_users(self):
        """Load users from storage."""

        users_file = self.data_dir / "users.json"
        if not users_file.exists():
            return

        try:
            with open(users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
        except Exception:  # noqa: BLE001
            return

        for user_data in users_data or []:
            role_ids = user_data.get("role_ids", [])
            roles = [self.roles[role_id] for role_id in role_ids if role_id in self.roles]

            user = User(
                user_id=str(user_data.get("user_id", str(uuid.uuid4()))),
                username=str(user_data.get("username", "")),
                email=str(user_data.get("email", "")),
                password_hash=str(user_data.get("password_hash", "")),
                roles=roles,
                full_name=str(user_data.get("full_name", "")),
                department=user_data.get("department"),
                is_active=bool(user_data.get("is_active", True)),
            )
            if user.username:
                self.users[user.username] = user

    def _save_users(self):
        """Save users to storage."""

        users_file = self.data_dir / "users.json"
        users_data = []
        for user in self.users.values():
            users_data.append(
                {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "full_name": user.full_name,
                    "department": user.department,
                    "is_active": user.is_active,
                    "role_ids": [role.role_id for role in user.roles],
                }
            )

        tmp_path = users_file.with_suffix(users_file.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, users_file)

    # =====================
    # Password hashing
    # =====================

    @staticmethod
    def _hash_password_pbkdf2(password: str) -> str:
        """Hash password with PBKDF2-HMAC-SHA256.

        Used as a fallback when `bcrypt` is unavailable.

        Format:
            pbkdf2_sha256$<iterations>$<salt_b64>$<dk_b64>
        """

        iterations = int(os.getenv("RBAC_PBKDF2_ITERATIONS", "200000"))
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return "pbkdf2_sha256${}${}${}".format(
            iterations,
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(dk).decode("ascii"),
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using a salted scheme.

        Prefer `bcrypt` when installed. Fall back to PBKDF2-HMAC.
        """

        if bcrypt is not None:
            rounds = int(os.getenv("RBAC_BCRYPT_ROUNDS", "12"))
            salt = bcrypt.gensalt(rounds=rounds)
            pw_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
            return pw_hash.decode("utf-8")

        return RBACManager._hash_password_pbkdf2(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a stored hash.

        Supports:
        - bcrypt ($2a$/$2b$/$2y$)
        - pbkdf2_sha256$...
        - legacy sha256 hex (64 chars)
        """

        if not password_hash:
            return False

        try:
            if password_hash.startswith("$2"):
                if bcrypt is None:
                    return False
                return bool(
                    bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
                )

            if password_hash.startswith("pbkdf2_sha256$"):
                _, iterations_str, salt_b64, dk_b64 = password_hash.split("$", 3)
                iterations = int(iterations_str)
                salt = base64.b64decode(salt_b64.encode("ascii"))
                expected = base64.b64decode(dk_b64.encode("ascii"))
                actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
                return hmac.compare_digest(actual, expected)

            # Legacy deterministic SHA-256 hex
            if len(password_hash) == 64 and all(c in "0123456789abcdef" for c in password_hash.lower()):
                legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
                return hmac.compare_digest(legacy, password_hash.lower())

        except Exception:  # noqa: BLE001
            return False

        return False

    @staticmethod
    def _should_upgrade_hash(password_hash: str) -> bool:
        """Return True if the stored hash should be upgraded."""

        if not password_hash:
            return True

        # Upgrade legacy SHA-256 to bcrypt/pbkdf2
        if len(password_hash) == 64 and all(c in "0123456789abcdef" for c in password_hash.lower()):
            return True

        # Upgrade PBKDF2 to bcrypt when bcrypt is available
        if bcrypt is not None and password_hash.startswith("pbkdf2_sha256$"):
            return True

        return False

    # =====================
    # Sessions
    # =====================

    @staticmethod
    def generate_token() -> str:
        """Generate a secure session token."""

        return secrets.token_urlsafe(32)

    def authenticate(self, username: str, password: str, ip_address: str = "") -> Optional[str]:
        """Authenticate user and create session.

        Parameters:
            username: Username
            password: Password
            ip_address: Optional source IP for audit / rate limiting

        Returns:
            Session token if successful, None otherwise
        """

        now = datetime.now()

        with self._lock:
            user = self.users.get(username)
            if not user or not user.is_active:
                self._log_action("login", "auth", username, username, details={"ip": ip_address}, success=False)
                return None

            # Rate limit failed attempts
            attempts = [
                t
                for t in self._failed_logins.get(username, [])
                if (now - t[0]) <= self._failed_login_window
            ]
            self._failed_logins[username] = attempts

            if len(attempts) >= self._max_failed_logins:
                self._log_action(
                    "login_rate_limited",
                    "auth",
                    user.user_id,
                    username,
                    details={"ip": ip_address, "failed_attempts": len(attempts)},
                    success=False,
                )
                return None

            if not self.verify_password(password, user.password_hash):
                attempts.append((now, ip_address))
                self._failed_logins[username] = attempts
                self._log_action("login", "auth", user.user_id, username, details={"ip": ip_address}, success=False)
                return None

            # Upgrade hash if needed
            if self._should_upgrade_hash(user.password_hash):
                user.password_hash = self.hash_password(password)
                self._save_users()

            # Successful login clears failures
            self._failed_logins.pop(username, None)

            # Create session
            user.session_token = self.generate_token()
            user.token_expires = now + self._token_ttl
            user.last_login = now

            self._log_action("login", "auth", user.user_id, username, details={"ip": ip_address}, success=True)
            return user.session_token

    def validate_token(self, token: str) -> Optional[User]:
        """Validate session token."""

        if not token:
            return None

        now = datetime.now()
        with self._lock:
            for user in self.users.values():
                if user.session_token and hmac.compare_digest(user.session_token, token):
                    if user.token_expires and now < user.token_expires:
                        return user

                    # Token expired
                    user.session_token = None
                    user.token_expires = None
                    return None

        return None

    def logout(self, token: str) -> bool:
        """Logout user and invalidate session."""

        user = self.validate_token(token)
        if not user:
            return False

        with self._lock:
            user.session_token = None
            user.token_expires = None
            self._log_action("logout", "auth", user.user_id, user.username, success=True)
            return True

    def check_permission(self, token: str, permission: Permission) -> bool:
        """Check if user has permission."""

        user = self.validate_token(token)
        if not user:
            return False

        return user.has_permission(permission)

    # =====================
    # User management
    # =====================

    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        full_name: str,
        role_names: List[str],
        department: Optional[str] = None,
    ) -> User:
        """Create a new user."""

        with self._lock:
            if username in self.users:
                raise ValueError(f"User '{username}' already exists")

            roles = [self.roles[r] for r in role_names if r in self.roles]
            if not roles:
                raise ValueError("At least one valid role must be specified")

            user = User(
                user_id=str(uuid.uuid4()),
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                roles=roles,
                full_name=full_name,
                department=department,
            )

            self.users[username] = user
            self._save_users()
            self._log_action("create_user", "user", user.user_id, user.username, success=True)
            return user

    # =====================
    # Audit logging
    # =====================

    def _log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        username: str,
        details: Optional[Dict] = None,
        success: bool = True,
    ):
        """Log user action for audit trail."""

        # Resolve user_id safely
        user_obj = self.users.get(username)
        user_id = user_obj.user_id if user_obj else ""

        log = AuditLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.now(),
            details=details,
            success=success,
        )

        self.audit_logs.append(log)
        self._save_audit_log(log)

    def _save_audit_log(self, log: AuditLog):
        """Save audit log to file."""

        logs_file = self.data_dir / "audit_logs.jsonl"
        with open(logs_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log.to_dict(), ensure_ascii=False) + "\n")

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditLog]:
        """Get filtered audit logs."""

        logs = self.audit_logs

        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        if action:
            logs = [log for log in logs if log.action == action]

        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]

        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]

        return logs


def create_default_admin(rbac_manager: RBACManager) -> User:
    """Create default admin user if none exists.

    Security: the default admin password is not hard-coded.

    - If `RBAC_DEFAULT_ADMIN_PASSWORD` env var is set, it is used.
    - Otherwise, a random password is generated and written to
      `<data_dir>/initial_admin_password.txt`.

    This keeps local/dev instances usable while avoiding a known default.
    """

    if "admin" in rbac_manager.users:
        return rbac_manager.users["admin"]

    password = os.getenv("RBAC_DEFAULT_ADMIN_PASSWORD")
    if not password:
        password = secrets.token_urlsafe(18)
        try:
            cred_path = rbac_manager.data_dir / "initial_admin_password.txt"
            cred_path.write_text(
                "username=admin\npassword={}\ncreated_at={}\n".format(
                    password,
                    datetime.now().isoformat(),
                ),
                encoding="utf-8",
            )
        except Exception:  # noqa: BLE001
            pass

    return rbac_manager.create_user(
        username="admin",
        password=password,
        email="admin@example.com",
        full_name="System Administrator",
        role_names=[UserRole.ADMIN.value],
    )
