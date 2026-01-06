#!/usr/bin/env python3
"""
Balakovo Berth Planning
=======================

Планирование причала Балаково:
- Баржи с маслом → Olya
- Сухогрузы со шротом → Turkey

Использование:
    python main_balakovo.py
    python main_balakovo.py --input input/balakovo --output output/balakovo
"""

import argparse
import logging
import sys
from pathlib import Path

from modules.balakovo_loader import BalakovoLoader
from modules.balakovo_planner import BalakovoPlanner
from modules.balakovo_gantt import BalakovoGanttExcel


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    parser = argparse.ArgumentParser(description="Balakovo Berth Planning")
    parser.add_argument('--input', '-i', default='input/balakovo', help='Входная директория')
    parser.add_argument('--output', '-o', default='output/balakovo', help='Выходная директория')
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    logger.info("\n" + "=" * 60)
    logger.info(" BALAKOVO BERTH PLANNING")
    logger.info("   Баржи → Olya | Сухогрузы → Turkey")
    logger.info("=" * 60)
    
    # 1. Загрузка данных
    loader = BalakovoLoader(input_dir=args.input)
    data = loader.load()
    
    if not data.cargo_plans:
        logger.error(" Нет плана отгрузок!")
        return 1
    
    # 2. Планирование
    planner = BalakovoPlanner(data)
    data = planner.plan()
    
    # 3. Генерация отчётов
    gantt = BalakovoGanttExcel(data, args.output)
    gantt.generate_schedule()
    
    # 4. Экспорт CSV
    logger.info("\n Экспорт CSV...")
    
    # Расписание
    import pandas as pd
    
    slots_data = []
    for schedule in data.schedules.values():
        for slot in schedule.slots:
            slots_data.append({
                'slot_id': slot.slot_id,
                'berth_id': slot.berth_id,
                'vessel_id': slot.vessel_id,
                'vessel_name': slot.vessel_name,
                'cargo_id': slot.cargo_id,
                'cargo_type': slot.cargo_type,
                'qty_mt': slot.qty_mt,
                'destination': slot.destination,
                'eta': slot.eta,
                'berthing_start': slot.berthing_start,
                'loading_start': slot.loading_start,
                'loading_end': slot.loading_end,
                'departure': slot.departure,
                'waiting_hours': slot.waiting_hours,
                'loading_hours': slot.loading_hours,
                'status': slot.status.value
            })
    
    if slots_data:
        df = pd.DataFrame(slots_data)
        csv_path = Path(args.output) / "berth_schedule.csv"
        df.to_csv(csv_path, index=False, sep=';')
        logger.info(f"   {csv_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info(" ГОТОВО!")
    logger.info(f"   Результаты: {args.output}/")
    logger.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
