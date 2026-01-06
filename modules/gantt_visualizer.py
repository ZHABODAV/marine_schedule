"""
Gantt-диаграммы для визуализации рейсов и операций
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from modules.data_loader import AllData, Voyage, VoyageLeg, Vessel
from modules.config import config

logger = logging.getLogger(__name__)


def get_colors_from_config() -> Dict[str, str]:
    """Load colors from config or use defaults."""
    defaults = {
        'Cargo_ops_ld': '#4CAF50',
        'Cargo_ops_ds': '#2196F3',
        'Laden': '#FF9800',
        'Ballast': '#9E9E9E',
        'Bunkering_DO': '#795548',
        'CanalTransit': '#9C27B0',
        'Waiting': '#F44336',
        'SFO': '#FFD700',
        'RPO': '#FFA500',
        'WHEAT': '#DEB887',
        'CORN': '#F0E68C',
        'Completed': '#4CAF50',
        'In Process': '#2196F3',
        'Planned': '#9E9E9E',
        'barge_arrival': '#E91E63',
        'vessel_loading': '#3F51B5',
        'storage': '#00BCD4',
    }
    
    # Try to load from config
    config_colors = config.get('gantt.colors', {})
    
    # Map config keys to internal keys if needed, or just merge
    # The config uses keys like 'loading', 'discharge' which map to 'Cargo_ops_ld', 'Cargo_ops_ds'
    mapping = {
        'loading': 'Cargo_ops_ld',
        'discharge': 'Cargo_ops_ds',
        'sea_laden': 'Laden',
        'sea_ballast': 'Ballast',
        'canal': 'CanalTransit',
        'bunker': 'Bunkering_DO',
        'waiting': 'Waiting',
        'In_Process': 'In Process'
    }
    
    colors = defaults.copy()
    for cfg_key, hex_val in config_colors.items():
        # Add # if missing
        if not hex_val.startswith('#'):
            hex_val = f"#{hex_val}"
            
        # Map to internal key if exists, otherwise use as is
        internal_key = mapping.get(cfg_key, cfg_key)
        colors[internal_key] = hex_val
        
    return colors

# Initialize colors
COLORS = get_colors_from_config()


class GanttVisualizer:
    """Создание Gantt-диаграмм"""
    
    def __init__(self, data: AllData, output_dir: str = "output"):
        self.data = data
        self.output_dir = output_dir
        
        # Настройки по умолчанию
        self.fig_width = 16
        self.bar_height = 0.6
        self.font_size = 8
    
    def create_vessel_schedule_gantt(
        self,
        vessel_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filename: str = "gantt_vessels.png"
    ) -> str:
        """
        Создание Gantt-диаграммы расписания судов
        """
        logger.info(f"Создание Gantt-диаграммы судов...")
        
        # Выбираем суда
        if vessel_ids:
            vessels = [self.data.vessels[vid] for vid in vessel_ids if vid in self.data.vessels]
        else:
            vessels = list(self.data.vessels.values())
        
        if not vessels:
            logger.warning("Нет судов для отображения")
            return ""
        
        # Получаем рейсы для судов
        vessel_voyages = {}
        for vessel in vessels:
            voyages = self.data.get_vessel_voyages(vessel.vessel_id)
            if voyages:
                vessel_voyages[vessel.vessel_id] = voyages
        
        if not vessel_voyages:
            logger.warning("Нет рейсов для отображения")
            return ""
        
        # Определяем временной диапазон
        all_times = []
        for voyages in vessel_voyages.values():
            for voyage in voyages:
                if voyage.start_time:
                    all_times.append(voyage.start_time)
                if voyage.end_time:
                    all_times.append(voyage.end_time)
        
        if not all_times:
            return ""
        
        if start_date is None:
            start_date = min(all_times) - timedelta(days=1)
        if end_date is None:
            end_date = max(all_times) + timedelta(days=1)
        
        # Создаем фигуру
        n_vessels = len(vessel_voyages)
        fig_height = max(6, n_vessels * 1.2)
        fig, ax = plt.subplots(figsize=(self.fig_width, fig_height))
        
        # Рисуем рейсы
        y_labels = []
        y_pos = 0
        
        for vessel_id in sorted(vessel_voyages.keys()):
            vessel = self.data.vessels.get(vessel_id)
            voyages = vessel_voyages[vessel_id]
            
            if vessel:
                vessel_label = f"{vessel.vessel_name}\n({vessel.vessel_class})"
            else:
                vessel_label = f"{vessel_id}\n(Unknown)"
            y_labels.append(vessel_label)
            
            for voyage in voyages:
                for leg in voyage.legs:
                    self._draw_leg_bar(ax, leg, y_pos)
            
            y_pos += 1
        
        # Настраиваем оси
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=self.font_size)
        ax.set_ylim(-0.5, len(y_labels) - 0.5)
        
        ax.set_xlim(float(mdates.date2num(start_date)), float(mdates.date2num(end_date)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45, ha='right', fontsize=self.font_size)
        
        ax.set_xlabel('Дата', fontsize=10)
        ax.set_title('Расписание судов', fontsize=14, fontweight='bold')
        
        # Сетка
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        ax.set_axisbelow(True)
        
        # Легенда
        self._add_legend(ax)
        
        # Сохраняем
        filepath = f"{self.output_dir}/{filename}"
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"   Сохранено: {filepath}")
        return filepath
    
    def create_voyage_detail_gantt(
        self,
        voyage_id: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Детальная Gantt-диаграмма одного рейса
        """
        voyage = self.data.voyages.get(voyage_id)
        if not voyage:
            logger.warning(f"Рейс {voyage_id} не найден")
            return ""
        
        if filename is None:
            filename = f"gantt_voyage_{voyage_id}.png"
        
        logger.info(f"Создание детальной диаграммы рейса {voyage_id}...")
        
        # Создаем фигуру
        n_legs = len(voyage.legs)
        fig_height = max(4, n_legs * 0.8)
        fig, ax = plt.subplots(figsize=(14, fig_height))
        
        # Рисуем каждый leg отдельной строкой
        y_labels = []
        
        for i, leg in enumerate(sorted(voyage.legs, key=lambda l: l.leg_seq)):
            y_pos = i
            
            # Метка
            if leg.leg_type == 'Port':
                label = f"{leg.op_detail}\n@ {leg.port_start_id}"
            else:
                label = f"{leg.op_detail}\n{leg.port_start_id}→{leg.port_end_id}"
            y_labels.append(label)
            
            # Рисуем бар
            self._draw_leg_bar(ax, leg, y_pos, show_details=True)
        
        # Настраиваем оси
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=self.font_size)
        ax.set_ylim(-0.5, len(y_labels) - 0.5)
        
        # Временной диапазон
        if voyage.start_time and voyage.end_time:
            margin = timedelta(hours=12)
            ax.set_xlim(
                float(mdates.date2num(voyage.start_time - margin)),
                float(mdates.date2num(voyage.end_time + margin))
            )
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %H:%M'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        plt.xticks(rotation=45, ha='right', fontsize=self.font_size)
        
        ax.set_xlabel('Дата/Время', fontsize=10)
        ax.set_title(
            f'Рейс: {voyage_id}\n'
            f'Судно: {voyage.vessel_name} | Груз: {voyage.cargo_id} | {voyage.qty_mt:,.0f} MT',
            fontsize=12, fontweight='bold'
        )
        
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        
        # Сохраняем
        filepath = f"{self.output_dir}/{filename}"
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"   Сохранено: {filepath}")
        return filepath
    
    def create_port_operations_gantt(
        self,
        port_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Gantt-диаграмма операций в порту
        """
        if filename is None:
            filename = f"gantt_port_{port_id}.png"
        
        logger.info(f"Создание диаграммы операций в порту {port_id}...")
        
        # Находим все legs в этом порту
        port_legs = [
            leg for leg in self.data.voyage_legs
            if leg.port_start_id == port_id or leg.port_end_id == port_id
        ]
        
        if not port_legs:
            logger.warning(f"Нет операций в порту {port_id}")
            return ""
        
        # Группируем по судам
        legs_by_vessel = {}
        for leg in port_legs:
            if leg.vessel_id not in legs_by_vessel:
                legs_by_vessel[leg.vessel_id] = []
            legs_by_vessel[leg.vessel_id].append(leg)
        
        # Определяем временной диапазон
        all_times = []
        for leg in port_legs:
            all_times.append(leg.start_time)
            all_times.append(leg.end_time)
        
        if start_date is None:
            start_date = min(all_times) - timedelta(days=1)
        if end_date is None:
            end_date = max(all_times) + timedelta(days=1)
        
        # Создаем фигуру
        n_vessels = len(legs_by_vessel)
        fig_height = max(4, n_vessels * 1.0)
        fig, ax = plt.subplots(figsize=(14, fig_height))
        
        y_labels = []
        y_pos = 0
        
        for vessel_id in sorted(legs_by_vessel.keys()):
            vessel = self.data.vessels.get(vessel_id)
            vessel_name = vessel.vessel_name if vessel else vessel_id
            y_labels.append(vessel_name)
            
            for leg in legs_by_vessel[vessel_id]:
                self._draw_leg_bar(ax, leg, y_pos, show_details=True)
            
            y_pos += 1
        
        # Настраиваем оси
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=self.font_size)
        ax.set_ylim(-0.5, len(y_labels) - 0.5)
        
        ax.set_xlim(float(mdates.date2num(start_date)), float(mdates.date2num(end_date)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        plt.xticks(rotation=45, ha='right', fontsize=self.font_size)
        
        port = self.data.ports.get(port_id)
        port_name = port.port_name if port else port_id
        ax.set_title(f'Операции в порту: {port_name} ({port_id})', fontsize=14, fontweight='bold')
        
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        self._add_legend(ax)
        
        # Сохраняем
        filepath = f"{self.output_dir}/{filename}"
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"   Сохранено: {filepath}")
        return filepath
    
    def create_olya_coordination_gantt(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filename: str = "gantt_olya_coordination.png"
    ) -> str:
        """
        Специальная диаграмма для стыковки в Olya
        Показывает прибытие барж и загрузку судов
        """
        logger.info("Создание диаграммы стыковки в Olya...")
        
        # Находим все операции в Olya (OYA)
        olya_legs = self.data.get_olya_operations()
        
        if not olya_legs:
            logger.warning("Нет операций в Olya")
            return ""
        
        # Разделяем по типу судна (река-море vs морские)
        river_sea_ops = []  # Баржи/река-море суда (discharge в OYA)
        sea_vessel_ops = []  # Морские суда (loading в OYA)
        
        for leg in olya_legs:
            vessel = self.data.vessels.get(leg.vessel_id)
            if vessel:
                if vessel.is_river_sea:
                    river_sea_ops.append(leg)
                else:
                    sea_vessel_ops.append(leg)
        
        # Определяем временной диапазон
        all_times = []
        for leg in olya_legs:
            all_times.append(leg.start_time)
            all_times.append(leg.end_time)
        
        if not all_times:
            logger.warning("Нет временных меток для операций в Olya")
            return ""
        
        # Гарантируем, что start_date и end_date определены
        if start_date is None:
            start_date = min(all_times) - timedelta(days=2)
        if end_date is None:
            end_date = max(all_times) + timedelta(days=2)
        
        # Убеждаемся, что типы корректны для type checker
        assert start_date is not None, "start_date должен быть определен"
        assert end_date is not None, "end_date должен быть определен"
        
        # Создаем фигуру с двумя подграфиками
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
        
        # === Верхний график: Река-море суда (баржи) ===
        self._draw_olya_section(
            ax1, 
            river_sea_ops, 
            "Река-море суда / Баржи (разгрузка в Olya)",
            start_date, end_date
        )
        
        # === Нижний график: Морские суда ===
        self._draw_olya_section(
            ax2,
            sea_vessel_ops,
            "Морские суда (загрузка в Olya)",
            start_date, end_date
        )
        
        # Общий заголовок
        fig.suptitle(
            'Координация стыковки в OLYA\n'
            'Синхронизация прибытия барж и загрузки морских судов',
            fontsize=14, fontweight='bold', y=1.02
        )
        
        # Сохраняем
        filepath = f"{self.output_dir}/{filename}"
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"   Сохранено: {filepath}")
        return filepath
    
    def _draw_olya_section(
        self,
        ax,
        legs: List[VoyageLeg],
        title: str,
        start_date: datetime,
        end_date: datetime
    ):
        """Рисуем секцию Olya диаграммы"""
        if not legs:
            ax.text(0.5, 0.5, 'Нет операций', ha='center', va='center', fontsize=12)
            ax.set_title(title, fontsize=11, fontweight='bold')
            return
        
        # Группируем по судам
        legs_by_vessel = {}
        for leg in legs:
            if leg.vessel_id not in legs_by_vessel:
                legs_by_vessel[leg.vessel_id] = []
            legs_by_vessel[leg.vessel_id].append(leg)
        
        y_labels = []
        y_pos = 0
        
        for vessel_id in sorted(legs_by_vessel.keys()):
            vessel = self.data.vessels.get(vessel_id)
            vessel_name = vessel.vessel_name if vessel else vessel_id
            y_labels.append(vessel_name)
            
            for leg in legs_by_vessel[vessel_id]:
                # Цвет в зависимости от операции
                if leg.is_loading:
                    color = COLORS['vessel_loading']
                elif leg.is_discharge:
                    color = COLORS['barge_arrival']
                else:
                    color = COLORS.get(leg.op_group, '#808080')
                
                start_num = float(mdates.date2num(leg.start_time))
                duration = (leg.end_time - leg.start_time).total_seconds() / 86400
                
                rect = Rectangle(
                    (start_num, y_pos - self.bar_height/2),
                    duration,
                    self.bar_height,
                    facecolor=color,
                    edgecolor='black',
                    linewidth=0.5,
                    alpha=0.8
                )
                ax.add_patch(rect)
                
                # Подпись
                if duration > 0.5:  # Если достаточно места
                    mid_time = leg.start_time + (leg.end_time - leg.start_time) / 2
                    ax.text(
                        mdates.date2num(mid_time), y_pos,
                        f"{leg.qty_mt/1000:.0f}k",
                        ha='center', va='center',
                        fontsize=7, color='white', fontweight='bold'
                    )
            
            y_pos += 1
        
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=self.font_size)
        ax.set_ylim(-0.5, max(1, len(y_labels)) - 0.5)
        
        ax.set_xlim(start_date, end_date)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        
        # Легенда для Olya
        legend_patches = [
            mpatches.Patch(color=COLORS['barge_arrival'], label='Разгрузка баржи'),
            mpatches.Patch(color=COLORS['vessel_loading'], label='Загрузка судна'),
        ]
        ax.legend(handles=legend_patches, loc='upper right', fontsize=8)
    
    def _draw_leg_bar(
        self,
        ax,
        leg: VoyageLeg,
        y_pos: float,
        show_details: bool = False
    ):
        """Рисуем бар для одного leg"""
        # Определяем цвет
        color = COLORS.get(leg.op_group, '#808080')
        
        # Определяем альфу по статусу
        alpha = 0.9 if leg.status == 'Completed' else 0.7 if leg.status == 'In Process' else 0.5
        
        start_num = float(mdates.date2num(leg.start_time))
        duration = leg.duration_days
        
        if duration <= 0:
            duration = 0.1  # Минимальная ширина
        
        rect = Rectangle(
            (start_num, y_pos - self.bar_height/2),
            duration,
            self.bar_height,
            facecolor=color,
            edgecolor='black',
            linewidth=0.5,
            alpha=alpha
        )
        ax.add_patch(rect)
        
        # Добавляем текст если достаточно места
        if show_details and duration > 1:
            mid_time = leg.start_time + timedelta(days=duration/2)
            label = leg.op_detail[:15]
            ax.text(
                mdates.date2num(mid_time), y_pos,
                label,
                ha='center', va='center',
                fontsize=6, color='white'
            )
    
    def _add_legend(self, ax):
        """Добавляем легенду"""
        legend_patches = [
            mpatches.Patch(color=COLORS['Cargo_ops_ld'], label='Загрузка'),
            mpatches.Patch(color=COLORS['Cargo_ops_ds'], label='Выгрузка'),
            mpatches.Patch(color=COLORS['Laden'], label='Груженый переход'),
            mpatches.Patch(color=COLORS['Ballast'], label='Балласт'),
            mpatches.Patch(color=COLORS['CanalTransit'], label='Канал'),
            mpatches.Patch(color=COLORS['Bunkering_DO'], label='Бункеровка'),
        ]
        ax.legend(handles=legend_patches, loc='upper right', fontsize=7, ncol=2)