"""
Простой загрузчик CSV данных
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class Port:
    """Порт"""
    port_id: str
    port_name: str
    country: str
    basin: str
    can_handle_liquid: bool
    can_handle_dry: bool
    
    def __hash__(self):
        return hash(self.port_id)


@dataclass
class Vessel:
    """Судно"""
    vessel_id: str
    vessel_name: str
    vessel_type: str  # Tanker, Bulk
    vessel_class: str
    dwt_mt: float
    capacity_mt: float
    draft_max_m: float
    contract_type: str  # TimeCharter, Spot
    tc_daily_hire_usd: Optional[float]
    basin_home: str
    suitable_vegoils: bool
    suitable_agri: bool
    
    @property
    def is_river_sea(self) -> bool:
        """Река-море судно (может работать в Olya)"""
        return 'RIVERSEA' in self.vessel_class.upper()
    
    def __hash__(self):
        return hash(self.vessel_id)


@dataclass
class VoyageLeg:
    """Этап рейса"""
    voyage_leg_id: str
    voyage_id: str
    leg_seq: int
    vessel_id: str
    op_group: str  # Cargo_ops_ld, Laden, Cargo_ops_ds, etc.
    op_detail: str
    leg_type: str  # Port, Sea, Canal
    port_start_id: str
    port_end_id: str
    berth_id: Optional[str]
    cargo_id: Optional[str]
    qty_mt: float
    start_time: datetime
    end_time: datetime
    status: str  # Planned, In Process, Completed
    remarks: str = ""
    
    @property
    def duration_days(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 86400
        return 0
    
    @property
    def is_loading(self) -> bool:
        return self.op_group == 'Cargo_ops_ld'
    
    @property
    def is_discharge(self) -> bool:
        return self.op_group == 'Cargo_ops_ds'
    
    @property
    def is_sea_leg(self) -> bool:
        return self.leg_type == 'Sea'
    
    def __hash__(self):
        return hash(self.voyage_leg_id)


@dataclass
class Voyage:
    """Рейс (агрегированный из legs)"""
    voyage_id: str
    vessel_id: str
    vessel_name: str
    legs: List[VoyageLeg] = field(default_factory=list)
    
    @property
    def start_time(self) -> Optional[datetime]:
        if self.legs:
            return min(leg.start_time for leg in self.legs)
        return None
    
    @property
    def end_time(self) -> Optional[datetime]:
        if self.legs:
            return max(leg.end_time for leg in self.legs)
        return None
    
    @property
    def load_port(self) -> Optional[str]:
        for leg in self.legs:
            if leg.is_loading:
                return leg.port_start_id
        return None
    
    @property
    def discharge_port(self) -> Optional[str]:
        for leg in self.legs:
            if leg.is_discharge:
                return leg.port_start_id
        return None
    
    @property
    def cargo_id(self) -> Optional[str]:
        for leg in self.legs:
            if leg.cargo_id:
                return leg.cargo_id
        return None
    
    @property
    def qty_mt(self) -> float:
        for leg in self.legs:
            if leg.is_loading and leg.qty_mt > 0:
                return leg.qty_mt
        return 0
    
    @property
    def status(self) -> str:
        statuses = [leg.status for leg in self.legs]
        if all(s == 'Completed' for s in statuses):
            return 'Completed'
        elif any(s == 'In Process' for s in statuses):
            return 'In Progress'
        return 'Planned'


@dataclass
class CargoMovement:
    """Движение груза"""
    cargo_movement_id: str
    product_name: str
    qty_mt: float
    load_port_id: str
    discharge_port_id: str
    load_date_plan: date
    discharge_date_plan: Optional[date]
    vessel_id: Optional[str]
    buyer_name: str
    delivery_deadline: date
    status: str
    rail_id: Optional[str] = None


@dataclass
class RailCargo:
    """Железнодорожный груз"""
    rail_cargo_id: str
    product_name: str
    qty_mt: float
    origin_station: str
    destination_port_id: str
    departure_date: date
    eta_port_date: date
    actual_arrival: Optional[date]
    status: str
    assigned_cargo_movement_id: Optional[str]


@dataclass 
class AllData:
    """Контейнер всех данных"""
    ports: Dict[str, Port] = field(default_factory=dict)
    vessels: Dict[str, Vessel] = field(default_factory=dict)
    voyage_legs: List[VoyageLeg] = field(default_factory=list)
    voyages: Dict[str, Voyage] = field(default_factory=dict)
    cargo_movements: Dict[str, CargoMovement] = field(default_factory=dict)
    rail_cargo: Dict[str, RailCargo] = field(default_factory=dict)
    
    def get_vessel_voyages(self, vessel_id: str) -> List[Voyage]:
        """Получить все рейсы судна"""
        return [v for v in self.voyages.values() if v.vessel_id == vessel_id]
    
    def get_olya_operations(self) -> List[VoyageLeg]:
        """Получить все операции в Olya"""
        return [leg for leg in self.voyage_legs 
                if leg.port_start_id == 'OYA' or leg.port_end_id == 'OYA']


class DataLoader:
    """Загрузчик данных из CSV"""
    
    def __init__(self, input_dir: str = "input"):
        self.input_dir = Path(input_dir)
    
    def load_all(self) -> AllData:
        """Загрузить все данные"""
        logger.info("=" * 60)
        logger.info("ЗАГРУЗКА ДАННЫХ")
        logger.info("=" * 60)
        
        data = AllData()
        
        # Загружаем в порядке зависимостей
        data.ports = self._load_ports()
        data.vessels = self._load_vessels()
        data.voyage_legs = self._load_voyage_legs()
        data.cargo_movements = self._load_cargo_movements()
        data.rail_cargo = self._load_rail_cargo()
        
        # Агрегируем legs в voyages
        data.voyages = self._aggregate_voyages(data.voyage_legs, data.vessels)
        
        self._print_summary(data)
        
        return data
    
    def _read_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """Читаем CSV с разделителем ; и поддержкой комментариев (с кэшированием)"""
        return self._read_csv_cached(str(self.input_dir), filename)

    @staticmethod
    @lru_cache(maxsize=32)
    def _read_csv_cached(input_dir_str: str, filename: str) -> Optional[pd.DataFrame]:
        """Cached CSV reader"""
        input_dir = Path(input_dir_str)
        filepath = input_dir / filename
        
        # Try case-insensitive file lookup
        if not filepath.exists():
            # Try capitalized version
            alt_name = filename[0].upper() + filename[1:] if filename else filename
            alt_path = input_dir / alt_name
            if alt_path.exists():
                filepath = alt_path
            else:
                logger.warning(f"Файл не найден: {filepath}")
                return None
        
        try:
            df = pd.read_csv(filepath, delimiter=';', encoding='utf-8', comment='#')
            logger.info(f"   {filename}: {len(df)} записей (cached)")
            return df
        except Exception as e:
            logger.error(f"   Ошибка чтения {filename}: {e}")
            return None
    
    def _load_ports(self) -> Dict[str, Port]:
        """Загрузка портов"""
        logger.info("Загрузка портов...")
        ports = {}
        
        df = self._read_csv('ports.csv')
        if df is None:
            return ports
        
        for _, row in df.iterrows():
            port = Port(
                port_id=str(row['port_id']).strip(),
                port_name=str(row['port_name']).strip(),
                country=str(row.get('country', '')).strip(),
                basin=str(row.get('basin', '')).strip(),  # Make optional
                can_handle_liquid=str(row.get('can_handle_liquid', 'No')).strip().lower() == 'yes',
                can_handle_dry=str(row.get('can_handle_dry', 'No')).strip().lower() == 'yes'
            )
            ports[port.port_id] = port
        
        return ports
    
    def _load_vessels(self) -> Dict[str, Vessel]:
        """Загрузка судов"""
        logger.info("Загрузка судов...")
        vessels = {}
        
        df = self._read_csv('vessels.csv')
        if df is None:
            return vessels
        
        for _, row in df.iterrows():
            tc_hire = row.get('tc_daily_hire_usd')
            if pd.isna(tc_hire) or tc_hire == '':
                tc_hire = None
            else:
                tc_hire = float(tc_hire)
            
            vessel = Vessel(
                vessel_id=str(row['vessel_id']).strip(),
                vessel_name=str(row['vessel_name']).strip(),
                vessel_type=str(row.get('type', 'Unknown')).strip(),  # Make optional
                vessel_class=str(row['vessel_class']).strip(),
                dwt_mt=float(row['dwt_mt']),
                capacity_mt=float(row.get('capacity_mt', row.get('dwt_mt', 0))),  # Fallback to dwt if capacity missing
                draft_max_m=float(row.get('draft_max_m', 0)),  # Make optional
                contract_type=str(row.get('contract_type', 'Spot')).strip(),
                tc_daily_hire_usd=tc_hire,
                basin_home=str(row.get('basin_home', '')).strip(),
                suitable_vegoils=str(row.get('suitable_vegoils', 'No')).strip().lower() == 'yes',
                suitable_agri=str(row.get('suitable_agri', 'No')).strip().lower() == 'yes'
            )
            vessels[vessel.vessel_id] = vessel
        
        return vessels
    
    def _load_voyage_legs(self) -> List[VoyageLeg]:
        """Load voyage legs from CSV - handles both detailed legs and high-level voyage data"""
        logger.info("Loading voyage legs...")
        legs = []
        
        df = self._read_csv('voyage_legs.csv')
        if df is None:
            return legs
        
        # Check which schema we have
        has_detailed_legs = 'voyage_leg_id' in df.columns and 'start_time_plan' in df.columns
        has_voyage_data = 'voyage_id' in df.columns and 'laycan_start' in df.columns
        
        if has_detailed_legs:
            # Original detailed leg format
            legs = self._parse_detailed_legs(df)
        elif has_voyage_data:
            # High-level voyage format - expand to detailed legs
            legs = self._expand_voyages_to_legs(df)
        else:
            logger.warning(f"Voyage legs CSV has unrecognized schema. Columns: {df.columns.tolist()}")
        
        logger.info(f"   Successfully parsed {len(legs)} voyage legs")
        return legs
    
    def _parse_detailed_legs(self, df: pd.DataFrame) -> List[VoyageLeg]:
        """Parse detailed operational legs format"""
        legs = []
        for _, row in df.iterrows():
            try:
                start_time = self._parse_datetime(row.get('start_time_plan'))
                end_time = self._parse_datetime(row.get('end_time_plan'))
                
                if start_time is None or end_time is None:
                    logger.debug(f"Skipping leg {row.get('voyage_leg_id')} - invalid dates")
                    continue
                
                berth_id = row.get('berth_id')
                if pd.isna(berth_id) or str(berth_id).upper() == 'NULL':
                    berth_id = None
                else:
                    berth_id = str(berth_id).strip()
                
                cargo_id = row.get('cargo_id')
                if pd.isna(cargo_id) or str(cargo_id).upper() == 'NULL':
                    cargo_id = None
                else:
                    cargo_id = str(cargo_id).strip()
                
                leg = VoyageLeg(
                    voyage_leg_id=str(row['voyage_leg_id']).strip(),
                    voyage_id=str(row['voyage_id']).strip(),
                    leg_seq=int(row['leg_seq']),
                    vessel_id=str(row['vessel_id']).strip(),
                    op_group=str(row['op_group']).strip(),
                    op_detail=str(row['op_detail']).strip(),
                    leg_type=str(row['leg_type']).strip(),
                    port_start_id=str(row['port_start_id']).strip(),
                    port_end_id=str(row['port_end_id']).strip(),
                    berth_id=berth_id,
                    cargo_id=cargo_id,
                    qty_mt=float(row.get('qty_leg_mt', 0) or 0),
                    start_time=start_time,
                    end_time=end_time,
                    status=str(row.get('status', 'Planned')).strip(),
                    remarks=str(row.get('remarks', '') or '')
                )
                legs.append(leg)
            except Exception as e:
                logger.warning(f"Error parsing detailed leg: {e}")
        return legs
    
    def _expand_voyages_to_legs(self, df: pd.DataFrame) -> List[VoyageLeg]:
        """Expand high-level voyage data into detailed operational legs"""
        legs = []
        for _, row in df.iterrows():
            try:
                voyage_id = str(row['voyage_id']).strip()
                vessel_id = str(row['vessel_id']).strip()
                load_port = str(row['load_port']).strip()
                disch_port = str(row['disch_port']).strip()
                qty_mt = float(row['qty_mt'])
                cargo_type = str(row.get('cargo_type', 'Unknown')).strip()
                
                # Parse laycan dates
                laycan_start = self._parse_datetime(row.get('laycan_start'))
                laycan_end = self._parse_datetime(row.get('laycan_end'))
                
                if laycan_start is None:
                    logger.debug(f"Skipping voyage {voyage_id} - invalid laycan_start")
                    continue
                
                # For high-level data, create simplified legs
                # Leg 1: Loading operation
                leg_load = VoyageLeg(
                    voyage_leg_id=f"{voyage_id}_LD",
                    voyage_id=voyage_id,
                    leg_seq=1,
                    vessel_id=vessel_id,
                    op_group='Cargo_ops_ld',
                    op_detail=f'Loading {cargo_type}',
                    leg_type='Port',
                    port_start_id=load_port,
                    port_end_id=load_port,
                    berth_id=None,
                    cargo_id=voyage_id,  # Use voyage_id as cargo_id
                    qty_mt=qty_mt,
                    start_time=laycan_start,
                    end_time=laycan_start + pd.Timedelta(days=2),  # Estimated 2 days loading
                    status='Planned',
                    remarks=str(row.get('remarks', ''))
                )
                legs.append(leg_load)
                
                # Leg 2: Sea passage
                transit_start = leg_load.end_time
                transit_end = transit_start + pd.Timedelta(days=10)  # Estimated transit
                if laycan_end and laycan_end > transit_start:
                    transit_end = laycan_end
                
                leg_sea = VoyageLeg(
                    voyage_leg_id=f"{voyage_id}_SEA",
                    voyage_id=voyage_id,
                    leg_seq=2,
                    vessel_id=vessel_id,
                    op_group='Laden',
                    op_detail=f'Transit {load_port} to {disch_port}',
                    leg_type='Sea',
                    port_start_id=load_port,
                    port_end_id=disch_port,
                    berth_id=None,
                    cargo_id=voyage_id,
                    qty_mt=qty_mt,
                    start_time=transit_start,
                    end_time=transit_end,
                    status='Planned',
                    remarks=''
                )
                legs.append(leg_sea)
                
                # Leg 3: Discharge operation
                leg_disch = VoyageLeg(
                    voyage_leg_id=f"{voyage_id}_DS",
                    voyage_id=voyage_id,
                    leg_seq=3,
                    vessel_id=vessel_id,
                    op_group='Cargo_ops_ds',
                    op_detail=f'Discharge {cargo_type}',
                    leg_type='Port',
                    port_start_id=disch_port,
                    port_end_id=disch_port,
                    berth_id=None,
                    cargo_id=voyage_id,
                    qty_mt=qty_mt,
                    start_time=transit_end,
                    end_time=transit_end + pd.Timedelta(days=2),  # Estimated 2 days discharge
                    status='Planned',
                    remarks=''
                )
                legs.append(leg_disch)
                
                logger.debug(f"Expanded voyage {voyage_id} into 3 legs")
                
            except Exception as e:
                logger.warning(f"Error expanding voyage to legs: {e}")
        
        return legs
    
    def _load_cargo_movements(self) -> Dict[str, CargoMovement]:
        """Загрузка cargo movements"""
        logger.info("Загрузка cargo movements...")
        movements = {}
        
        df = self._read_csv('cargo_movements.csv')
        if df is None:
            return movements
        
        for _, row in df.iterrows():
            try:
                # Парсинг дат
                load_date = self._parse_date(row.get('load_date_plan'))
                discharge_date = self._parse_date(row.get('discharge_date_plan'))
                deadline = self._parse_date(row.get('delivery_deadline'))
                
                if load_date is None:
                    continue
                
                # Optional fields
                vessel_id = row.get('vessel_id')
                if pd.isna(vessel_id) or str(vessel_id).upper() == 'NULL':
                    vessel_id = None
                else:
                    vessel_id = str(vessel_id).strip()
                
                rail_id = row.get('rail_id')
                if pd.isna(rail_id) or str(rail_id).upper() == 'NULL':
                    rail_id = None
                else:
                    rail_id = str(rail_id).strip()
                
                cm = CargoMovement(
                    cargo_movement_id=str(row['cargo_movement_id']).strip(),
                    product_name=str(row['product_name']).strip(),
                    qty_mt=float(row['qty_mt']),
                    load_port_id=str(row['load_port_id']).strip(),
                    discharge_port_id=str(row['discharge_port_id']).strip(),
                    load_date_plan=load_date,
                    discharge_date_plan=discharge_date,
                    vessel_id=vessel_id,
                    buyer_name=str(row.get('buyer_name', '')).strip(),
                    delivery_deadline=deadline,
                    status=str(row.get('status', 'Planned')).strip(),
                    rail_id=rail_id
                )
                movements[cm.cargo_movement_id] = cm
                
            except Exception as e:
                logger.warning(f"Ошибка парсинга cargo movement: {e}")
        
        return movements
    
    def _load_rail_cargo(self) -> Dict[str, RailCargo]:
        """Загрузка rail cargo"""
        logger.info("Загрузка rail cargo...")
        rail = {}
        
        df = self._read_csv('rail_cargo.csv')
        if df is None:
            return rail
        
        for _, row in df.iterrows():
            try:
                departure = self._parse_date(row.get('departure_date'))
                eta = self._parse_date(row.get('eta_port_date'))
                actual = self._parse_date(row.get('actual_arrival'))
                
                if departure is None or eta is None:
                    continue
                
                assigned_cm = row.get('assigned_cargo_movement_id')
                if pd.isna(assigned_cm) or str(assigned_cm).upper() == 'NULL':
                    assigned_cm = None
                else:
                    assigned_cm = str(assigned_cm).strip()
                
                rc = RailCargo(
                    rail_cargo_id=str(row['rail_cargo_id']).strip(),
                    product_name=str(row['product_name']).strip(),
                    qty_mt=float(row['qty_mt']),
                    origin_station=str(row['origin_station']).strip(),
                    destination_port_id=str(row['destination_port_id']).strip(),
                    departure_date=departure,
                    eta_port_date=eta,
                    actual_arrival=actual,
                    status=str(row.get('status', 'Planned')).strip(),
                    assigned_cargo_movement_id=assigned_cm
                )
                rail[rc.rail_cargo_id] = rc
                
            except Exception as e:
                logger.warning(f"Ошибка парсинга rail cargo: {e}")
        
        return rail
    
    def _aggregate_voyages(self, legs: List[VoyageLeg], vessels: Dict[str, Vessel]) -> Dict[str, Voyage]:
        """Агрегируем legs в voyages"""
        logger.info("Агрегация рейсов...")
        
        # Группируем по voyage_id
        legs_by_voyage = {}
        for leg in legs:
            if leg.voyage_id not in legs_by_voyage:
                legs_by_voyage[leg.voyage_id] = []
            legs_by_voyage[leg.voyage_id].append(leg)
        
        voyages = {}
        for voyage_id, voyage_legs in legs_by_voyage.items():
            sorted_legs = sorted(voyage_legs, key=lambda l: l.leg_seq)
            vessel_id = sorted_legs[0].vessel_id
            vessel_name = vessels.get(vessel_id, Vessel(
                vessel_id=vessel_id, vessel_name=vessel_id,
                vessel_type='Unknown', vessel_class='Unknown',
                dwt_mt=0, capacity_mt=0, draft_max_m=0,
                contract_type='Unknown', tc_daily_hire_usd=None,
                basin_home='', suitable_vegoils=False, suitable_agri=False
            )).vessel_name
            
            voyages[voyage_id] = Voyage(
                voyage_id=voyage_id,
                vessel_id=vessel_id,
                vessel_name=vessel_name,
                legs=sorted_legs
            )
        
        logger.info(f"   Агрегировано {len(voyages)} рейсов")
        return voyages
    
    def _parse_datetime(self, value) -> Optional[datetime]:
        """Парсинг datetime"""
        if pd.isna(value) or value is None or str(value).upper() == 'NULL':
            return None
        
        if isinstance(value, datetime):
            return value
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        
        value_str = str(value).strip()
        
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_date(self, value) -> Optional[date]:
        """Парсинг date"""
        dt = self._parse_datetime(value)
        if dt:
            return dt.date()
        return None
    
    def _print_summary(self, data: AllData):
        """Вывод сводки"""
        logger.info("=" * 60)
        logger.info("СВОДКА ЗАГРУЖЕННЫХ ДАННЫХ")
        logger.info("=" * 60)
        logger.info(f"  Порты:           {len(data.ports)}")
        logger.info(f"  Суда:            {len(data.vessels)}")
        logger.info(f"  Voyage Legs:     {len(data.voyage_legs)}")
        logger.info(f"  Рейсы:           {len(data.voyages)}")
        logger.info(f"  Cargo Movements: {len(data.cargo_movements)}")
        logger.info(f"  Rail Cargo:      {len(data.rail_cargo)}")
        logger.info("=" * 60)