"""
Загрузчик данных Olya из CSV
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, List, Tuple
import logging

from modules.olya_data import (
    OlyaData, OlyaParams, Port, Distance, Vessel, VoyageConfig
)

logger = logging.getLogger(__name__)


class OlyaLoader:
    """Загрузчик CSV файлов для Olya"""
    
    def __init__(self, input_dir: str = "input/olya"):
        self.input_dir = Path(input_dir)
    
    def load(self) -> OlyaData:
        """Загрузить все данные"""
        logger.info("=" * 70)
        logger.info("ЗАГРУЗКА ДАННЫХ OLYA")
        logger.info(f"   Директория: {self.input_dir}")
        logger.info("=" * 70)
        
        data = OlyaData()
        
        data.params = self._load_params()
        data.ports = self._load_ports()
        data.distances = self._load_distances()
        data.vessels = self._load_fleet()
        data.voyage_configs = self._load_voyage_configs()
        
        self._print_summary(data)
        
        return data
    
    def _read_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """Чтение CSV с пропуском комментариев"""
        filepath = self.input_dir / filename
        
        if not filepath.exists():
            logger.warning(f" Файл не найден: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath, delimiter=';', comment='#', encoding='utf-8')
            logger.info(f"   {filename}: {len(df)} записей")
            return df
        except Exception as e:
            logger.error(f"  Ошибка: {e}")
            return None
    
    def _load_params(self) -> OlyaParams:
        """Загрузка параметров"""
        logger.info("\n Параметры...")
        params = OlyaParams()
        
        df = self._read_csv('params_olya.csv')
        if df is None:
            return params
        
        param_dict = dict(zip(df['parameter'], df['value']))
        
        for attr in ['speed_barge', 'speed_vessel', 'load_rate_bko', 'load_rate_oya',
                     'discharge_rate_oya', 'discharge_rate_iran', 'storage_capacity',
                     'demurrage_barge', 'demurrage_vessel', 'ideal_buffer', 'port_turnaround']:
            if attr in param_dict:
                try:
                    setattr(params, attr, float(param_dict[attr]))
                except (ValueError, TypeError) as e:
                    logger.warning(f"   Не удалось преобразовать параметр {attr}: {e}")
        
        return params
    
    def _load_ports(self) -> Dict[str, Port]:
        """Загрузка портов"""
        logger.info("\n Порты...")
        ports = {}
        
        df = self._read_csv('ports_olya.csv')
        if df is None:
            return ports
        
        for _, row in df.iterrows():
            port = Port(
                port_id=str(row['port_id']).strip(),
                port_name=str(row['port_name']).strip(),
                country=str(row.get('country', '')).strip(),
                port_type=str(row.get('type', '')).strip()
            )
            ports[port.port_id] = port
        
        return ports
    
    def _load_distances(self) -> Dict[Tuple[str, str], float]:
        """Загрузка расстояний"""
        logger.info("\n Расстояния...")
        distances = {}
        
        df = self._read_csv('distances_olya.csv')
        if df is None:
            return distances
        
        for _, row in df.iterrows():
            from_port = str(row['from_port']).strip()
            to_port = str(row['to_port']).strip()
            dist = float(row['distance_nm'])
            distances[(from_port, to_port)] = dist
        
        return distances
    
    def _load_fleet(self) -> Dict[str, Vessel]:
        """Загрузка флота"""
        logger.info("\n Флот...")
        vessels = {}
        
        df = self._read_csv('fleet_olya.csv')
        if df is None:
            return vessels
        
        for _, row in df.iterrows():
            vessel = Vessel(
                vessel_id=str(row['vessel_id']).strip(),
                vessel_name=str(row['vessel_name']).strip(),
                vessel_type=str(row['vessel_type']).strip().lower(),
                vessel_class=str(row['vessel_class']).strip(),
                capacity_mt=float(row['capacity_mt']),
                draft_m=float(row['draft_m']),
                speed_kn=float(row['speed_kn']),
                daily_rate_usd=float(row['daily_rate_usd']),
                owner=str(row.get('owner', '')).strip()
            )
            vessels[vessel.vessel_id] = vessel
        
        return vessels
    
    def _load_voyage_configs(self) -> List[VoyageConfig]:
        """Загрузка конфигураций рейсов"""
        logger.info("\n Конфигурации рейсов...")
        configs = []
        
        df = self._read_csv('voyage_config.csv')
        if df is None:
            return configs
        
        for _, row in df.iterrows():
            # Парсим start_date (может быть пустым)
            start_date = None
            if pd.notna(row.get('start_date')) and str(row.get('start_date')).strip():
                start_date = self._parse_date(row['start_date'])
            
            config = VoyageConfig(
                voyage_id=str(row['voyage_id']).strip(),
                vessel_id=str(row['vessel_id']).strip(),
                seq=int(row['seq']),
                operation=str(row['operation']).strip().lower(),
                port=str(row['port']).strip(),
                cargo=str(row.get('cargo', '')).strip(),
                qty_mt=float(row.get('qty_mt', 0) or 0),
                start_date=start_date,
                remarks=str(row.get('remarks', '')).strip()
            )
            configs.append(config)
        
        # Сортируем по voyage_id и seq
        configs.sort(key=lambda x: (x.voyage_id, x.seq))
        
        # Считаем уникальные рейсы
        unique_voyages = len(set(c.voyage_id for c in configs))
        logger.info(f"     Уникальных рейсов: {unique_voyages}")
        
        return configs
    
    def _parse_date(self, value) -> Optional[date]:
        """Парсинг даты"""
        if pd.isna(value) or value is None:
            return None
        
        if isinstance(value, (datetime, date)):
            return value if isinstance(value, date) else value.date()
        
        value_str = str(value).strip()
        
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                return datetime.strptime(value_str, fmt).date()
            except:
                continue
        
        return None
    
    def _print_summary(self, data: OlyaData):
        """Сводка"""
        logger.info("\n" + "=" * 70)
        logger.info(" СВОДКА")
        logger.info("=" * 70)
        logger.info(f"  Порты:      {len(data.ports)}")
        logger.info(f"  Расстояния: {len(data.distances)}")
        logger.info(f"  Флот:       {len(data.vessels)} (барж: {len(data.barges)}, судов: {len(data.sea_vessels)})")
        logger.info(f"  Рейсов:     {len(set(c.voyage_id for c in data.voyage_configs))}")
        logger.info(f"  Операций:   {len(data.voyage_configs)}")