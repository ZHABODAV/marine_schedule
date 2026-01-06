"""
CSV Template Generator
======================

Creates empty templates for user input
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """CSV Template Generator"""
    
    def __init__(self, output_dir: str = "templates"):
        self.output_dir = Path(output_dir)
    
    def generate_all(self):
        """Generate all templates"""
        logger.info("=" * 60)
        logger.info("TEMPLATE GENERATION")
        logger.info("=" * 60)
        
        # Olya
        self.generate_olya_templates()
        
        # Deep Sea
        self.generate_deepsea_templates()
        
        # Balakovo
        self.generate_balakovo_templates()
        
        logger.info("\n Templates created!")
        logger.info(f"   Directory: {self.output_dir}")
    
    # ==========================================
    # OLYA TEMPLATES
    # ===========================================
    
    def generate_olya_templates(self):
        """Generate templates for Olya operations"""
        logger.info("\n Olya templates...")
        
        olya_dir = self.output_dir / "olya"
        olya_dir.mkdir(parents=True, exist_ok=True)
        
        self._generate_olya_vessels(olya_dir)
        self._generate_olya_cargo(olya_dir)
        self._generate_olya_routes(olya_dir)
        
        logger.info(f"    Olya templates created")
    
    def _generate_olya_vessels(self, output_dir: Path):
        """Template for Olya vessels"""
        columns = [
            'vessel_id', 'vessel_name', 'vessel_type', 'capacity_mt',
            'loa_m', 'beam_m', 'draft_m', 'speed_kn', 'owner', 'remarks'
        ]
        
        comments = """# ================================================
# OLYA VESSELS - River-sea vessels
# ================================================
# vessel_id    - Vessel ID (OLY_01, OLY_02...)
# vessel_name  - Vessel name
# vessel_type  - Type: river-sea, tanker, barge
# capacity_mt  - Cargo capacity (MT)
# loa_m        - Length overall (m)
# beam_m       - Beam (m)
# draft_m      - Draft (m)
# speed_kn     - Speed (knots)
# owner        - Vessel owner
# remarks      - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "vessels_olya.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_olya_cargo(self, output_dir: Path):
        """Template for Olya cargo"""
        columns = [
            'cargo_id', 'cargo_type', 'qty_mt', 'load_port', 'disch_port',
            'earliest_date', 'latest_date', 'priority', 'remarks'
        ]
        
        comments = """# ================================================
# OLYA CARGO - Cargo movements
# ================================================
# cargo_id     - Cargo ID (CARG_01, CARG_02...)
# cargo_type   - Product type (SFO, RPO, CSO)
# qty_mt       - Quantity (MT)
# load_port    - Loading port
# disch_port   - Discharge port
# earliest_date - Laycan start (YYYY-MM-DD)
# latest_date  - Laycan end (YYYY-MM-DD)
# priority     - Priority: 1 (high) - 3 (low)
# remarks      - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "cargo_olya.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_olya_routes(self, output_dir: Path):
        """Template for Olya routes"""
        columns = [
            'route_id', 'from_port', 'to_port', 'distance_km', 'transit_time_hours', 'remarks'
        ]
        
        comments = """# ================================================
# OLYA ROUTES - River routes
# ================================================
# route_id    - Route ID (RT_01, RT_02...)
# from_port   - Origin port
# to_port     - Destination port
# distance_km - Distance (kilometers)
# transit_time_hours - Typical transit time (hours)
# remarks     - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "routes_olya.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    # ==========================================
    # DEEP SEA TEMPLATES
    # ==========================================
    
    def generate_deepsea_templates(self):
        """Generate templates for Deep Sea operations"""
        logger.info("\n Deep Sea templates...")
        
        ds_dir = self.output_dir / "deepsea"
        ds_dir.mkdir(parents=True, exist_ok=True)
        
        self._generate_deepsea_vessels(ds_dir)
        self._generate_deepsea_cargo(ds_dir)
        self._generate_deepsea_ports(ds_dir)
        self._generate_deepsea_routes(ds_dir)
        
        logger.info(f"    Deep Sea templates created")
    
    def _generate_deepsea_vessels(self, output_dir: Path):
        """Template for Deep Sea vessels"""
        columns = [
            'vessel_id', 'vessel_name', 'imo', 'vessel_type', 'vessel_class', 'dwt_mt',
            'capacity_mt', 'loa_m', 'beam_m', 'draft_laden_m', 'draft_ballast_m',
            'speed_laden_kn', 'speed_ballast_kn', 'owner', 'flag', 'built_year', 'remarks'
        ]
        
        comments = """# ================================================
# DEEP SEA VESSELS - Ocean-going vessels
# ================================================
# vessel_id        - Vessel ID (DS_01, DS_02...)
# vessel_name      - Vessel name
# imo              - IMO number
# vessel_type      - Type: tanker, bulker, container
# vessel_class     - Class: MR2, MR1, Handysize, Panamax, etc.
# dwt_mt           - Deadweight tonnage (MT)
# capacity_mt      - Cargo capacity (MT)
# loa_m            - Length overall (m)
# beam_m           - Beam (m)
# draft_laden_m    - Laden draft (m)
# draft_ballast_m  - Ballast draft (m)
# speed_laden_kn   - Laden speed (knots)
# speed_ballast_kn - Ballast speed (knots)
# owner            - Vessel owner
# flag             - Flag state
# built_year       - Build year
# remarks          - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "vessels_deepsea.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_deepsea_cargo(self, output_dir: Path):
        """Template for Deep Sea cargo"""
        columns = [
            'cargo_id', 'commodity', 'qty_mt', 'load_port', 'disch_port',
            'laycan_start', 'laycan_end', 'charterer', 'freight_rate_mt', 'remarks'
        ]
        
        comments = """# ================================================
