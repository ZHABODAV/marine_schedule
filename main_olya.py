#!/usr/bin/env python3
"""
Olya Schedule & Coordination Tool
=================================

1. Загрузка конфигурации рейсов
2. Автоматический расчёт дат
3. Анализ стыковок
4. Генерация Gantt в Excel по месяцам

Использование:
    python main_olya.py
    python main_olya.py --input input/olya --output output/olya
"""

import argparse
import logging
import sys
from pathlib import Path

from modules.olya_loader import OlyaLoader
from modules.olya_calculator import OlyaVoyageCalculator
from modules.olya_coordinator import OlyaCoordinator
from modules.olya_gantt_excel import OlyaGanttExcel


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    parser = argparse.ArgumentParser(description="Olya Schedule Tool")
    parser.add_argument('--input', '-i', default='input/olya', help='Входная директория')
    parser.add_argument('--output', '-o', default='output/olya', help='Выходная директория')
    parser.add_argument('--no-gantt', action='store_true', help='Без Gantt')
    parser.add_argument('--no-analysis', action='store_true', help='Без анализа стыковок')
    
    args = parser.parse_args()
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    logger.info("\n" + "=" * 70)
    logger.info(" OLYA SCHEDULE & COORDINATION TOOL")
    logger.info("=" * 70)
    
    # 1. Загрузка данных
    loader = OlyaLoader(input_dir=args.input)
    data = loader.load()
    
    if not data.voyage_configs:
        logger.error(" Нет конфигураций рейсов!")
        return 1
    
    # 2. Расчёт расписания
    calculator = OlyaVoyageCalculator(data)
    data = calculator.calculate_all()
    
    # Экспорт рассчитанного расписания
    schedule_path = Path(args.output) / "schedule_calculated.csv"
    calculator.export_schedule_csv(str(schedule_path))
    
    # 3. Анализ стыковок
    if not args.no_analysis:
        coordinator = OlyaCoordinator(data)
        analysis = coordinator.analyze()
    
    # 4. Генерация Gantt
    if not args.no_gantt:
        gantt = OlyaGanttExcel(data, args.output)
        
        # По месяцам
        gantt.generate_all_months()
        
        # Сводный
        gantt.generate_summary_gantt()
    
    logger.info("\n" + "=" * 70)
    logger.info(" ГОТОВО!")
    logger.info(f"   Результаты: {args.output}/")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())