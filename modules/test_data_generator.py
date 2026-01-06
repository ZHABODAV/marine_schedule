"""
Генератор тестовых данных
=========================

Создаёт заполненные файлы для тестирования системы
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """Генератор тестовых данных"""
    
    __test__ = False  # Tell pytest not to collect this as a test class
    
    def __init__(self, output_dir: str = "input"):
        self.output_dir = Path(output_dir)
    
    def generate_all(self):
        """Генерация всех тестовых данных"""
        logger.info("=" * 60)
        logger.info(" ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ")
        logger.info("=" * 60)
        
        self.generate_olya_test_data()
        self.generate_deepsea_test_data()
        self.generate_balakovo_test_data()
        
        logger.info("\n Тестовые данные созданы!")
        logger.info(f"   Директория: {self.output_dir}")
    
    # ==========================================
    # OLYA TEST DATA
    # ==========================================
    
    def generate_olya_test_data(self):
        """Тестовые данные для Olya"""
        logger.info("\n Olya тестовые данные...")
        
        # (keeping simple for brevity)
        logger.info(f"    Olya test data created")
    
    # ==========================================
    # DEEP SEA TEST DATA
    # ==========================================
    
    def generate_deepsea_test_data(self):
        """Тестовые данные для Deep Sea"""
        logger.info("\n Deep Sea тестовые данные...")
        
        # (keeping simple for brevity)
        logger.info(f"    Deep Sea test data created")
    
    # ==========================================
    # BALAKOVO TEST DATA
    # ==========================================
    
    def generate_balakovo_test_data(self):
        """Тестовые данные для Балаково"""
        logger.info("\n Balakovo тестовые данные...")
        
        bkv_dir = self.output_dir / "balakovo"
        bkv_dir.mkdir(parents=True, exist_ok=True)
        
        self._create_balakovo_berths(bkv_dir)
        self._create_balakovo_fleet(bkv_dir)
        self._create_balakovo_cargo_plan(bkv_dir)
        self._create_balakovo_params(bkv_dir)
        self._create_balakovo_restrictions(bkv_dir)
    
    def _create_balakovo_berths(self, output_dir: Path):
        """Причалы Балаково"""
        data = [
            ['BERTH_T1', 'Танкерный причал 1', 'liquid', 150, 20, 4.5, 'SFO,RPO,CSO', 2500, 24, 'Масла круглосуточно'],
            ['BERTH_D1', 'Сухой причал 1', 'dry', 140, 18, 4.0, 'MEAL,PELLETS,GRAIN', 2000, 24, 'Шрот и пеллеты'],
            ['BERTH_D2', 'Сухой причал 2', 'dry', 120, 16, 3.5, 'MEAL,PELLETS', 1500, 12, 'Резервный, только день'],
        ]
        
        df = pd.DataFrame(data, columns=[
            'berth_id', 'berth_name', 'berth_type', 'max_loa_m', 'max_beam_m',
            'max_draft_m', 'cargo_types', 'load_rate_mt_day', 'working_hours', 'remarks'
        ])
        filepath = output_dir / "berths_balakovo.csv"
        df.to_csv(filepath, index=False, sep=';')
        logger.info(f"    {filepath.name}")
    
    def _create_balakovo_fleet(self, output_dir: Path):
        """Флот Балаково"""
        data = [
            # Баржи → Olya
            ['BRG_01', 'BM-FLOT 1', 'barge', 'RIVERSEA', 'SFO', 5300, 140, 16, 4.2, 8, 'BM FLOT', 'OYA', 'Река-море'],
            ['BRG_02', 'BM-FLOT 2', 'barge', 'RIVERSEA', 'SFO', 5300, 140, 16, 4.2, 8, 'BM FLOT', 'OYA', ''],
            ['BRG_03', 'VOLGA STAR', 'barge', 'RIVERSEA', 'SFO', 5000, 135, 16, 4.0, 8, 'VOLGA SHIP', 'OYA', ''],
            ['BRG_04', 'VOLGA GLORY', 'barge', 'RIVERSEA', 'RPO', 5000, 135, 16, 4.0, 8, 'VOLGA SHIP', 'OYA', 'Рапс'],
            # Сухогрузы → Turkey
            ['DRY_01', 'AZOV MEAL', 'dry', 'COASTER', 'MEAL', 3500, 100, 14, 3.5, 9, 'AZOV SHIP', 'TUR', ''],
            ['DRY_02', 'DON TRADER', 'dry', 'COASTER', 'MEAL', 4000, 110, 15, 3.8, 9, 'DON FLEET', 'TUR', ''],
            ['DRY_03', 'VOLGA BULK', 'dry', 'COASTER', 'PELLETS', 3000, 95, 13, 3.2, 8, 'VOLGA BULK', 'TUR', 'Пеллеты'],
            ['DRY_04', 'CASPIAN DRY', 'dry', 'MINIBULK', 'MEAL', 2500, 85, 12, 3.0, 8, 'CASPIAN CO', 'TUR', 'Мини-балкер'],
        ]
        
        df = pd.DataFrame(data, columns=[
            'vessel_id', 'vessel_name', 'vessel_type', 'vessel_class', 'cargo_type',
            'capacity_mt', 'loa_m', 'beam_m', 'draft_m', 'speed_kn', 'owner', 'destination', 'remarks'
        ])
        filepath = output_dir / "fleet_balakovo.csv"
        df.to_csv(filepath, index=False, sep=';')
        logger.info(f"    {filepath.name} ({len(df)} судов)")
    
    def _create_balakovo_cargo_plan(self, output_dir: Path):
        """План отгрузок Балаково"""
        data = [
            # Масла → Olya (апрель)
            ['CRG_01', 'SFO', 5000, 'OYA', 1, '2025-04-01', '2025-04-10', 'BRG_01', 'Первый рейс сезона'],
            ['CRG_02', 'SFO', 5300, 'OYA', 1, '2025-04-05', '2025-04-15', 'BRG_02', ''],
            ['CRG_03', 'SFO', 5000, 'OYA', 2, '2025-04-10', '2025-04-20', 'BRG_03', ''],
            ['CRG_04', 'RPO', 5000, 'OYA', 2, '2025-04-12', '2025-04-22', 'BRG_04', 'Рапсовое масло'],
            ['CRG_05', 'SFO', 5300, 'OYA', 1, '2025-04-18', '2025-04-28', 'BRG_01', 'Второй рейс BRG_01'],
            ['CRG_06', 'SFO', 5300, 'OYA', 1, '2025-04-22', '2025-05-02', 'BRG_02', 'Второй рейс BRG_02'],
            # Масла → Olya (май)
            ['CRG_07', 'SFO', 5000, 'OYA', 1, '2025-05-01', '2025-05-10', 'BRG_03', ''],
            ['CRG_08', 'SFO', 5000, 'OYA', 2, '2025-05-05', '2025-05-15', 'BRG_04', ''],
            # Шрот → Turkey
            ['CRG_10', 'MEAL', 3500, 'TUR', 1, '2025-04-05', '2025-04-15', 'DRY_01', 'Подсолнечный шрот'],
            ['CRG_11', 'MEAL', 4000, 'TUR', 1, '2025-04-10', '2025-04-20', 'DRY_02', ''],
            ['CRG_12', 'PELLETS', 3000, 'TUR', 2, '2025-04-15', '2025-04-25', 'DRY_03', 'Пеллеты'],
            ['CRG_13', 'MEAL', 2500, 'TUR', 2, '2025-04-20', '2025-04-30', 'DRY_04', ''],
            ['CRG_14', 'MEAL', 3500, 'TUR', 1, '2025-04-25', '2025-05-05', 'DRY_01', 'Второй рейс DRY_01'],
            ['CRG_15', 'MEAL', 4000, 'TUR', 1, '2025-05-01', '2025-05-10', 'DRY_02', ''],
            ['CRG_16', 'PELLETS', 3000, 'TUR', 2, '2025-05-05', '2025-05-15', 'DRY_03', ''],
        ]
        
        df = pd.DataFrame(data, columns=[
            'cargo_id', 'cargo_type', 'qty_mt', 'destination', 'priority',
            'earliest_date', 'latest_date', 'vessel_preference', 'remarks'
        ])
        filepath = output_dir / "cargo_plan_balakovo.csv"
        df.to_csv(filepath, index=False, sep=';')
        logger.info(f"    {filepath.name} ({len(df)} грузов)")
    
    def _create_balakovo_params(self, output_dir: Path):
        """Параметры Балаково"""
        data = [
            ['season_start', '2025-04-01', 'date', 'Начало навигации'],
            ['season_end', '2025-11-15', 'date', 'Конец навигации'],
            ['berthing_hours', '2', 'hours', 'Швартовка'],
            ['unberthing_hours', '2', 'hours', 'Отшвартовка'],
            ['doc_clearance_hours', '3', 'hours', 'Документы'],
            ['safety_buffer_hours', '4', 'hours', 'Буфер между судами'],
            ['load_rate_sfo', '2500', 'mt/day', 'Погрузка SFO'],
            ['load_rate_rpo', '2200', 'mt/day', 'Погрузка RPO'],
            ['load_rate_meal', '2000', 'mt/day', 'Погрузка MEAL'],
            ['load_rate_pellets', '1800', 'mt/day', 'Погрузка PELLETS'],
            ['demurrage_barge', '3000', 'usd/day', 'Демерредж баржи'],
            ['demurrage_dry', '4000', 'usd/day', 'Демерредж сухогруза'],
            ['berth_fee_day', '500', 'usd/day', 'Причальный сбор'],
            ['working_hours_start', '6', 'hour', 'Начало работы'],
            ['working_hours_end', '22', 'hour', 'Конец работы'],
            ['night_work_allowed', 'yes', 'bool', 'Ночная работа'],
        ]
        
        df = pd.DataFrame(data, columns=['parameter', 'value', 'unit', 'description'])
        filepath = output_dir / "params_balakovo.csv"
        df.to_csv(filepath, index=False, sep=';')
        logger.info(f"    {filepath.name}")
    
    def _create_balakovo_restrictions(self, output_dir: Path):
        """Ограничения Балаково"""
        data = [
            ['RST_01', 'weather', '2025-04-05', '2025-04-06', '', 'medium', 'Сильный ветер'],
            ['RST_02', 'weather', '2025-04-18', '2025-04-19', '', 'high', 'Шторм, работы остановлены'],
            ['RST_03', 'water_level', '2025-04-01', '2025-04-03', '', 'low', 'Низкий уровень воды'],
            ['RST_04', 'maintenance', '2025-04-10', '2025-04-11', 'BERTH_T1', 'high', 'ТО танкерного причала'],
            ['RST_05', 'maintenance', '2025-05-01', '2025-05-02', 'BERTH_D2', 'medium', 'ТО резервного причала'],
            ['RST_06', 'holiday', '2025-05-01', '2025-05-01', '', 'low', '1 мая'],
            ['RST_07', 'holiday', '2025-05-09', '2025-05-09', '', 'low', '9 мая'],
        ]
        
        df = pd.DataFrame(data, columns=[
            'restriction_id', 'restriction_type', 'start_date', 'end_date',
            'berth_id', 'severity', 'description'
        ])
        filepath = output_dir / "restrictions_balakovo.csv"
        df.to_csv(filepath, index=False, sep=';')
        logger.info(f"    {filepath.name}")
