"""
Type extensions for api_server_enhanced.py
Provides type hints and extensions for Flask Request, User models, and data loaders.
"""

from flask import Request as FlaskRequest
from typing import Optional, Any, Dict, List
from datetime import datetime


class RequestWithUser(FlaskRequest):
    """Extended Flask Request with current_user attribute for type checking."""
    current_user: Optional['User'] = None


class User:
    """
    User model with authentication tokens.
    This is a type stub for modules.rbac.User to provide type hints.
    """
    user_id: str
    username: str
    email: str
    token: str
    token_expires: Optional[datetime]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
        }


# Type extensions for data loaders
class DeepSeaLoaderProtocol:
    """
    Protocol for DeepSeaLoader with load_all method.
    Use this for type hints when the actual loader may not have all methods.
    """
    
    def load_all(self) -> 'DeepSeaData':
        """Load all deep sea data."""
        raise NotImplementedError("Subclass must implement load_all()")
    
    def load(self) -> 'DeepSeaData':
        """Alternative load method."""
        raise NotImplementedError("Subclass must implement load()")


class OlyaLoaderProtocol:
    """
    Protocol for OlyaLoader with standard load method.
    """
    
    def load(self) -> 'OlyaData':
        """Load Olya module data."""
        raise NotImplementedError("Subclass must implement load()")


class DeepSeaData:
    """Type stub for DeepSea data structure."""
    vessels: Dict[str, 'Vessel']
    ports: Dict[str, 'Port']
    routes: List['Route']
    voyage_plans: List['VoyagePlan']


class OlyaData:
    """Type stub for Olya data structure."""
    roster: Dict[str, 'Vessel']  # Vessel roster
    routes: List['Route']
    schedules: List[Dict[str, Any]]


class Vessel:
    """Generic vessel model."""
    vessel_id: str
    vessel_name: str
    vessel_class: Optional[str] = None
    vessel_type: Optional[str] = None
    dwt_mt: Optional[float] = None
    capacity_mt: Optional[float] = None
    speed_kts: Optional[float] = None


class Port:
    """Generic port model."""
    port_id: str
    port_name: str


class Route:
    """Generic route model."""
    route_id: str
    from_port: str
    to_port: str


class VoyagePlan:
    """Voyage plan with route legs."""
    voyage_id: str
    route_legs: List['RouteLeg']


class RouteLeg:
    """A leg of a route."""
    from_port: str
    to_port: str
    distance_nm: float