# DEEP SEA CARGO - Cargo fixtures
# ================================================
# cargo_id       - Cargo ID (CRG_01, CRG_02...)
# commodity      - Product: Grain, Coal, Iron ore, etc.
# qty_mt         - Quantity (MT)
# load_port      - Loading port
# disch_port     - Discharge port
# laycan_start   - Laycan start (YYYY-MM-DD)
# laycan_end     - Laycan end (YYYY-MM-DD)
# charterer      - Charterer name
# freight_rate_mt - Freight rate (USD/MT)
# remarks        - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "cargo_deepsea.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_deepsea_ports(self, output_dir: Path):
        """Template for Deep Sea ports"""
        columns = [
            'port_id', 'port_name', 'country', 'region', 'latitude', 'longitude',
            'port_type', 'max_draft_m', 'load_rate_mt_day', 'disch_rate_mt_day',
            'port_charges_usd', 'remarks'
        ]
        
        comments = """# ================================================
# DEEP SEA PORTS - Port specifications
# ================================================
# port_id          - Port ID (PRT_01, PRT_02...)
# port_name        - Port name
# country          - Country
# region           - Region (e.g., Med, Far East, AG)
# latitude         - Latitude
# longitude        - Longitude
# port_type        - Type: load, discharge, transit, bunker
# max_draft_m      - Maximum draft (m)
# load_rate_mt_day - Loading rate (MT/day)
# disch_rate_mt_day - Discharge rate (MT/day)
# port_charges_usd - Port charges (USD)
# remarks          - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "ports_deepsea.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_deepsea_routes(self, output_dir: Path):
        """Template for Deep Sea routes"""
        columns = [
            'from_port', 'to_port', 'distance_nm', 'canal', 'remarks'
        ]
        
        comments = """# ================================================
# DEEP SEA ROUTES - Port-to-port distances
# ================================================
# from_port    - Origin port
# to_port      - Destination port
# distance_nm  - Distance (nautical miles)
# canal        - Canal name (Suez, Panama) or leave empty
# remarks      - Notes
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "routes_deepsea.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    # ==========================================
    # BALAKOVO TEMPLATES
    # ==========================================
    
    def generate_balakovo_templates(self):
        """Generate templates for Balakovo operations"""
        logger.info("\n Balakovo templates...")
        
        bkv_dir = self.output_dir / "balakovo"
        bkv_dir.mkdir(parents=True, exist_ok=True)
        
        self._generate_balakovo_berths(bkv_dir)
        self._generate_balakovo_fleet(bkv_dir)
        self._generate_balakovo_cargo_plan(bkv_dir)
        self._generate_balakovo_params(bkv_dir)
        self._generate_balakovo_restrictions(bkv_dir)
    
    def _generate_balakovo_berths(self, output_dir: Path):
        """Template for Balakovo berths"""
        columns = [
            'berth_id', 'berth_name', 'berth_type', 'max_loa_m', 'max_beam_m',
            'max_draft_m', 'cargo_types', 'load_rate_mt_day', 'working_hours', 'remarks'
        ]
        
        comments = """# ================================================
# BALAKOVO BERTHS - Причалы
# ================================================
# berth_id        - ID причала (BERTH_T1, BERTH_D1...)
# berth_name      - Название
# berth_type      - Тип: liquid (танкерный) или dry (сухой)
# max_loa_m       - Макс. длина судна (м)
# max_beam_m      - Макс. ширина судна (м)
# max_draft_m     - Макс. осадка (м)
# cargo_types     - Типы грузов через запятую (SFO,RPO,MEAL,PELLETS)
# load_rate_mt_day - Норма погрузки (MT/день)
# working_hours   - Режим работы: 24 (круглосуточно) или 12 (дневной)
# remarks         - Примечания
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "berths_balakovo.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_balakovo_fleet(self, output_dir: Path):
        """Template for Balakovo fleet"""
        columns = [
            'vessel_id', 'vessel_name', 'vessel_type', 'vessel_class', 'cargo_type',
            'capacity_mt', 'loa_m', 'beam_m', 'draft_m', 'speed_kn',
            'owner', 'destination', 'remarks'
        ]
        
        comments = """# ================================================
