/**
 * Gantt Chart Service
 * Wraps the existing gantt-chart.js module with TypeScript and Vue reactive integration
 */

import type { Voyage } from '@/types/voyage.types'

export interface GanttDay {
  operation: string
  class: string
}

export interface GanttRow {
  vessel: string
  days: GanttDay[]
}

export interface GanttLeg {
  type: 'ballast' | 'loading' | 'transit' | 'discharge' | 'canal' | 'bunker' | 'waiting'
  duration: number
  start_time?: string
  end_time?: string
  leg_type?: string
}

export interface GanttVoyage extends Omit<Voyage, 'legs' | 'startDate'> {
  legs: GanttLeg[]
  startDate: string | Date
  vessel?: string
}

const operationMap: Record<string, { label: string; class: string }> = {
  ballast: { label: 'Б', class: 'ballast' },
  loading: { label: 'П', class: 'loading' },
  transit: { label: 'Т', class: 'transit' },
  discharge: { label: 'В', class: 'discharge' },
  canal: { label: 'К', class: 'canal' },
  bunker: { label: 'Ф', class: 'bunker' },
  waiting: { label: 'О', class: 'waiting' },
}

/**
 * Generate Gantt chart data from voyages
 */
export async function generateGanttFromVoyages(
  voyages: GanttVoyage[],
  days = 30
): Promise<GanttRow[]> {
  const gantt: GanttRow[] = []
  const startDate = new Date()

  // Get unique vessels from voyages
  const vessels = Array.from(new Set(voyages.map((v) => v.vesselId || v.vessel)))
    .map((id) => ({
      id,
      name: voyages.find((v) => (v.vesselId || v.vessel) === id)?.vessel || String(id),
    }))

  vessels.forEach((vessel) => {
    const row: GanttRow = { vessel: vessel.name, days: [] }

    // Initialize all days as empty
    for (let i = 0; i < days; i++) {
      row.days.push({ operation: '', class: '' })
    }

    // Find voyages for this vessel
    const vesselVoyages = voyages.filter(
      (v) => (v.vesselId || v.vessel) === vessel.id
    )

    vesselVoyages.forEach((voyage) => {
      const voyageStart = new Date(voyage.startDate)
      const dayOffset = Math.floor(
        (voyageStart.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
      )

      if (dayOffset < 0 || dayOffset >= days) return // Voyage outside timeline

      let currentDay = dayOffset

      // Plot each leg on the timeline
      if (voyage.legs) {
        voyage.legs.forEach((leg) => {
          const durationDays = Math.ceil((leg.duration || 0) / 24) // Convert hours to days
          const opInfo = operationMap[leg.type] || { label: '?', class: 'waiting' }

          for (let i = 0; i < durationDays && currentDay < days; i++) {
            if (currentDay >= 0) {
              row.days[currentDay] = {
                operation: opInfo.label,
                class: opInfo.class,
              }
            }
            currentDay++
          }
        })
      }
    })

    gantt.push(row)
  })

  return gantt
}

/**
 * Generate Gantt chart data from API or computation
 */
export async function generateGanttData(days = 30): Promise<GanttRow[]> {
  try {
    // Try to fetch from API
    const response = await fetch('/api/gantt-data')
    if (!response.ok) {
      throw new Error('Failed to fetch Gantt data from API')
    }

    const result = await response.json()
    return generateGanttFromAPI(result.assets || {}, days)
  } catch (error) {
    console.error('Error fetching Gantt data:', error)
    // Return empty array on error
    return []
  }
}

/**
 * Generate Gantt from API response
 */
function generateGanttFromAPI(
  assets: Record<string, GanttLeg[]>,
  days = 30
): GanttRow[] {
  const gantt: GanttRow[] = []
  const startDate = new Date()

  Object.keys(assets).forEach((assetName) => {
    const legs = assets[assetName]
    const row: GanttRow = { vessel: assetName, days: [] }

    // Initialize all days as empty
    for (let i = 0; i < days; i++) {
      row.days.push({ operation: '', class: '' })
    }

    legs?.forEach((leg) => {
      if (leg.start_time && leg.end_time) {
        const legStart = new Date(leg.start_time)
        const legEnd = new Date(leg.end_time)
        const duration = Math.ceil(
          (legEnd.getTime() - legStart.getTime()) / (1000 * 60 * 60 * 24)
        )

        const dayIndex = Math.floor(
          (legStart.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
        )

        if (dayIndex >= 0 && dayIndex < days) {
          const opInfo = operationMap[leg.leg_type || leg.type] || {
            label: '?',
            class: 'waiting',
          }

          for (let i = 0; i < duration && dayIndex + i < days; i++) {
            row.days[dayIndex + i] = {
              operation: opInfo.label,
              class: opInfo.class,
            }
          }
        }
      }
    })

    gantt.push(row)
  })

  return gantt
}

/**
 * Export Gantt chart to Excel
 */
export async function exportGantt(): Promise<void> {
  const now = new Date()
  const yearMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`

  const response = await fetch('/api/export/excel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      type: 'gantt',
      year_month: yearMonth,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Failed to export Gantt chart')
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `gantt_chart_${yearMonth}.xlsx`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}
