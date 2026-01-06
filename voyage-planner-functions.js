// Enhanced Voyage Planner Functions
// Includes: Excel export, enhanced Gantt with dates, berth Gantt, and calendar view

// Update displayGantt to include date markers
function displayGanttWithDates() {
    const container = document.getElementById('ganttChart');
    if (!data.calculatedLegs || !data.calculatedLegs.length) {
        container.innerHTML = '<p style="color: #94A3B8;">Данные диаграммы Гантта недоступны.</p>';
        return;
    }
    
    // Find date range
    const allDates = data.calculatedLegs.map(l => new Date(l.StartDateTime));
    const minDate = new Date(Math.min(...allDates));
    const maxDate = new Date(Math.max(...data.calculatedLegs.map(l => new Date(l.EndDateTime))));
    
    // Generate date labels
    let dateLabels = [];
    let currentDate = new Date(minDate);
    while (currentDate <= maxDate) {
        dateLabels.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    const assetGroups = {};
    data.calculatedLegs.forEach(leg => {
        if (!assetGroups[leg.AssetID]) {
            assetGroups[leg.AssetID] = [];
        }
        assetGroups[leg.AssetID].push(leg);
    });
    
    let html = `
        <div class="gantt-timeline-header">
            ${dateLabels.map(date => `
                <div class="gantt-date-marker">
                    ${date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}
                </div>
            `).join('')}
        </div>
    `;
    
    Object.keys(assetGroups).sort().forEach(assetId => {
        const legs = assetGroups[assetId].sort((a, b) =>
            new Date(a.StartDateTime) - new Date(b.StartDateTime)
        );
        
        html += `<div class="gantt-row">`;
        html += `<div class="gantt-label">${assetId}</div>`;
        html += `<div class="gantt-timeline">`;
        
        legs.forEach(leg => {
            const opCode = getOpCode(leg.LegType, leg.OpDetail);
            const color = colorMap[opCode] || colorMap['UNK'];
            const width = Math.max(leg.DurationHours * 5, 50);
            const startDate = new Date(leg.StartDateTime);
            const endDate = new Date(leg.EndDateTime);
            
            html += `
                <div class="gantt-bar" style="background: ${color}; width: ${width}px;" 
                     title="${leg.VoyageID} - ${leg.LegType}\n${startDate.toLocaleString('ru-RU')} - ${endDate.toLocaleString('ru-RU')}\n${leg.DurationHours}ч">
                    ${leg.VoyageID.substring(0, 8)}
                </div>
            `;
        });
        
        html += `</div></div>`;
    });
    
    container.innerHTML = html;
}

// Display berth-based Gantt chart
function displayBerthGantt() {
    const container = document.getElementById('ganttBerthsChart');
    if (!data.calculatedLegs || !data.calculatedLegs.length) {
        container.innerHTML = '<p style="color: #94A3B8;">Данные диаграммы Гантта недоступны.</p>';
        return;
    }
    
    // Group by berths
    const berthGroups = {};
    data.calculatedLegs.forEach(leg => {
        if (leg.ConsumesBerthID) {
            if (!berthGroups[leg.ConsumesBerthID]) {
                berthGroups[leg.ConsumesBerthID] = [];
            }
            berthGroups[leg.ConsumesBerthID].push(leg);
        }
    });
    
    if (Object.keys(berthGroups).length === 0) {
        container.innerHTML = '<p style="color: #94A3B8;">Нет данных о причалах в рейсах.</p>';
        return;
    }
    
    // Find date range
    const allDates = data.calculatedLegs.filter(l => l.ConsumesBerthID).map(l => new Date(l.StartDateTime));
    const minDate = new Date(Math.min(...allDates));
    const maxDate = new Date(Math.max(...data.calculatedLegs.filter(l => l.ConsumesBerthID).map(l => new Date(l.EndDateTime))));
    
    // Generate date labels
    let dateLabels = [];
    let currentDate = new Date(minDate);
    while (currentDate <= maxDate) {
        dateLabels.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    let html = `
        <div class="gantt-timeline-header">
            ${dateLabels.map(date => `
                <div class="gantt-date-marker">
                    ${date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}
                </div>
            `).join('')}
        </div>
    `;
    
    Object.keys(berthGroups).sort().forEach(berthId => {
        const legs = berthGroups[berthId].sort((a, b) => 
            new Date(a.StartDateTime) - new Date(b.StartDateTime)
        );
        
        html += `<div class="gantt-row">`;
        html += `<div class="gantt-label">${berthId}</div>`;
        html += `<div class="gantt-timeline">`;
        
        legs.forEach(leg => {
            const opCode = getOpCode(leg.LegType, leg.OpDetail);
            const color = colorMap[opCode] || colorMap['UNK'];
            const width = Math.max(leg.DurationHours * 5, 50);
            const startDate = new Date(leg.StartDateTime);
            const endDate = new Date(leg.EndDateTime);
            
            html += `
                <div class="gantt-bar" style="background: ${color}; width: ${width}px;" 
                     title="${leg.AssetID} - ${leg.VoyageID}\n${startDate.toLocaleString('ru-RU')} - ${endDate.toLocaleString('ru-RU')}\n${leg.DurationHours}ч">
                    ${leg.AssetID.substring(0, 10)}
                </div>
            `;
        });
        
        html += `</div></div>`;
    });
    
    container.innerHTML = html;
}

// Display interactive calendar view
function displayCalendar() {
    const container = document.getElementById('calendarView');
    if (!data.calculatedLegs || !data.calculatedLegs.length) {
        container.innerHTML = '<p style="color: #94A3B8;">Календарь недоступен.</p>';
        return;
    }
    
    // Group legs by date
    const eventsByDate = {};
    data.calculatedLegs.forEach(leg => {
        const startDate = new Date(leg.StartDateTime).toDateString();
        if (!eventsByDate[startDate]) {
            eventsByDate[startDate] = [];
        }
        eventsByDate[startDate].push(leg);
    });
    
    // Get min and max dates
    const allDates = Object.keys(eventsByDate).map(d => new Date(d)).sort((a, b) => a - b);
    if (allDates.length === 0) return;
    
    let html = '<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-top: 20px;">';
    
    // Calendar header
    const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    weekDays.forEach(day => {
        html += `<div style="text-align: center; color: #64748B; font-weight: 600; padding: 10px;">${day}</div>`;
    });
    
    const firstDate = new Date(allDates[0]);
    const lastDate = new Date(allDates[allDates.length - 1]);
    
    // Start from Monday of the week containing firstDate
    const startDate = new Date(firstDate);
    startDate.setDate(firstDate.getDate() - (firstDate.getDay() === 0 ? 6 : firstDate.getDay() - 1));
    
    let currentDate = new Date(startDate);
    while (currentDate <= lastDate) {
        const dateStr = currentDate.toDateString();
        const events = eventsByDate[dateStr] || [];
        const isToday = currentDate.toDateString() === new Date().toDateString();
        
        html += `
            <div style="
                background: ${events.length > 0 ? '#1E293B' : '#0F172A'};
                border: ${isToday ? '2px solid #3B82F6' : '1px solid #334155'};
                border-radius: 8px;
                padding: 10px;
                min-height: 80px;
                ${events.length > 0 ? 'cursor: pointer;' : ''}
            ">
                <div style="color: ${currentDate.getMonth() === firstDate.getMonth() ? '#F8FAFC' : '#64748B'}; font-weight: 600; margin-bottom: 5px;">
                    ${currentDate.getDate()}
                </div>
                ${events.length > 0 ? `
                    <div style="font-size: 0.75rem; color: #94A3B8;">
                        ${events.length} событий
                    </div>
                    <div style="margin-top: 5px;">
                        ${events.slice(0, 2).map(e => `
                            <div style="background: ${colorMap[getOpCode(e.LegType, e.OpDetail)] || '#64748B'}; color: white; padding: 2px 5px; border-radius: 4px; font-size: 0.7rem; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                ${e.AssetID.substring(0, 10)}
                            </div>
                        `).join('')}
                        ${events.length > 2 ? `<div style="font-size: 0.7rem; color: #64748B;">+${events.length - 2} еще</div>` : ''}
                    </div>
                ` : ''}
            </div>
        `;
        
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// Export results to Excel
function exportToExcel() {
    if (!data.calculatedLegs || !data.calculatedLegs.length) {
        alert('Нет данных для экспорта. Сначала рассчитайте рейсы.');
        return;
    }
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    
    // Export calculated legs
    const legsData = data.calculatedLegs.map(leg => ({
        'ID Рейса': leg.VoyageID,
        'Актив': leg.AssetID,
        'Этап': leg.LegSeq,
        'Тип': leg.LegType,
        'Детали': leg.OpDetail,
        'Порт Начала': leg.PortStartID,
        'Порт Конца': leg.PortEndID,
        'Начало': new Date(leg.StartDateTime).toLocaleString('ru-RU'),
        'Окончание': new Date(leg.EndDateTime).toLocaleString('ru-RU'),
        'Длительность (ч)': leg.DurationHours,
        'Тип Груза': leg.CargoType,
        'Количество (MT)': leg.Qty_MT,
        'ID Причала': leg.ConsumesBerthID
    }));
    
    const legsSheet = XLSX.utils.json_to_sheet(legsData);
    XLSX.utils.book_append_sheet(wb, legsSheet, 'Этапы Рейсов');
    
    // Export voyage summary
    const voyageSummary = data.voyages.map(v => {
        const legs = data.calculatedLegs.filter(l => l.VoyageID === v.VoyageID);
        const start = legs.length ? new Date(legs[0].StartDateTime) : null;
        const end = legs.length ? new Date(legs[legs.length - 1].EndDateTime) : null;
        const duration = legs.reduce((sum, l) => sum + l.DurationHours, 0);
        
        return {
            'ID Рейса': v.VoyageID,
            'Актив': v.AssetID,
            'ID Шаблона': v.TemplateID,
            'Тип Груза': v.CargoType,
            'Количество (MT)': v.Qty_MT,
            'Начало': start ? start.toLocaleString('ru-RU') : 'Н/Д',
            'Окончание': end ? end.toLocaleString('ru-RU') : 'Н/Д',
            'Длительность (ч)': duration,
            'Длительность (дней)': (duration / 24).toFixed(2),
            'Количество Этапов': legs.length
        };
    });
    
    const summarySheet = XLSX.utils.json_to_sheet(voyageSummary);
    XLSX.utils.book_append_sheet(wb, summarySheet, 'Сводка Рейсов');
    
    // Export alerts if any
    if (data.alerts && data.alerts.length > 0) {
        const alertsSheet = XLSX.utils.json_to_sheet(data.alerts);
        XLSX.utils.book_append_sheet(wb, alertsSheet, 'Предупреждения');
    }
    
    // Save file
    const fileName = `voyage_results_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, fileName);
}

// Display berth utilization analysis
function displayBerthUtilization() {
    const container = document.getElementById('utilizationResults');
    if (!data.calculatedLegs || !data.calculatedLegs.length) {
        container.innerHTML = '<p style="color: #94A3B8;">Данные о загрузке недоступны. Сначала рассчитайте рейсы.</p>';
        return;
    }
    
    // Calculate berth utilization
    const berthStats = {};
    const berthLegs = data.calculatedLegs.filter(leg => leg.ConsumesBerthID);
    
    if (berthLegs.length === 0) {
        container.innerHTML = '<p style="color: #94A3B8;">Нет данных о причалах в рассчитанных рейсах.</p>';
        return;
    }
    
    // Find date range
    const allDates = berthLegs.map(l => new Date(l.StartDateTime));
    const minDate = new Date(Math.min(...allDates));
    const maxDate = new Date(Math.max(...berthLegs.map(l => new Date(l.EndDateTime))));
    const totalHours = (maxDate - minDate) / (1000 * 60 * 60);
    
    berthLegs.forEach(leg => {
        if (!berthStats[leg.ConsumesBerthID]) {
            berthStats[leg.ConsumesBerthID] = {
                totalHours: 0,
                loadingHours: 0,
                dischargeHours: 0,
                otherHours: 0,
                operations: 0,
                assets: new Set()
            };
        }
        
        const stats = berthStats[leg.ConsumesBerthID];
        stats.totalHours += leg.DurationHours;
        stats.operations++;
        stats.assets.add(leg.AssetID);
        
        const opCode = getOpCode(leg.LegType, leg.OpDetail);
        if (opCode === 'LD') {
            stats.loadingHours += leg.DurationHours;
        } else if (opCode === 'DS') {
            stats.dischargeHours += leg.DurationHours;
        } else {
            stats.otherHours += leg.DurationHours;
        }
    });
    
    let html = `
        <div style="margin-bottom: 20px;">
            <button class="export-button" onclick="downloadBerthUtilization()">
                 Скачать Загрузку Причалов (Excel)
            </button>
        </div>
        <div class="results-grid">
    `;
    
    Object.keys(berthStats).sort().forEach(berthId => {
        const stats = berthStats[berthId];
        const utilization = Math.round((stats.totalHours / totalHours) * 100);
        
        html += `
            <div class="metric-card">
                <h3 style="color: #5C6BC0; margin-bottom: 15px;">${berthId}</h3>
                <div class="metric-label">Загрузка</div>
                <div class="metric-value">${utilization}%</div>
                <div class="metric-unit">от общего времени</div>
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #374151;">
                    <p style="color: #D1D5DB; margin-bottom: 5px;"><strong>Всего часов:</strong> ${Math.round(stats.totalHours)}</p>
                    <p style="color: #10B981; margin-bottom: 5px;">Погрузка: ${Math.round(stats.loadingHours)} ч</p>
                    <p style="color: #06B6D4; margin-bottom: 5px;">Разгрузка: ${Math.round(stats.dischargeHours)} ч</p>
                    <p style="color: #F59E0B; margin-bottom: 5px;">Другое: ${Math.round(stats.otherHours)} ч</p>
                    <p style="color: #9CA3AF; margin-top: 10px;"><strong>Операций:</strong> ${stats.operations}</p>
                    <p style="color: #9CA3AF;"><strong>Судов:</strong> ${stats.assets.size}</p>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Add detailed table
    html += `
        <h3 style="margin-top: 40px; color: #F8FAFC;">Детализация по Операциям</h3>
        <table>
            <thead>
                <tr>
                    <th>Причал</th>
                    <th>Актив</th>
                    <th>Рейс</th>
                    <th>Тип</th>
                    <th>Начало</th>
                    <th>Окончание</th>
                    <th>Часы</th>
                </tr>
            </thead>
            <tbody>
                ${berthLegs.sort((a, b) => a.ConsumesBerthID.localeCompare(b.ConsumesBerthID) || new Date(a.StartDateTime) - new Date(b.StartDateTime)).map(leg => `
                    <tr>
                        <td>${leg.ConsumesBerthID}</td>
                        <td>${leg.AssetID}</td>
                        <td>${leg.VoyageID}</td>
                        <td>${leg.OpDetail || leg.LegType}</td>
                        <td>${new Date(leg.StartDateTime).toLocaleString('ru-RU')}</td>
                        <td>${new Date(leg.EndDateTime).toLocaleString('ru-RU')}</td>
                        <td>${leg.DurationHours}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

// Download berth utilization as Excel
function downloadBerthUtilization() {
    if (!data.calculatedLegs || !data.calculatedLegs.length) {
        alert('Нет данных для экспорта. Сначала рассчитайте рейсы.');
        return;
    }
    
    const berthLegs = data.calculatedLegs.filter(leg => leg.ConsumesBerthID);
    
    if (berthLegs.length === 0) {
        alert('Нет данных о причалах для экспорта.');
        return;
    }
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    
    // Calculate statistics
    const berthStats = {};
    const allDates = berthLegs.map(l => new Date(l.StartDateTime));
    const minDate = new Date(Math.min(...allDates));
    const maxDate = new Date(Math.max(...berthLegs.map(l => new Date(l.EndDateTime))));
    const totalHours = (maxDate - minDate) / (1000 * 60 * 60);
    
    berthLegs.forEach(leg => {
        if (!berthStats[leg.ConsumesBerthID]) {
            berthStats[leg.ConsumesBerthID] = {
                totalHours: 0,
                loadingHours: 0,
                dischargeHours: 0,
                otherHours: 0,
                operations: 0,
                assets: new Set()
            };
        }
        
        const stats = berthStats[leg.ConsumesBerthID];
        stats.totalHours += leg.DurationHours;
        stats.operations++;
        stats.assets.add(leg.AssetID);
        
        const opCode = getOpCode(leg.LegType, leg.OpDetail);
        if (opCode === 'LD') {
            stats.loadingHours += leg.DurationHours;
        } else if (opCode === 'DS') {
            stats.dischargeHours += leg.DurationHours;
        } else {
            stats.otherHours += leg.DurationHours;
        }
    });
    
    // Summary sheet
    const summaryData = Object.keys(berthStats).sort().map(berthId => {
        const stats = berthStats[berthId];
        const utilization = ((stats.totalHours / totalHours) * 100).toFixed(2);
        
        return {
            'Причал': berthId,
            'Загрузка %': utilization,
            'Всего Часов': Math.round(stats.totalHours),
            'Часы Погрузки': Math.round(stats.loadingHours),
            'Часы Разгрузки': Math.round(stats.dischargeHours),
            'Другие Часы': Math.round(stats.otherHours),
            'Количество Операций': stats.operations,
            'Количество Судов': stats.assets.size
        };
    });
    
    const summarySheet = XLSX.utils.json_to_sheet(summaryData);
    XLSX.utils.book_append_sheet(wb, summarySheet, 'Сводка Загрузки');
    
    // Details sheet
    const detailsData = berthLegs.sort((a, b) =>
        a.ConsumesBerthID.localeCompare(b.ConsumesBerthID) ||
        new Date(a.StartDateTime) - new Date(b.StartDateTime)
    ).map(leg => ({
        'Причал': leg.ConsumesBerthID,
        'Актив': leg.AssetID,
        'ID Рейса': leg.VoyageID,
        'Тип Операции': leg.OpDetail || leg.LegType,
        'Начало': new Date(leg.StartDateTime).toLocaleString('ru-RU'),
        'Окончание': new Date(leg.EndDateTime).toLocaleString('ru-RU'),
        'Часы': leg.DurationHours,
        'Тип Груза': leg.CargoType,
        'Количество MT': leg.Qty_MT
    }));
    
    const detailsSheet = XLSX.utils.json_to_sheet(detailsData);
    XLSX.utils.book_append_sheet(wb, detailsSheet, 'Детали Операций');
    
    // Save file
    const fileName = `berth_utilization_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, fileName);
}

// Override the original displayGantt with the enhanced version
if (typeof window !== 'undefined') {
    window.displayGanttOriginal = window.displayGantt;
    window.displayGantt = displayGanttWithDates;
}
