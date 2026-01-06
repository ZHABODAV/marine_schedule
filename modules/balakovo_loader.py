"""
Загрузчик данных Балаково
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Set
import logging

from modules.balakovo_data import (
    BalakovoData, BalakovoParams, Berth, BalakovoVessel,
    CargoPlan, Restriction
)

logger = logging.getLogger(__name__)


class BalakovoLoader:
    """Загрузчик CSV для Балаково"""
    
    def __init__(self, input_dir: str = "input/balakovo"):
        self.input_dir = Path(input_dir)
    
    def load(self) -> BalakovoData:
        """Загрузить все данные"""
        logger.info("=" * 60)
        logger.info(" ЗАГРУЗКА ДАННЫХ БАЛАКОВО")
        logger.info(f"   Директория: {self.input_dir}")
        logger.info("=" * 60)
        
        data = BalakovoData()
        
        data.params = self._load_params()
        data.berths = self._load_berths()
        data.vessels = self._load_fleet()
        data.cargo_plans = self._load_cargo_plans()
        data.restrictions = self._load_restrictions()
        
        self._validate(data)
        self._print_summary(data)
        
        return data
    
    def _read_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """Чтение CSV"""
        filepath = self.input_dir / filename
        if not filepath.exists():
            logger.warning(f"   Файл не найден: {filepath}")
            return None
        
        try:
            df = pd.read_csv(filepath, delimiter=';', comment='#', encoding='utf-8')
            logger.info(f"   {filename}: {len(df)} записей")
            return df
        except Exception as e:
            logger.error(f"   Ошибка: {e}")
            return None
    
    def _load_params(self) -> BalakovoParams:
        """Загрузка параметров"""
        logger.info("\n Параметры...")
        params = BalakovoParams()
        
        df = self._read_csv('params_balakovo.csv')
        if df is None:
            return params
        
        param_dict = dict(zip(df['parameter'], df['value']))
        
        # Даты
        if 'season_start' in param_dict:
            params.season_start = self._parse_date(param_dict['season_start'])
        if 'season_end' in param_dict:
            params.season_end = self._parse_date(param_dict['season_end'])
        
        # Числовые параметры
        float_params = [
            'berthing_hours', 'unberthing_hours', 'doc_clearance_hours', 'safety_buffer_hours',
            'load_rate_sfo', 'load_rate_rpo', 'load_rate_meal', 'load_rate_pellets',
            'demurrage_barge', 'demurrage_dry', 'berth_fee_day'
        ]
        for p in float_params:
            if p in param_dict:
                try:
                    setattr(params, p, float(param_dict[p]))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not set parameter {p}: {e}")
        
        # Целые
        if 'working_hours_start' in param_dict:
            params.working_hours_start = int(param_dict['working_hours_start'])
        if 'working_hours_end' in param_dict:
            params.working_hours_end = int(param_dict['working_hours_end'])
        
        # Boolean
        if 'night_work_allowed' in param_dict:
            params.night_work_allowed = str(param_dict['night_work_allowed']).lower() == 'yes'
        
        return params
    
    def _load_berths(self) -> Dict[str, Berth]:
        """Загрузка причалов"""
        logger.info("\n Причалы...")
        berths = {}
        
        df = self._read_csv('berths_balakovo.csv')
        if df is None:
            return berths
        
        for _, row in df.iterrows():
            cargo_types_str = str(row.get('cargo_types', '')).strip()
            cargo_types = set(ct.strip().upper() for ct in cargo_types_str.split(',') if ct.strip())
            
            berth = Berth(
                berth_id=str(row['berth_id']).strip(),
                berth_name=str(row['berth_name']).strip(),
                berth_type=str(row['berth_type']).strip().lower(),
                max_loa_m=float(row['max_loa_m']),
                max_beam_m=float(row['max_beam_m']),
                max_draft_m=float(row['max_draft_m']),
                cargo_types=cargo_types,
                load_rate_mt_day=float(row.get('load_rate_mt_day', 2000)),
                working_hours=int(row.get('working_hours', 24)),
                remarks=str(row.get('remarks', '')).strip()
            )
            berths[berth.berth_id] = berth
        
        return berths
    
    def _load_fleet(self) -> Dict[str, BalakovoVessel]:
        """Загрузка флота"""
        logger.info("\n Флот...")
        vessels = {}
        
        df = self._read_csv('fleet_balakovo.csv')
        if df is None:
            return vessels
        
        for _, row in df.iterrows():
            vessel = BalakovoVessel(
                vessel_id=str(row['vessel_id']).strip(),
                vessel_name=str(row['vessel_name']).strip(),
                vessel_type=str(row['vessel_type']).strip().lower(),
                vessel_class=str(row['vessel_class']).strip(),
                cargo_type=str(row['cargo_type']).strip().upper(),
                capacity_mt=float(row['capacity_mt']),
                loa_m=float(row['loa_m']),
                beam_m=float(row['beam_m']),
                draft_m=float(row['draft_m']),
                speed_kn=float(row['speed_kn']),
                owner=str(row.get('owner', '')).strip(),
                destination=str(row['destination']).strip().upper(),
                remarks=str(row.get('remarks', '')).strip()
            )
            vessels[vessel.vessel_id] = vessel
        
        barges = sum(1 for v in vessels.values() if v.is_barge)
        dry = sum(1 for v in vessels.values() if v.is_dry)
        logger.info(f"     Баржи → Olya: {barges}")
        logger.info(f"     Сухогрузы → Turkey: {dry}")
        
        return vessels
    
    def _load_cargo_plans(self) -> List[CargoPlan]:
        """Загрузка планов отгрузки"""
        logger.info("\n План отгрузок...")
        plans = []
        
        df = self._read_csv('cargo_plan_balakovo.csv')
        if df is None:
            return plans
        
        for _, row in df.iterrows():
            earliest = self._parse_date(row.get('earliest_date'))
            latest = self._parse_date(row.get('latest_date'))
            
            if earliest is None:
                continue
            if latest is None:
                latest = earliest + timedelta(days=10)
            
            vessel_pref = row.get('vessel_preference')
            if pd.isna(vessel_pref) or str(vessel_pref).strip() == '':
                vessel_pref = None
            else:
                vessel_pref = str(vessel_pref).strip()
            
            plan = CargoPlan(
                cargo_id=str(row['cargo_id']).strip(),
                cargo_type=str(row['cargo_type']).strip().upper(),
                qty_mt=float(row['qty_mt']),
                destination=str(row['destination']).strip().upper(),
                priority=int(row.get('priority', 2)),
                earliest_date=earliest,
                latest_date=latest,
                vessel_preference=vessel_pref,
                remarks=str(row.get('remarks', '')).strip()
            )
            plans.append(plan)
        
        # Сортируем по приоритету и дате
        plans.sort(key=lambda x: (x.priority, x.earliest_date))
        
        oil_qty = sum(p.qty_mt for p in plans if p.is_oil)
        dry_qty = sum(p.qty_mt for p in plans if p.is_dry)
        logger.info(f"     Масла → Olya: {oil_qty:,.0f} MT")
        logger.info(f"     Шрот → Turkey: {dry_qty:,.0f} MT")
        
        return plans
    
    def _load_restrictions(self) -> List[Restriction]:
        """Загрузка ограничений"""
        logger.info("\n Ограничения...")
        restrictions = []
        
        df = self._read_csv('restrictions_balakovo.csv')
        if df is None:
            return restrictions
        
        for _, row in df.iterrows():
            start = self._parse_date(row.get('start_date'))
            end = self._parse_date(row.get('end_date'))
            
            if start is None or end is None:
                continue
            
            berth_id = row.get('berth_id')
            if pd.isna(berth_id) or str(berth_id).strip() == '':
                berth_id = None
            else:
                berth_id = str(berth_id).strip()
            
            restriction = Restriction(
                restriction_id=str(row['restriction_id']).strip(),
                restriction_type=str(row['restriction_type']).strip().lower(),
                start_date=start,
                end_date=end,
                berth_id=berth_id,
                severity=str(row.get('severity', 'medium')).strip().lower(),
                description=str(row.get('description', '')).strip()
            )
            restrictions.append(restriction)
        
        return restrictions
    
    def _parse_date(self, value) -> Optional[date]:
        """Парсинг даты"""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, (datetime, date)):
            return value if isinstance(value, date) else value.date()
        
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except:
                continue
        return None
    
    def _validate(self, data: BalakovoData):
        """Валидация данных"""
        logger.info("\n Валидация...")
        
        errors = []
        
        # Проверяем что суда помещаются на причалы
        for plan in data.cargo_plans:
            vessel_id = plan.vessel_preference
            if vessel_id and vessel_id in data.vessels:
                vessel = data.vessels[vessel_id]
                
                # Находим подходящий причал
                suitable_berths = []
                for berth in data.berths.values():
                    if berth.can_handle_vessel(vessel) and berth.can_handle_cargo(plan.cargo_type):
                        suitable_berths.append(berth)
                
                if not suitable_berths:
                    errors.append(f"Груз {plan.cargo_id}: нет подходящего причала для {vessel_id}")
        
        if errors:
            for e in errors:
                logger.warning(f"   {e}")
        else:
            logger.info("   Валидация пройдена")
    
    def _print_summary(self, data: BalakovoData):
        """Сводка"""
        logger.info("\n" + "=" * 60)
        logger.info(" СВОДКА БАЛАКОВО")
        logger.info("=" * 60)
        logger.info(f"  Причалы:    {len(data.berths)} (жидкие: {len(data.liquid_berths)}, сухие: {len(data.dry_berths)})")
        logger.info(f"  Флот:       {len(data.vessels)} (баржи: {len(data.barges)}, сухогрузы: {len(data.dry_vessels)})")
        logger.info(f"  Отгрузки:   {len(data.cargo_plans)}")
        logger.info(f"  Ограничения:{len(data.restrictions)}")
        if data.params.season_start and data.params.season_end:
            logger.info(f"  Навигация:  {data.params.season_start} - {data.params.season_end}")
