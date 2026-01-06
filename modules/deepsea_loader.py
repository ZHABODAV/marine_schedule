"""
Deep Sea data loader
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

import pandas as pd

from modules.deepsea_data import (
    Canal,
    DeepSeaData,
    DeepSeaParams,
    Distance,
    Port,
    RouteLeg,
    Vessel,
    VoyagePlan,
)

logger = logging.getLogger(__name__)


class DeepSeaLoader:
    """Loader for Deep Sea CSV files."""

    def __init__(self, input_dir: str = "input", voyage_plan_filename: str = "voyage_plan.csv") -> None:
        self.input_dir = Path(input_dir)
        self.deepsea_dir = self.input_dir / "deepsea"
        self.voyage_plan_filename = voyage_plan_filename

    def load(self) -> DeepSeaData:
        """Load all Deep Sea data sets from CSV files."""
        logger.info("=" * 70)
        logger.info("DEEP SEA DATA LOAD")
        logger.info("   Directory: %s", self.input_dir)
        logger.info("=" * 70)

        data = DeepSeaData()

        data.params = self._load_params()
        data.ports = self._load_ports()
        data.distances = self._load_distances()
        data.canals = self._load_canals()
        data.vessels = self._load_fleet()
        data.route_legs = self._load_routes()
        data.voyage_plans = self._load_voyage_plans()

        self._print_summary(data)

        return data

    def _read_csv(self, filename: str, alt_filename: str = None) -> Optional[pd.DataFrame]:
        """Read a CSV file with standard settings, checking multiple locations."""
        # Try primary location (input/filename)
        filepath = self.input_dir / filename
        
        # If not found, try alternative filename in input/
        if not filepath.exists() and alt_filename:
             filepath = self.input_dir / alt_filename

        # If still not found, try deepsea subdirectory
        if not filepath.exists():
            filepath = self.deepsea_dir / filename
            
        # If still not found, try alternative in deepsea
        if not filepath.exists() and alt_filename:
            filepath = self.deepsea_dir / alt_filename

        if not filepath.exists():
            logger.warning(" File not found: %s (checked input/ and input/deepsea/)", filename)
            return None

        try:
            df = pd.read_csv(filepath, delimiter=";", comment="#", encoding="utf-8")
            logger.info("   %s: %d records", filepath.name, len(df))
            return df
        except Exception as exc:  # noqa: BLE001
            logger.error("   Error reading %s: %s", filepath.name, exc)
            return None

    def _load_params(self) -> DeepSeaParams:
        """Load operational parameters."""
        logger.info("\n Parameters...")
        params = DeepSeaParams()

        df = self._read_csv("params_deepsea.csv", "Params.csv")
        if df is None:
            return params

        param_dict = dict(zip(df["parameter"], df["value"]))

        for attr in dir(params):
            if attr.startswith("_"):
                continue
            if attr in param_dict:
                try:
                    setattr(params, attr, float(param_dict[attr]))
                except (ValueError, TypeError) as exc:
                    logger.warning("Could not set parameter %s: %s", attr, exc)

        return params

    def _load_ports(self) -> Dict[str, Port]:
        """Load ports."""
        logger.info("\n Ports...")
        ports: Dict[str, Port] = {}

        df = self._read_csv("ports_deepsea.csv", "Ports.csv")
        if df is None:
            return ports

        for _, row in df.iterrows():
            port = Port(
                port_id=str(row["port_id"]).strip(),
                port_name=str(row["port_name"]).strip(),
                country=str(row.get("country", "")).strip(),
                region=str(row.get("region", "")).strip(),
                latitude=float(row.get("latitude", 0) or 0),
                longitude=float(row.get("longitude", 0) or 0),
                port_type=str(row.get("port_type", "")).strip(),
                max_draft_m=float(row.get("max_draft_m", 20) or 20),
                load_rate_mt_day=float(row.get("load_rate_mt_day", 5000) or 5000),
                disch_rate_mt_day=float(row.get("disch_rate_mt_day", 5000) or 5000),
                port_charges_usd=float(row.get("port_charges_usd", 0) or 0),
                remarks=str(row.get("remarks", "")).strip(),
            )
            ports[port.port_id] = port

        return ports

    def _load_distances(self) -> Dict[Tuple[str, str], Distance]:
        """Load distances between ports."""
        logger.info("\n Distances...")
        distances: Dict[Tuple[str, str], Distance] = {}

        df = self._read_csv("distances_deepsea.csv", "Distances.csv")
        if df is None:
            return distances

        for _, row in df.iterrows():
            from_port = str(row["from_port"]).strip()
            to_port = str(row["to_port"]).strip()

            canal_id = row.get("canal_id")
            if pd.isna(canal_id) or str(canal_id).strip() == "":
                canal_id = None
            else:
                canal_id = str(canal_id).strip()

            dist = Distance(
                from_port=from_port,
                to_port=to_port,
                distance_nm=float(row["distance_nm"]),
                via_canal=str(row.get("via_canal", "no")).lower() == "yes",
                canal_id=canal_id,
                eca_miles=float(row.get("eca_miles", 0) or 0),
            )
            distances[(from_port, to_port)] = dist

        return distances

    def _load_canals(self) -> Dict[str, Canal]:
        """Load canal data."""
        logger.info("\nCanals...")
        canals: Dict[str, Canal] = {}

        df = self._read_csv("canals_deepsea.csv", "Canals.csv")
        if df is None:
            return canals

        for _, row in df.iterrows():
            canal = Canal(
                canal_id=str(row["canal_id"]).strip(),
                canal_name=str(row["canal_name"]).strip(),
                transit_hours=float(row.get("transit_hours", 12) or 12),
                base_fee_usd=float(row.get("base_fee_usd", 0) or 0),
                fee_per_ton_usd=float(row.get("fee_per_ton_usd", 0) or 0),
                max_draft_m=float(row.get("max_draft_m", 0) or 0),
                max_beam_m=float(row.get("max_beam_m", 0) or 0),
                max_loa_m=float(row.get("max_loa_m", 0) or 0),
                waiting_hours_avg=float(row.get("waiting_hours_avg", 6) or 6),
            )
            canals[canal.canal_id] = canal

        return canals

    def _load_fleet(self) -> Dict[str, Vessel]:
        """Load fleet data."""
        logger.info("\n Fleet...")
        vessels: Dict[str, Vessel] = {}

        df = self._read_csv("fleet_deepsea.csv", "Vessels.csv")
        if df is None:
            return vessels

        for _, row in df.iterrows():
            vessel = Vessel(
                vessel_id=str(row["vessel_id"]).strip(),
                vessel_name=str(row["vessel_name"]).strip(),
                imo=str(row.get("imo", "")).strip(),
                vessel_type=str(row["vessel_type"]).strip(),
                vessel_class=str(row["vessel_class"]).strip(),
                dwt_mt=float(row["dwt_mt"]),
                capacity_mt=float(row["capacity_mt"]),
                loa_m=float(row["loa_m"]),
                beam_m=float(row["beam_m"]),
                draft_laden_m=float(row["draft_laden_m"]),
                draft_ballast_m=float(row["draft_ballast_m"]),
                speed_laden_kn=float(row["speed_laden_kn"]),
                speed_ballast_kn=float(row["speed_ballast_kn"]),
                consumption_laden_mt=float(row.get("consumption_laden_mt", 30) or 30),
                consumption_ballast_mt=float(row.get("consumption_ballast_mt", 25) or 25),
                daily_hire_usd=float(row["daily_hire_usd"]),
                owner=str(row.get("owner", "")).strip(),
                flag=str(row.get("flag", "")).strip(),
                built_year=int(row.get("built_year", 2010) or 2010),
                ice_class=str(row.get("ice_class", "")).strip(),
                tank_coated=str(row.get("tank_coated", "No")).lower() == "yes",
                heating_capable=str(row.get("heating_capable", "No")).lower() == "yes",
            )
            vessels[vessel.vessel_id] = vessel

        by_class: Dict[str, int] = {}
        for vessel in vessels.values():
            by_class[vessel.vessel_class] = by_class.get(vessel.vessel_class, 0) + 1
        for vessel_class, count in by_class.items():
            logger.info("     %s: %d", vessel_class, count)

        return vessels

    def _load_routes(self) -> Dict[str, List[RouteLeg]]:
        """Load routes and their legs."""
        logger.info("\n Routes...")
        routes: Dict[str, List[RouteLeg]] = {}

        df = self._read_csv("routes_deepsea.csv", "Routes.csv")
        if df is None:
            return routes

        for _, row in df.iterrows():
            route_id = str(row["route_id"]).strip()

            canal_id = row.get("canal_id")
            if pd.isna(canal_id) or str(canal_id).strip() == "":
                canal_id = None
            else:
                canal_id = str(canal_id).strip()

            leg = RouteLeg(
                route_id=route_id,
                route_name=str(row["route_name"]).strip(),
                leg_seq=int(row["leg_seq"]),
                leg_type=str(row["leg_type"]).strip().lower(),
                from_port=str(row["from_port"]).strip(),
                to_port=str(row["to_port"]).strip(),
                cargo_state=str(row.get("cargo_state", "laden")).strip().lower(),
                canal_id=canal_id,
                remarks=str(row.get("remarks", "")).strip(),
            )

            if route_id not in routes:
                routes[route_id] = []
            routes[route_id].append(leg)

        for route_id in routes:
            routes[route_id].sort(key=lambda leg: leg.leg_seq)

        logger.info("     Routes: %d", len(routes))

        return routes

    def _load_voyage_plans(self) -> List[VoyagePlan]:
        """Load voyage plans."""
        logger.info("\nVoyage plans...")
        plans: List[VoyagePlan] = []

        df = self._read_csv(self.voyage_plan_filename, "voyage_plan.csv")
        if df is None:
            return plans

        for _, row in df.iterrows():
            laycan_start = self._parse_date(row.get("laycan_start"))
            laycan_end = self._parse_date(row.get("laycan_end"))

            if laycan_start is None:
                continue
            if laycan_end is None:
                laycan_end = laycan_start + timedelta(days=5)

            plan = VoyagePlan(
                voyage_id=str(row["voyage_id"]).strip(),
                vessel_id=str(row["vessel_id"]).strip(),
                route_id=str(row["route_id"]).strip(),
                cargo_type=str(row.get("cargo_type", "")).strip(),
                qty_mt=float(row.get("qty_mt", 0) or 0),
                load_port=str(row.get("load_port", "")).strip(),
                disch_port=str(row.get("disch_port", "")).strip(),
                laycan_start=laycan_start,
                laycan_end=laycan_end,
                charterer=str(row.get("charterer", "")).strip(),
                freight_rate_mt=float(row.get("freight_rate_mt", 0) or 0),
                remarks=str(row.get("remarks", "")).strip(),
            )
            plans.append(plan)

        return plans

    def _parse_date(self, value) -> Optional[date]:
        """Parse a date value from supported formats."""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, (datetime, date)):
            return value if isinstance(value, date) else value.date()

        for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"]:
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except Exception:  # noqa: BLE001, TRY002
                continue
        return None

    def _print_summary(self, data: DeepSeaData) -> None:
        """Print a summary of loaded datasets."""
        logger.info("\n" + "=" * 70)
        logger.info("DEEP SEA SUMMARY")
        logger.info("=" * 70)
        logger.info("  Ports:      %d", len(data.ports))
        logger.info("  Distances:  %d", len(data.distances))
        logger.info("  Canals:     %d", len(data.canals))
        logger.info("  Vessels:    %d", len(data.vessels))
        logger.info("  Routes:     %d", len(data.route_legs))
        logger.info("  Voyages:    %d", len(data.voyage_plans))
