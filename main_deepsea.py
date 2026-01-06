#!/usr/bin/env python3
"""
Deep Sea Voyage Calculator
==========================

Автоматический расчёт рейсов по плечам

Использование:
    python main_deepsea.py
    python main_deepsea.py --input input/deepsea --output output/deepsea
"""

import argparse
import logging
import sys
from pathlib import Path

from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    parser = argparse.ArgumentParser(description="Deep Sea Voyage Calculator")
    parser.add_argument('--input', '-i', default='input/deepsea', help='Входная директория')
    parser.add_argument('--output', '-o', default='output/deepsea', help='Выходная директория')
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    logger.info("\n" + "=" * 70)
    logger.info(" DEEP SEA VOYAGE CALCULATOR")
    logger.info("=" * 70)
    
    # 1. Загрузка данных
    loader = DeepSeaLoader(input_dir=args.input)
    data = loader.load()
    
    if not data.voyage_plans:
        logger.error(" Нет планов рейсов!")
        return 1
    
    # 2. Расчёт рейсов
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    # 3. Экспорт
    logger.info("\n Экспорт результатов...")
    
    schedule_path = Path(args.output) / "schedule_calculated.csv"
    calculator.export_schedule_csv(str(schedule_path))
    
    summary_path = Path(args.output) / "voyage_summary.csv"
    calculator.export_summary_csv(str(summary_path))
    
    # 4. Итоговая статистика
    logger.info("\n" + "=" * 70)
    logger.info(" ИТОГОВАЯ СТАТИСТИКА")
    logger.info("=" * 70)
    
    total_cargo = sum(v.qty_mt for v in data.calculated_voyages.values())
    total_cost = sum(v.total_cost_usd for v in data.calculated_voyages.values())
    total_bunker = sum(v.total_bunker_cost_usd for v in data.calculated_voyages.values())
    total_hire = sum(v.hire_cost_usd for v in data.calculated_voyages.values())
    total_operational = sum(v.operational_cost_allocation for v in data.calculated_voyages.values())
    total_overhead = sum(v.overhead_cost_allocation for v in data.calculated_voyages.values())
    
    logger.info(f"  Рейсов:            {len(data.calculated_voyages)}")
    logger.info(f"  Груз:              {total_cargo:,.0f} MT")
    logger.info(f"  Затраты всего:     ${total_cost:,.0f}")
    logger.info(f"    - Аренда судов:  ${total_hire:,.0f}")
    logger.info(f"    - Бункер:        ${total_bunker:,.0f}")
    logger.info(f"    - Операц. расх.: ${total_operational:,.0f}")
    logger.info(f"    - Накладные:     ${total_overhead:,.0f}")
    
    logger.info("\n" + "=" * 70)
    logger.info(" ГОТОВО!")
    logger.info(f"   Результаты: {args.output}/")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())