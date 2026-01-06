"""
Калькулятор рейсов Deep Sea
===========================

Автоматический расчёт времени и стоимости по плечам
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import logging
import math

from modules.deepsea_data import (
    DeepSeaData, DeepSeaParams, Vessel, Port, Canal, Distance,
    RouteLeg, VoyagePlan, CalculatedLeg, CalculatedVoyage
)
from modules.profiler import profile_performance

logger = logging.getLogger(__name__)


class DeepSeaCalculator:
    """
    Калькулятор рейсов Deep Sea
    
    Расчёт по плечам:
    1. Loading  - время = qty / load_rate + port overhead
    2. Sea      - время = distance / speed + weather margin
    3. Canal    - время = transit + waiting
    4. Bunker   - время = bunker_time
    5. Discharge - время = qty / disch_rate + port overhead
    """
    
    def __init__(self, data: DeepSeaData):
        self.data = data
        self.params = data.params
    
    @profile_performance
    def calculate_all(self) -> DeepSeaData:
        """Рассчитать все рейсы"""
        logger.info("\n" + "=" * 70)
        logger.info(" РАСЧЁТ РЕЙСОВ DEEP SEA")
        logger.info("=" * 70)
        
        for plan in self.data.voyage_plans:
            voyage = self._calculate_voyage(plan)
            if voyage:
                self.data.calculated_voyages[voyage.voyage_id] = voyage
                
                logger.info(f"\n   {voyage.voyage_id}: {voyage.vessel_name}")
                logger.info(f"     {voyage.load_port} → {voyage.disch_port}")
                logger.info(f"     {voyage.cargo_type} {voyage.qty_mt:,.0f} MT")
                logger.info(f"     {voyage.actual_start.strftime('%d.%m')} - {voyage.actual_end.strftime('%d.%m')} ({voyage.total_days:.1f} дней)")
                logger.info(f"     Расстояние: {voyage.total_distance_nm:,.0f} nm")
                logger.info(f"     Стоимость: ${voyage.total_cost_usd:,.0f}")
        
        logger.info(f"\n  Рассчитано рейсов: {len(self.data.calculated_voyages)}")
        
        return self.data
    
    def _calculate_voyage(self, plan: VoyagePlan) -> Optional[CalculatedVoyage]:
        """Расчёт одного рейса"""
        # Получаем судно
        vessel = self.data.vessels.get(plan.vessel_id)
        if not vessel:
            logger.warning(f" Судно {plan.vessel_id} не найдено")
            return None
        
        # Получаем плечи маршрута
        route_legs = self.data.get_route_legs(plan.route_id)
        if not route_legs:
            logger.warning(f" Маршрут {plan.route_id} не найден")
            return None
        
        # Начинаем с laycan_start в 08:00
        start_time = datetime.combine(plan.laycan_start, datetime.min.time())
        start_time = start_time.replace(hour=8)
        
        # Создаём рейс
        voyage = CalculatedVoyage(
            voyage_id=plan.voyage_id,
            vessel_id=plan.vessel_id,
            vessel_name=vessel.vessel_name,
            vessel_class=vessel.vessel_class,
            route_id=plan.route_id,
            cargo_type=plan.cargo_type,
            qty_mt=plan.qty_mt,
            load_port=plan.load_port,
            disch_port=plan.disch_port,
            laycan_start=plan.laycan_start,
            laycan_end=plan.laycan_end,
            actual_start=start_time,
            actual_end=start_time,  # Will be updated after leg calculations
            charterer=plan.charterer,
            remarks=plan.remarks,
            operational_cost_allocation=plan.operational_cost_allocation,
            overhead_cost_allocation=plan.overhead_cost_allocation,
            other_cost_allocation=plan.other_cost_allocation)
        
        current_time = start_time
        
        # Рассчитываем каждое плечо
        total_distance = 0
        total_bunker_cost = 0
        total_port_cost = 0
        total_canal_cost = 0
        sea_days = 0
        port_days = 0
        
        for leg_template in route_legs:
            calc_leg = self._calculate_leg(leg_template, plan, vessel, current_time)
            
            if calc_leg:
                voyage.legs.append(calc_leg)
                current_time = calc_leg.end_time
                
                # Накапливаем статистику
                total_distance += calc_leg.distance_nm
                total_bunker_cost += calc_leg.bunker_cost_usd
                total_port_cost += calc_leg.port_cost_usd
                total_canal_cost += calc_leg.canal_cost_usd
                
                if calc_leg.leg_type == 'sea':
                    sea_days += calc_leg.duration_days
                elif calc_leg.leg_type in ['loading', 'discharge']:
                    port_days += calc_leg.duration_days
        
        voyage.actual_end = current_time
        voyage.total_distance_nm = total_distance
        voyage.total_bunker_cost_usd = total_bunker_cost
        voyage.total_port_cost_usd = total_port_cost
        voyage.total_canal_cost_usd = total_canal_cost
        voyage.sea_days = sea_days
        voyage.port_days = port_days
        
        # Расчёт финансов
        voyage.freight_revenue_usd = plan.qty_mt * plan.freight_rate_mt
        voyage.hire_cost_usd = vessel.daily_hire_usd * voyage.total_days
        
        return voyage
    
    def _calculate_leg(
        self,
        leg_template: RouteLeg,
        plan: VoyagePlan,
        vessel: Vessel,
        start_time: datetime
    ) -> Optional[CalculatedLeg]:
        """Расчёт одного плеча"""
        
        leg_type = leg_template.leg_type.lower()
        is_laden = leg_template.cargo_state.lower() == 'laden'
        
        # Базовые параметры
        duration_hours = 0
        distance_nm = 0
        speed_kn = 0
        bunker_cost = 0
        port_cost = 0
        canal_cost = 0
        
        if leg_type == 'loading':
            duration_hours, port_cost = self._calc_loading(leg_template, plan, vessel)
            
        elif leg_type == 'discharge':
            duration_hours, port_cost = self._calc_discharge(leg_template, plan, vessel)
            
        elif leg_type == 'sea':
            duration_hours, distance_nm, speed_kn, bunker_cost = self._calc_sea_leg(
                leg_template, vessel, is_laden
            )
            
        elif leg_type == 'canal':
            duration_hours, canal_cost = self._calc_canal(leg_template, plan, vessel)
            
        elif leg_type == 'bunker':
            duration_hours = self.params.bunker_time_hours
            # Стоимость бункера считается в sea legs
            
        elif leg_type == 'waiting':
            duration_hours = 24  # Default 1 день
            
        else:
            duration_hours = 12  # Default
        
        end_time = start_time + timedelta(hours=duration_hours)
        
        calc_leg = CalculatedLeg(
            voyage_id=plan.voyage_id,
            vessel_id=plan.vessel_id,
            vessel_name=vessel.vessel_name,
            leg_seq=leg_template.leg_seq,
            leg_type=leg_type,
            from_port=leg_template.from_port,
            to_port=leg_template.to_port,
            cargo_state=leg_template.cargo_state,
            start_time=start_time,
            end_time=end_time,
            duration_hours=duration_hours,
            distance_nm=distance_nm,
            speed_kn=speed_kn,
            cargo_type=plan.cargo_type,
            qty_mt=plan.qty_mt if leg_type in ['loading', 'discharge'] else 0,
            bunker_cost_usd=bunker_cost,
            port_cost_usd=port_cost,
            canal_cost_usd=canal_cost,
            canal_id=leg_template.canal_id,
            remarks=leg_template.remarks
        )
        
        return calc_leg
    
    def _calc_loading(
        self, 
        leg: RouteLeg, 
        plan: VoyagePlan, 
        vessel: Vessel
    ) -> tuple:
        """Расчёт времени загрузки"""
        port = self.data.ports.get(leg.from_port)
        
        if port:
            load_rate = port.load_rate_mt_day
            port_charges = port.port_charges_usd
        else:
            load_rate = self.params.default_load_rate
            port_charges = 0
        
        # Время погрузки
        cargo_hours = (plan.qty_mt / load_rate) * 24
        
        # Накладные расходы порта
        overhead_hours = self.params.port_overhead_hours
        
        total_hours = cargo_hours + overhead_hours
        
        return total_hours, port_charges
    
    def _calc_discharge(
        self,
        leg: RouteLeg,
        plan: VoyagePlan,
        vessel: Vessel
    ) -> tuple:
        """Расчёт времени выгрузки"""
        port = self.data.ports.get(leg.from_port)
        
        if port:
            disch_rate = port.disch_rate_mt_day
            port_charges = port.port_charges_usd
        else:
            disch_rate = self.params.default_disch_rate
            port_charges = 0
        
        cargo_hours = (plan.qty_mt / disch_rate) * 24
        overhead_hours = self.params.port_overhead_hours
        
        total_hours = cargo_hours + overhead_hours
        
        return total_hours, port_charges
    
    def _calc_sea_leg(
        self,
        leg: RouteLeg,
        vessel: Vessel,
        is_laden: bool
    ) -> tuple:
        """Расчёт морского перехода"""
        # Получаем расстояние
        dist_obj = self.data.get_distance(leg.from_port, leg.to_port)
        
        if dist_obj:
            distance = dist_obj.distance_nm
            eca_miles = dist_obj.eca_miles
        else:
            # Пробуем обратное направление
            dist_obj = self.data.get_distance(leg.to_port, leg.from_port)
            if dist_obj:
                distance = dist_obj.distance_nm
                eca_miles = dist_obj.eca_miles
            else:
                logger.warning(f"Расстояние не найдено: {leg.from_port} → {leg.to_port}")
                distance = 1000  # Default
                eca_miles = 0
        
        # Скорость
        if is_laden:
            speed = vessel.speed_laden_kn or self.params.default_speed_laden
            consumption = vessel.consumption_laden_mt
        else:
            speed = vessel.speed_ballast_kn or self.params.default_speed_ballast
            consumption = vessel.consumption_ballast_mt
        
        # Время перехода
        sea_hours = distance / speed
        
        # Погодный запас
        weather_margin = 1 + (self.params.weather_margin_pct / 100)
        sea_hours *= weather_margin
        
        # Расход топлива
        sea_days = sea_hours / 24
        ifo_consumed = consumption * sea_days
        
        # ECA зона - MGO
        if eca_miles > 0:
            eca_hours = eca_miles / speed
            eca_days = eca_hours / 24
            mgo_consumed = consumption * eca_days * 0.8  # MGO немного меньше
            ifo_consumed -= mgo_consumed  # Вычитаем из IFO
        else:
            mgo_consumed = 0
        
        bunker_cost = (ifo_consumed * self.params.bunker_ifo_price + 
                       mgo_consumed * self.params.bunker_mgo_price)
        
        return sea_hours, distance, speed, bunker_cost
    
    def _calc_canal(
        self,
        leg: RouteLeg,
        plan: VoyagePlan,
        vessel: Vessel
    ) -> tuple:
        """Расчёт прохода канала"""
        if not leg.canal_id:
            return 12, 0  # No canal specified
        
        canal = self.data.canals.get(leg.canal_id)
        
        if not canal:
            return 12, 0  # Default
        
        # Проверка ограничений
        if not vessel.can_transit_canal(canal):
            logger.warning(f"  {vessel.vessel_name} не может пройти {canal.canal_name}")
            return 0, 0
        
        # Время
        transit_hours = canal.transit_hours
        waiting_hours = canal.waiting_hours_avg + self.params.canal_waiting_buffer
        total_hours = transit_hours + waiting_hours
        
        # Стоимость
        canal_fee = canal.base_fee_usd + (canal.fee_per_ton_usd * vessel.dwt_mt)
        
        return total_hours, canal_fee
    
    def get_schedule_dataframe(self):
        """Получить расписание как DataFrame"""
        import pandas as pd
        
        rows = []
        for voyage in self.data.calculated_voyages.values():
            for leg in voyage.legs:
                rows.append({
                    'voyage_id': leg.voyage_id,
                    'vessel_id': leg.vessel_id,
                    'vessel_name': leg.vessel_name,
                    'leg_seq': leg.leg_seq,
                    'leg_type': leg.leg_type,
                    'from_port': leg.from_port,
                    'to_port': leg.to_port,
                    'cargo_state': leg.cargo_state,
                    'cargo_type': leg.cargo_type,
                    'qty_mt': leg.qty_mt,
                    'start_time': leg.start_time,
                    'end_time': leg.end_time,
                    'duration_hours': round(leg.duration_hours, 1),
                    'duration_days': round(leg.duration_days, 2),
                    'distance_nm': round(leg.distance_nm, 0),
                    'speed_kn': round(leg.speed_kn, 1),
                    'bunker_cost_usd': round(leg.bunker_cost_usd, 0),
                    'port_cost_usd': round(leg.port_cost_usd, 0),
                    'canal_cost_usd': round(leg.canal_cost_usd, 0),
                    'remarks': leg.remarks
                })
        
        return pd.DataFrame(rows)
    
    def get_voyage_summary_dataframe(self):
        """Сводка по рейсам"""
        import pandas as pd
        
        rows = []
        for voyage in self.data.calculated_voyages.values():
            rows.append({
                'voyage_id': voyage.voyage_id,
                'vessel_name': voyage.vessel_name,
                'vessel_class': voyage.vessel_class,
                'route': f"{voyage.load_port} → {voyage.disch_port}",
                'cargo_type': voyage.cargo_type,
                'qty_mt': voyage.qty_mt,
                'laycan': f"{voyage.laycan_start.strftime('%d.%m')} - {voyage.laycan_end.strftime('%d.%m')}",
                'actual_start': voyage.actual_start.strftime('%d.%m %H:%M'),
                'actual_end': voyage.actual_end.strftime('%d.%m %H:%M'),
                'total_days': round(voyage.total_days, 1),
                'sea_days': round(voyage.sea_days, 1),
                'port_days': round(voyage.port_days, 1),
                'distance_nm': round(voyage.total_distance_nm, 0),
                'freight_usd': round(voyage.freight_revenue_usd, 0),
                'bunker_cost': round(voyage.total_bunker_cost_usd, 0),
                'port_cost': round(voyage.total_port_cost_usd, 0),
                'canal_cost': round(voyage.total_canal_cost_usd, 0),
                'hire_cost': round(voyage.hire_cost_usd, 0),
                'total_cost': round(voyage.total_cost_usd, 0),
                'tce_usd': round(voyage.tce_usd, 0),
                'charterer': voyage.charterer
            })
        
        return pd.DataFrame(rows)
    
    def export_schedule_csv(self, filepath: str):
        """Экспорт расписания в CSV"""
        df = self.get_schedule_dataframe()
        df.to_csv(filepath, index=False, sep=';', encoding='utf-8')
        logger.info(f"   Расписание: {filepath}")
    
    def export_summary_csv(self, filepath: str):
        """Экспорт сводки в CSV"""
        df = self.get_voyage_summary_dataframe()
        df.to_csv(filepath, index=False, sep=';', encoding='utf-8')
        logger.info(f"   Сводка: {filepath}")