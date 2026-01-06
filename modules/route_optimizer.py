"""
Route Optimization Module

Optimizes vessel routes considering:
- Distance minimization
- Canal fees
- Weather conditions
- Bunker port availability
- Time windows
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class OptimizationObjective(Enum):
    """Optimization objectives."""
    MINIMIZE_DISTANCE = "minimize_distance"
    MINIMIZE_COST = "minimize_cost"
    MINIMIZE_TIME = "minimize_time"
    MAXIMIZE_PROFIT = "maximize_profit"


@dataclass
class RouteSegment:
    """A segment of a route between two ports."""
    from_port: str
    to_port: str
    distance_nm: float
    transit_time_hours: float
    cost_usd: float = 0
    canal_fee_usd: float = 0
    canal_name: Optional[str] = None
    weather_score: float = 1.0  # 0-1, where 1 is perfect conditions
    bunker_available: bool = False
    
    def get_total_cost(self) -> float:
        """Get total cost including canal fees."""
        return self.cost_usd + self.canal_fee_usd
    
    def get_adjusted_time(self) -> float:
        """Get transit time adjusted for weather."""
        return self.transit_time_hours / self.weather_score


@dataclass
class Route:
    """Complete route from origin to destination."""
    route_id: str
    segments: List[RouteSegment]
    total_distance_nm: float
    total_time_hours: float
    total_cost_usd: float
    ports_sequence: List[str]
    optimization_objective: OptimizationObjective
    
    def get_summary(self) -> Dict:
        """Get route summary."""
        return {
            'route_id': self.route_id,
            'from': self.ports_sequence[0],
            'to': self.ports_sequence[-1],
            'total_distance_nm': self.total_distance_nm,
            'total_time_hours': self.total_time_hours,
            'total_cost_usd': self.total_cost_usd,
            'number_of_segments': len(self.segments),
            'ports_visited': len(self.ports_sequence)
        }


class RouteGraph:
    """Graph representation of route network."""
    
    def __init__(self):
        self.adjacency: Dict[str, List[RouteSegment]] = {}
        self.ports: Set[str] = set()
    
    def add_segment(self, segment: RouteSegment):
        """Add a route segment to the graph."""
        if segment.from_port not in self.adjacency:
            self.adjacency[segment.from_port] = []
        
        self.adjacency[segment.from_port].append(segment)
        self.ports.add(segment.from_port)
        self.ports.add(segment.to_port)
    
    def get_neighbors(self, port: str) -> List[RouteSegment]:
        """Get all segments departing from a port."""
        return self.adjacency.get(port, [])


class RouteOptimizer:
    """
    Optimizes vessel routes using various algorithms.
    
    Features:
    - Dijkstra's algorithm for shortest path
    - Multi-objective optimization
    - Canal cost consideration
    - Weather routing
    - Bunker optimization integration
    """
    
    def __init__(self, route_graph: RouteGraph):
        """
        Initialize route optimizer.
        
        Parameters:
            route_graph: Graph of available route segments
        """
        self.graph = route_graph
    
    def find_optimal_route(
        self,
        origin: str,
        destination: str,
        objective: OptimizationObjective = OptimizationObjective.MINIMIZE_DISTANCE,
        avoid_ports: Optional[List[str]] = None,
        required_ports: Optional[List[str]] = None,
        max_segments: int = 10
    ) -> Optional[Route]:
        """
        Find optimal route between two ports.
        
        Parameters:
            origin: Origin port
            destination: Destination port
            objective: Optimization objective
            avoid_ports: Ports to avoid in the route
            required_ports: Ports that must be visited
            max_segments: Maximum number of segments allowed
            
        Returns:
            Optimal route or None if no route found
        """
        if avoid_ports is None:
            avoid_ports = []
        if required_ports is None:
            required_ports = []
        
        # Use A* algorithm for route finding
        route_segments = self._find_path_astar(
            origin,
            destination,
            objective,
            avoid_ports,
            max_segments
        )
        
        if not route_segments:
            return None
        
        # Build ports sequence
        ports_sequence = [origin]
        for segment in route_segments:
            ports_sequence.append(segment.to_port)
        
        # Verify required ports are visited
        if required_ports:
            if not all(port in ports_sequence for port in required_ports):
                # Try to insert required ports
                route_segments = self._insert_required_ports(
                    route_segments,
                    required_ports,
                    objective
                )
                if not route_segments:
                    return None
        
        # Calculate totals
        total_distance = sum(seg.distance_nm for seg in route_segments)
        total_time = sum(seg.get_adjusted_time() for seg in route_segments)
        total_cost = sum(seg.get_total_cost() for seg in route_segments)
        
        # Rebuild ports sequence
        ports_sequence = [origin]
        for segment in route_segments:
            ports_sequence.append(segment.to_port)
        
        return Route(
            route_id=f"{origin}_{destination}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            segments=route_segments,
            total_distance_nm=total_distance,
            total_time_hours=total_time,
            total_cost_usd=total_cost,
            ports_sequence=ports_sequence,
            optimization_objective=objective
        )
    
    def _find_path_astar(
        self,
        start: str,
        goal: str,
        objective: OptimizationObjective,
        avoid_ports: List[str],
        max_segments: int
    ) -> List[RouteSegment]:
        """
        A* pathfinding algorithm.
        
        Parameters:
            start: Start port
            goal: Goal port
            objective: Optimization objective
            avoid_ports: Ports to avoid
            max_segments: Maximum segments allowed
            
        Returns:
            List of route segments forming the path
        """
        # Priority queue: (priority, cost_so_far, current_port, path)
        from heapq import heappush, heappop
        
        frontier = []
        heappush(frontier, (0, 0, start, []))
        
        visited = set()
        
        while frontier:
            priority, cost_so_far, current_port, path = heappop(frontier)
            
            if current_port == goal:
                return path
            
            if current_port in visited:
                continue
            
            visited.add(current_port)
            
            # Don't exceed max segments
            if len(path) >= max_segments:
                continue
            
            # Explore neighbors
            for segment in self.graph.get_neighbors(current_port):
                if segment.to_port in avoid_ports:
                    continue
                
                if segment.to_port in visited:
                    continue
                
                new_path = path + [segment]
                new_cost = cost_so_far + self._get_segment_cost(segment, objective)
                
                # Heuristic: straight-line distance (simplified)
                heuristic = 0  # In real implementation, use great circle distance
                
                priority = new_cost + heuristic
                
                heappush(frontier, (priority, new_cost, segment.to_port, new_path))
        
        return []  # No path found
    
    def _get_segment_cost(self, segment: RouteSegment, objective: OptimizationObjective) -> float:
        """Get cost of a segment based on optimization objective."""
        if objective == OptimizationObjective.MINIMIZE_DISTANCE:
            return segment.distance_nm
        elif objective == OptimizationObjective.MINIMIZE_COST:
            return segment.get_total_cost()
        elif objective == OptimizationObjective.MINIMIZE_TIME:
            return segment.get_adjusted_time()
        else:  # MAXIMIZE_PROFIT (inverse of cost)
            return -segment.get_total_cost() if segment.get_total_cost() > 0 else 1000000
    
    def _insert_required_ports(
        self,
        route_segments: List[RouteSegment],
        required_ports: List[str],
        objective: OptimizationObjective
    ) -> List[RouteSegment]:
        """
        Insert required ports into the existing route.
        
        Parameters:
            route_segments: Current route segments
            required_ports: Ports that must be visited
            objective: Optimization objective
            
        Returns:
            Modified route segments
        """
        # Strategy: Find best insertion point for each required port
        modified_segments = route_segments.copy()
        
        for port in required_ports:
            # Check if already in route
            ports_in_route = set(seg.from_port for seg in modified_segments)
            ports_in_route.add(modified_segments[-1].to_port if modified_segments else "")
            
            if port in ports_in_route:
                continue
            
            # Find best insertion point
            best_cost = float('inf')
            best_insert_idx = -1
            best_new_segments = []
            
            for i in range(len(modified_segments) + 1):
                # Try inserting at position i
                if i == 0:
                    prev_port = modified_segments[0].from_port if modified_segments else ""
                else:
                    prev_port = modified_segments[i-1].to_port
                
                if i < len(modified_segments):
                    next_port = modified_segments[i].to_port
                else:
                    next_port = modified_segments[-1].to_port if modified_segments else ""
                
                # Try to find sements: prev_port -> port -> next_port
                seg1_candidates = self.graph.get_neighbors(prev_port)
                seg1 = None
                for s in seg1_candidates:
                    if s.to_port == port:
                        seg1 = s
                        break
                
                seg2_candidates = self.graph.get_neighbors(port)
                seg2 = None
                for s in seg2_candidates:
                    if s.to_port == next_port:
                        seg2 = s
                        break
                
                if seg1 and seg2:
                    # Calculate cost of this insertion
                    insertion_cost = (
                        self._get_segment_cost(seg1, objective) +
                        self._get_segment_cost(seg2, objective)
                    )
                    
                    # Remove cost of original segment if replacing
                    if i < len(modified_segments):
                        insertion_cost -= self._get_segment_cost(modified_segments[i], objective)
                    
                    if insertion_cost < best_cost:
                        best_cost = insertion_cost
                        best_insert_idx = i
                        best_new_segments = [seg1, seg2]
            
            # Insert at best position
            if best_insert_idx >= 0:
                if best_insert_idx < len(modified_segments):
                    # Replace existing segment
                    modified_segments = (
                        modified_segments[:best_insert_idx] +
                        best_new_segments +
                        modified_segments[best_insert_idx+1:]
                    )
                else:
                    # Append to end
                    modified_segments.extend(best_new_segments)
        
        return modified_segments
    
    def find_alternative_routes(
        self,
        origin: str,
        destination: str,
        objective: OptimizationObjective = OptimizationObjective.MINIMIZE_DISTANCE,
        num_alternatives: int = 3
    ) -> List[Route]:
        """
        Find multiple alternative routes between two ports.
        
        Parameters:
            origin: Origin port
            destination: Destination port
            objective: Optimization objective
            num_alternatives: Number of alternative routes to find
            
        Returns:
            List of alternative routes
        """
        routes = []
        avoided_segments = set()
        
        for _ in range(num_alternatives):
            # Temporarily remove avoided segments
            original_adjacency = self.graph.adjacency.copy()
            
            for port, segments in self.graph.adjacency.items():
                self.graph.adjacency[port] = [
                    seg for seg in segments
                    if (seg.from_port, seg.to_port) not in avoided_segments
                ]
            
            # Find route
            route = self.find_optimal_route(origin, destination, objective)
            
            # Restore adjacency
            self.graph.adjacency = original_adjacency
            
            if route:
                routes.append(route)
                
                # Mark segments of this route to be avoided in next iteration
                for segment in route.segments:
                    avoided_segments.add((segment.from_port, segment.to_port))
            else:
                break  # No more routes found
        
        return routes
    
    def optimize_multi_port_route(
        self,
        ports: List[str],
        objective: OptimizationObjective = OptimizationObjective.MINIMIZE_DISTANCE,
        return_to_start: bool = False
    ) -> Optional[Route]:
        """
        Optimize route visiting multiple ports (Traveling Salesman Problem).
        
        Parameters:
            ports: List of ports to visit
            objective: Optimization objective
            return_to_start: Whether to return to starting port
            
        Returns:
            Optimized route or None
        """
        if len(ports) < 2:
            return None
        
        # For small number of ports, use brute force
        # For larger numbers, use heuristic approaches
        if len(ports) <= 8:
            return self._tsp_brute_force(ports, objective, return_to_start)
        else:
            return self._tsp_nearest_neighbor(ports, objective, return_to_start)
    
    def _tsp_brute_force(
        self,
        ports: List[str],
        objective: OptimizationObjective,
        return_to_start: bool
    ) -> Optional[Route]:
        """Solve TSP using brute force (for small instances)."""
        from itertools import permutations
        
        start_port = ports[0]
        remaining_ports = ports[1:]
        
        best_route = None
        best_cost = float('inf')
        
        for perm in permutations(remaining_ports):
            port_sequence = [start_port] + list(perm)
            if return_to_start:
                port_sequence.append(start_port)
            
            # Build route for this sequence
            segments = []
            total_cost = 0
            
            for i in range(len(port_sequence) - 1):
                from_port = port_sequence[i]
                to_port = port_sequence[i + 1]
                
                # Find segment
                candidates = self.graph.get_neighbors(from_port)
                segment = None
                for seg in candidates:
                    if seg.to_port == to_port:
                        segment = seg
                        break
                
                if not segment:
                    # No direct connection, try finding intermediate route
                    sub_route = self.find_optimal_route(from_port, to_port, objective)
                    if not sub_route:
                        total_cost = float('inf')
                        break
                    segments.extend(sub_route.segments)
                    total_cost += sum(self._get_segment_cost(s, objective) for s in sub_route.segments)
                else:
                    segments.append(segment)
                    total_cost += self._get_segment_cost(segment, objective)
            
            if total_cost < best_cost:
                best_cost = total_cost
                
                total_distance = sum(seg.distance_nm for seg in segments)
                total_time = sum(seg.get_adjusted_time() for seg in segments)
                total_cost_usd = sum(seg.get_total_cost() for seg in segments)
                
                best_route = Route(
                    route_id=f"TSP_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    segments=segments,
                    total_distance_nm=total_distance,
                    total_time_hours=total_time,
                    total_cost_usd=total_cost_usd,
                    ports_sequence=port_sequence,
                    optimization_objective=objective
                )
        
        return best_route
    
    def _tsp_nearest_neighbor(
        self,
        ports: List[str],
        objective: OptimizationObjective,
        return_to_start: bool
    ) -> Optional[Route]:
        """Solve TSP using nearest neighbor heuristic."""
        unvisited = set(ports)
        current_port = ports[0]
        unvisited.remove(current_port)
        
        port_sequence = [current_port]
        segments = []
        
        while unvisited:
            # Find nearest unvisited port
            nearest_port = None
            nearest_segment = None
            best_cost = float('inf')
            
            for next_port in unvisited:
                candidates = self.graph.get_neighbors(current_port)
                for segment in candidates:
                    if segment.to_port == next_port:
                        cost = self._get_segment_cost(segment, objective)
                        if cost < best_cost:
                            best_cost = cost
                            nearest_port = next_port
                            nearest_segment = segment
                        break
            
            if nearest_segment:
                segments.append(nearest_segment)
                port_sequence.append(nearest_port)
                current_port = nearest_port
                unvisited.remove(nearest_port)
            else:
                # No direct connection found
                return None
        
        if return_to_start:
            # Add return segment
            start_port = ports[0]
            candidates = self.graph.get_neighbors(current_port)
            return_segment = None
            for segment in candidates:
                if segment.to_port == start_port:
                    return_segment = segment
                    break
            
            if return_segment:
                segments.append(return_segment)
                port_sequence.append(start_port)
        
        total_distance = sum(seg.distance_nm for seg in segments)
        total_time = sum(seg.get_adjusted_time() for seg in segments)
        total_cost_usd = sum(seg.get_total_cost() for seg in segments)
        
        return Route(
            route_id=f"TSP_NN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            segments=segments,
            total_distance_nm=total_distance,
            total_time_hours=total_time,
            total_cost_usd=total_cost_usd,
            ports_sequence=port_sequence,
            optimization_objective=objective
        )


def create_sample_route_graph() -> RouteGraph:
    """Create sample route graph for testing."""
    graph = RouteGraph()
    
    # Add sample segments
    segments = [
        RouteSegment("SINGAPORE", "COLOMBO", 1500, 4.2, 50000),
        RouteSegment("SINGAPORE", "PORT_SAID", 5500, 15.3, 150000, canal_fee_usd=350000, canal_name="Suez"),
        RouteSegment("COLOMBO", "PORT_SAID", 4000, 11.1, 100000),
        RouteSegment("PORT_SAID", "ROTTERDAM", 2500, 6.9, 80000),
        RouteSegment("ROTTERDAM", "HOUSTON", 4500, 12.5, 120000),
        RouteSegment("SINGAPORE", "PANAMA", 9000, 25.0, 250000, canal_fee_usd=450000, canal_name="Panama"),
        RouteSegment("PANAMA", "HOUSTON", 2000, 5.6, 60000),
    ]
    
    for segment in segments:
        graph.add_segment(segment)
    
    return graph
