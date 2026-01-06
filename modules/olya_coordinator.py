"""
Координатор стыковки в Olya
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import logging

from modules.olya_data import OlyaData, CalculatedOperation, CalculatedVoyage

logger = logging.getLogger(__name__)


@dataclass
class Match:
    """Стыковка баржа → судно"""
    barge_discharge: CalculatedOperation
    vessel_loading: CalculatedOperation
    barge_name: str
    vessel_name: str
    gap_hours: float
    status: str
    demurrage_cost: float = 0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class OlyaAnalysis:
    """Результат анализа"""
    matches: List[Match] = field(default_factory=list)
    unmatched_barges: List[CalculatedOperation] = field(default_factory=list)
    unmatched_vessels: List[CalculatedOperation] = field(default_factory=list)
    total_waiting_hours: float = 0
    total_demurrage: float = 0
    potential_savings: float = 0


class OlyaCoordinator:
    """Координатор стыковки"""
    
    def __init__(self, data: OlyaData):
        self.data = data
        self.params = data.params
    
    def analyze(self) -> OlyaAnalysis:
        """Анализ стыковок"""
        logger.info("\n" + "=" * 70)
        logger.info(" АНАЛИЗ СТЫКОВКИ В OLYA")
        logger.info("=" * 70)
        
        analysis = OlyaAnalysis()
        
        # Находим разгрузки барж и загрузки судов в Olya
        barge_discharges = []
        vessel_loadings = []
        
        for op in self.data.calculated_operations:
            if not op.is_at_olya:
                continue
            
            vessel = self.data.get_vessel(op.vessel_id)
            if not vessel:
                continue
            
            if op.operation == 'discharge' and vessel.is_barge:
                barge_discharges.append(op)
            elif op.operation == 'loading' and vessel.is_vessel:
                vessel_loadings.append(op)
        
        logger.info(f"  Разгрузок барж: {len(barge_discharges)}")
        logger.info(f"  Загрузок судов: {len(vessel_loadings)}")
        
        # Сортируем по времени
        barge_discharges.sort(key=lambda x: x.end_time)
        vessel_loadings.sort(key=lambda x: x.start_time)
        
        # Строим стыковки
        used_barges = set()
        
        for vessel_load in vessel_loadings:
            vessel = self.data.get_vessel(vessel_load.vessel_id)
            best_match = None
            best_gap = float('inf')
            
            for barge_disch in barge_discharges:
                if barge_disch.voyage_id in used_barges:
                    continue
                
                # Проверка груза
                if vessel_load.cargo and barge_disch.cargo:
                    if vessel_load.cargo != barge_disch.cargo:
                        continue
                
                gap = (vessel_load.start_time - barge_disch.end_time).total_seconds() / 3600
                
                if abs(gap) < abs(best_gap):
                    best_gap = gap
                    best_match = barge_disch
            
            if best_match:
                barge = self.data.get_vessel(best_match.vessel_id)
                
                # Статус
                if best_gap < -self.params.port_turnaround:
                    status = 'OVERLAP'
                elif best_gap < self.params.ideal_buffer:
                    status = 'TIGHT'
                elif best_gap <= 24:
                    status = 'OK'
                else:
                    status = 'LONG_WAIT'
                
                # Демерредж
                demurrage = 0
                if best_gap > self.params.ideal_buffer:
                    wait_days = (best_gap - self.params.ideal_buffer) / 24
                    demurrage = wait_days * self.params.demurrage_vessel
                
                match = Match(
                    barge_discharge=best_match,
                    vessel_loading=vessel_load,
                    barge_name=barge.vessel_name if barge else best_match.vessel_id,
                    vessel_name=vessel.vessel_name if vessel else vessel_load.vessel_id,
                    gap_hours=best_gap,
                    status=status,
                    demurrage_cost=demurrage
                )
                
                # Рекомендации
                self._add_recommendations(match)
                
                analysis.matches.append(match)
                used_barges.add(best_match.voyage_id)
                analysis.total_demurrage += demurrage
            else:
                analysis.unmatched_vessels.append(vessel_load)
        
        # Несостыкованные баржи
        for barge_disch in barge_discharges:
            if barge_disch.voyage_id not in used_barges:
                analysis.unmatched_barges.append(barge_disch)
        
        # Считаем ожидания
        for op in self.data.calculated_operations:
            if op.operation == 'waiting':
                analysis.total_waiting_hours += op.duration_hours
                analysis.potential_savings += op.duration_hours
        
        # Отчёт
        self._print_report(analysis)
        
        return analysis
    
    def _add_recommendations(self, match: Match):
        """Добавление рекомендаций"""
        recs = []
        
        if match.status == 'OVERLAP':
            delay = abs(match.gap_hours) + self.params.ideal_buffer
            recs.append(f" Сдвинуть {match.vessel_name} на +{delay:.0f}ч")
        
        elif match.status == 'LONG_WAIT':
            recs.append(f" Демерредж ${match.demurrage_cost:,.0f}")
            recs.append(f"   → Судно может прибыть позже на {match.gap_hours - 6:.0f}ч")
        
        elif match.status == 'TIGHT':
            recs.append(f" Мало буфера ({match.gap_hours:.1f}ч)")
        
        elif match.status == 'OK':
            recs.append(f" OK (буфер {match.gap_hours:.0f}ч)")
        
        match.recommendations = recs
    
    def _print_report(self, analysis: OlyaAnalysis):
        """Печать отчёта"""
        logger.info("\n" + "-" * 70)
        logger.info("СТЫКОВКИ:")
        logger.info("-" * 70)
        
        for match in analysis.matches:
            icon = {'OK': '', 'TIGHT': '', 'LONG_WAIT': '', 'OVERLAP': ''}.get(match.status, '?')
            
            logger.info(f"\n{icon} {match.barge_name} → {match.vessel_name}")
            logger.info(f"   Баржа готова: {match.barge_discharge.end_time.strftime('%d.%m %H:%M')}")
            logger.info(f"   Судно нужно:  {match.vessel_loading.start_time.strftime('%d.%m %H:%M')}")
            logger.info(f"   Gap: {match.gap_hours:+.1f}ч")
            
            for rec in match.recommendations:
                logger.info(f"   {rec}")
        
        if analysis.unmatched_barges:
            logger.info("\n БАРЖИ БЕЗ СУДНА:")
            for op in analysis.unmatched_barges:
                logger.info(f"   {op.vessel_name} - готова {op.end_time.strftime('%d.%m %H:%M')}")
        
        if analysis.unmatched_vessels:
            logger.info("\n СУДА БЕЗ БАРЖИ:")
            for op in analysis.unmatched_vessels:
                logger.info(f"   {op.vessel_name} - нужна {op.start_time.strftime('%d.%m %H:%M')}")
        
        logger.info("\n" + "=" * 70)
        logger.info(" ИТОГО:")
        logger.info(f"   Стыковок: {len(analysis.matches)}")
        logger.info(f"   Ожидание: {analysis.total_waiting_hours:.1f}ч (можно оптимизировать)")
        logger.info(f"   Демерредж: ${analysis.total_demurrage:,.0f}")
        logger.info("=" * 70)