// ===== NETWORK VISUALIZATION MODULE =====
// Purpose: Network graph visualization for ports, plants, and routes
// Lines extracted from vessel_scheduler_enhanced.js: 2399-2615

import { appState, getCurrentData } from '../core/app-state.js';
import { toNumber, showNotification } from '../core/utils.js';

// ===== NETWORK VISUALIZATION =====
export function renderNetwork() {
    const data = getCurrentData();
    const container = document.getElementById('networkGraph');
    
    if (!container) return;

    const nodes = [];
    const edges = [];
    const nodeIds = new Set();

    // Add ports as nodes
    data.masters.ports.forEach(port => {
        nodes.push({
            id: port.name,
            label: port.name,
            group: 'port',
            title: `Порт: ${port.name}\nСтрана: ${port.country || 'Н/Д'}`
        });
        nodeIds.add(port.name);
    });

    // Add plants from rail cargo origin stations
    data.planning.railCargo.forEach(rc => {
        const plantId = rc.origin_station || rc.origin;
        if (plantId && !nodeIds.has(plantId)) {
            nodes.push({
                id: plantId,
                label: plantId,
                group: 'plant',
                title: `Завод: ${plantId}`
            });
            nodeIds.add(plantId);
        }
    });

    // Add edges from routes (sea)
    data.masters.routes.forEach(route => {
        if (nodeIds.has(route.from) && nodeIds.has(route.to)) {
            edges.push({
                from: route.from,
                to: route.to,
                label: `${route.distance} nm`,
                title: `Маршрут: ${route.from} → ${route.to}\nДистанция: ${route.distance} nm`,
                color: { color: '#4a9eff' },
                width: 2
            });
        }
    });

    // Add edges from rail cargo (rail)
    data.planning.railCargo.forEach(rc => {
        const from = rc.origin_station || rc.origin;
        const to = rc.destination_port || rc.destination;
        if (from && to && nodeIds.has(from) && nodeIds.has(to)) {
            edges.push({
                from: from,
                to: to,
                label: 'ЖД',
                title: `ЖД: ${from} → ${to}`,
                color: { color: '#00b894' },
                width: 1,
                dashes: true
            });
        }
    });

    const graphData = { nodes, edges };
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#e4e6eb'
            },
            borderWidth: 2
        },
        edges: {
            arrows: { to: { enabled: true, scaleFactor: 0.5 } },
            smooth: { type: 'continuous' }
        },
        groups: {
            port: { color: { background: '#0984e3', border: '#0984e3' }, shape: 'circle' },
            plant: { color: { background: '#00b894', border: '#00b894' }, shape: 'square' }
        },
        physics: {
            stabilization: true,
            barnesHut: {
                gravitationalConstant: -2000,
                springConstant: 0.001,
                springLength: 200
            }
        },
        configure: {
            enabled: false
        }
    };

    const network = new vis.Network(container, graphData, options);
    
    showNotification(`Сеть построена: ${nodes.length} узлов, ${edges.length} связей`, 'success');
}

export function exportNetworkSnapshot() {
    try {
        showNotification('Генерация снимка сети...', 'info');
        
        const data = getCurrentData();
        const wb = XLSX.utils.book_new();
        
        // Nodes sheet (Ports + Plants)
        const nodesData = [];
        nodesData.push(['ID', 'Тип', 'Название', 'Страна', 'Широта', 'Долгота', 'Скор. погр.', 'Скор. выгр.']);
        
        // Add ports
        data.masters.ports.forEach(port => {
            nodesData.push([
                port.id || port.name,
                'Порт',
                port.name,
                port.country || '',
                port.latitude || '',
                port.longitude || '',
                port.loadRate || '',
                port.dischRate || ''
            ]);
        });
        
        // Add plants from rail cargo
        const plants = new Set();
        data.planning.railCargo.forEach(rc => {
            const plantId = rc.origin_station || rc.origin;
            if (plantId && !plants.has(plantId)) {
                plants.add(plantId);
                nodesData.push([
                    plantId,
                    'Завод',
                    plantId,
                    '',
                    '',
                    '',
                    '',
                    ''
                ]);
            }
        });
        
        const nodesWs = XLSX.utils.aoa_to_sheet(nodesData);
        XLSX.utils.book_append_sheet(wb, nodesWs, 'Узлы');
        
        // Edges sheet (Routes + Rail connections)
        const edgesData = [];
        edgesData.push(['Откуда', 'Куда', 'Тип', 'Дистанция (nm)', 'Канал', 'Поток (MT/год)']);
        
        // Add sea routes
        data.masters.routes.forEach(route => {
            edgesData.push([
                route.from,
                route.to,
                'Море',
                route.distance || '',
                route.canal || '',
                ''
            ]);
        });
        
        // Add rail routes with aggregated flow
        const railFlow = {};
        data.planning.railCargo.forEach(rc => {
            const from = rc.origin_station || rc.origin;
            const to = rc.destination_port || rc.destination;
            if (from && to) {
                const key = `${from}->${to}`;
                railFlow[key] = (railFlow[key] || 0) + toNumber(rc.qty_mt || rc.quantity);
            }
        });
        
        Object.entries(railFlow).forEach(([key, flow]) => {
            const [from, to] = key.split('->');
            edgesData.push([
                from,
                to,
                'ЖД',
                '',
                '',
                Math.round(flow)
            ]);
        });
        
        const edgesWs = XLSX.utils.aoa_to_sheet(edgesData);
        XLSX.utils.book_append_sheet(wb, edgesWs, 'Связи');
        
        // Summary sheet
        const summaryData = [
            ['Сводка сети', ''],
            ['Всего узлов', nodesData.length - 1],
            ['Порты', data.masters.ports.length],
            ['Заводы', plants.size],
            ['Всего связей', edgesData.length - 1],
            ['Морские маршруты', data.masters.routes.length],
            ['ЖД маршруты', Object.keys(railFlow).length],
            ['Сгенерировано', new Date().toLocaleString('ru-RU')]
        ];
        
        const summaryWs = XLSX.utils.aoa_to_sheet(summaryData);
        XLSX.utils.book_append_sheet(wb, summaryWs, 'Сводка');
        
        const fileName = `network_snapshot_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('Снимок сети успешно выгружен!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте сети', 'error');
    }
}

// Export all functions
export const networkViz = {
    renderNetwork,
    exportNetworkSnapshot
};