# BALAKOVO FLEET - Флот для погрузки
# ================================================
# vessel_id    - ID судна (BRG_01, DRY_01...)
# vessel_name  - Название
# vessel_type  - Тип: barge (баржа) или dry (сухогруз)
# vessel_class - Класс: RIVERSEA, COASTER, MINIBULK...
# cargo_type   - Основной груз: SFO, RPO, MEAL, PELLETS
# capacity_mt  - Грузоподъёмность (MT)
# loa_m        - Длина (м)
# beam_m       - Ширина (м)
# draft_m      - Осадка (м)
# speed_kn     - Скорость (узлов)
# owner        - Владелец
# destination  - Направление: OYA (Olya) или TUR (Turkey)
# remarks      - Примечания
# ================================================
# БАРЖИ: везут масло в Olya для перегрузки на морские суда
# СУХОГРУЗЫ: везут шрот/пеллеты напрямую в Турцию
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "fleet_balakovo.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_balakovo_cargo_plan(self, output_dir: Path):
        """Шаблон плана отгрузок"""
        columns = [
            'cargo_id', 'cargo_type', 'qty_mt', 'destination', 'priority',
            'earliest_date', 'latest_date', 'vessel_preference', 'remarks'
        ]
        
        comments = """# ================================================
# BALAKOVO CARGO PLAN - План отгрузок
# ================================================
# cargo_id         - ID груза (CRG_01, CRG_02...)
# cargo_type       - Тип: SFO, RPO, CSO (масла) или MEAL, PELLETS (сухие)
# qty_mt           - Количество (MT)
# destination      - Направление: OYA (→Olya→Иран) или TUR (→Турция)
# priority         - Приоритет: 1 (высший) - 3 (низкий)
# earliest_date    - Начало окна погрузки (YYYY-MM-DD)
# latest_date      - Конец окна погрузки (YYYY-MM-DD)
# vessel_preference - Предпочтительное судно (опционально)
# remarks          - Примечания
# ================================================
# ВАЖНО: 
# - Масла (SFO/RPO) идут на танкерный причал → баржами в Olya
# - Сухие (MEAL/PELLETS) идут на сухой причал → сухогрузами в Турцию
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "cargo_plan_balakovo.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_balakovo_params(self, output_dir: Path):
        """Шаблон параметров"""
        data = [
            ['season_start', '2025-04-01', 'date', 'Начало навигации'],
            ['season_end', '2025-11-15', 'date', 'Конец навигации'],
            ['berthing_hours', '2', 'hours', 'Время швартовки'],
            ['unberthing_hours', '2', 'hours', 'Время отшвартовки'],
            ['doc_clearance_hours', '3', 'hours', 'Оформление документов'],
            ['safety_buffer_hours', '4', 'hours', 'Буфер между судами'],
            ['load_rate_sfo', '2500', 'mt/day', 'Норма погрузки SFO'],
            ['load_rate_rpo', '2200', 'mt/day', 'Норма погрузки RPO'],
            ['load_rate_meal', '2000', 'mt/day', 'Норма погрузки MEAL'],
            ['load_rate_pellets', '1800', 'mt/day', 'Норма погрузки PELLETS'],
            ['demurrage_barge', '3000', 'usd/day', 'Демерредж баржи'],
            ['demurrage_dry', '4000', 'usd/day', 'Демерредж сухогруза'],
            ['berth_fee_day', '500', 'usd/day', 'Причальный сбор'],
            ['working_hours_start', '6', 'hour', 'Начало рабочего дня'],
            ['working_hours_end', '22', 'hour', 'Конец рабочего дня'],
            ['night_work_allowed', 'yes', 'bool', 'Разрешена ночная работа'],
        ]
        
        comments = """# ================================================
# BALAKOVO PARAMETERS - Параметры
# ================================================
"""
        
        df = pd.DataFrame(data, columns=['parameter', 'value', 'unit', 'description'])
        filepath = output_dir / "params_balakovo.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
    
    def _generate_balakovo_restrictions(self, output_dir: Path):
        """Шаблон ограничений"""
        columns = [
            'restriction_id', 'restriction_type', 'start_date', 'end_date',
            'berth_id', 'severity', 'description'
        ]
        
        comments = """# ================================================
# BALAKOVO RESTRICTIONS - Ограничения работы
# ================================================
# restriction_id   - ID ограничения (RST_01, RST_02...)
# restriction_type - Тип: weather, water_level, maintenance, holiday
# start_date       - Начало (YYYY-MM-DD)
# end_date         - Конец (YYYY-MM-DD)
# berth_id         - ID причала (пусто = все причалы)
# severity         - Серьёзность: low, medium, high (high = работы остановлены)
# description      - Описание
# ================================================
# ТИПЫ ОГРАНИЧЕНИЙ:
# - weather: погода (ветер, шторм)
# - water_level: уровень воды (низкий/высокий)
# - maintenance: техническое обслуживание причала
# - holiday: праздники (сокращённый день)
# ================================================
"""
        
        df = pd.DataFrame(columns=columns)
        filepath = output_dir / "restrictions_balakovo.csv"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comments)
            df.to_csv(f, index=False, sep=';')
        
        logger.info(f"    {filepath.name}")
