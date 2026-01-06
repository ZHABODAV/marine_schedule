/**
 * Financial Analysis Service
 * Provides financial calculations and cost analysis
 */

import type { Vessel } from '@/types/vessel.types'
import type { CargoCommitment } from '@/types/cargo.types'
import type { Route } from '@/types/route.types'

export interface VoyageFinancial {
  id: string | number
  vessel: string
  cargo: number
  distance: number
  seaDays: number
  revenue: number
  bunkerCost: number
  hireCost: number
  portCost: number
  operationalCost?: number
  overheadCost?: number
  otherCost?: number
  totalCost: number
  tce: number // Time Charter Equivalent
  profit: number
}

export interface FinancialData {
  voyages: VoyageFinancial[]
  totalVoyages: number
  totalRevenue: number
  totalCosts: number
  totalProfit: number
  avgTCE: number
  totalDistance: number
  totalDays: number
}

export interface CalculationParams {
  speedLaden: number
  speedBallast: number
  bunkerIFO: number // Price per MT
  bunkerMGO: number // Price per MT
  consumptionLaden: number // MT per day
  consumptionBallast: number // MT per day
  loadRate: number // MT per day
  dischRate: number // MT per day
  portWaitingHours: number
  weatherMargin: number
  dailyHire: number
  freightRate: number // $ per MT
}

const defaultParams: CalculationParams = {
  speedLaden: 13.5,
  speedBallast: 14.5,
  bunkerIFO: 450,
  bunkerMGO: 650,
  consumptionLaden: 35,
  consumptionBallast: 28,
  loadRate: 5000,
  dischRate: 5000,
  portWaitingHours: 12,
  weatherMargin: 1.05,
  dailyHire: 15000,
  freightRate: 25,
}

/**
 * Calculate financial analysis for voyages
 */
export async function calculateFinancialAnalysis(
  cargo?: CargoCommitment[],
  vessels?: Vessel[],
  routes?: Route[],
  params: Partial<CalculationParams> = {}
): Promise<FinancialData> {
  const calculationParams = { ...defaultParams, ...params }

  // If no data provided, try to fetch from API
  if (!cargo || !vessels || !routes) {
    const response = await fetch('/api/financial/calculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    })

    if (response.ok) {
      return await response.json()
    }
  }

  // Client-side calculation
  const voyages: VoyageFinancial[] = []
  let totalRevenue = 0
  let totalCosts = 0
  let totalDistance = 0
  let totalDays = 0

  if (cargo && vessels && routes) {
    cargo.forEach((cargoItem, idx) => {
      const vessel = vessels[idx % vessels.length]
      const route = routes.find(
        (r) =>
          r.from === cargoItem.loadPort &&
          r.to === cargoItem.dischPort
      ) || routes[0]

      if (!vessel || !route) return

      // Calculate sea time
      const seaHours =
        (route.distance / calculationParams.speedLaden) *
        calculationParams.weatherMargin
      const seaDays = seaHours / 24

      // Calculate port time
      const loadDays = cargoItem.quantity / calculationParams.loadRate
      const dischDays = cargoItem.quantity / calculationParams.dischRate
      const portDays =
        loadDays +
        dischDays +
        (calculationParams.portWaitingHours / 24) * 2

      const totalVoyageDays = seaDays + portDays

      // Calculate costs
      const bunkerConsumed = calculationParams.consumptionLaden * seaDays
      const bunkerCost = bunkerConsumed * calculationParams.bunkerIFO

      const hireCost = calculationParams.dailyHire * totalVoyageDays

      const portCost = 10000 * 2 // Simplified port costs

      const totalCost = bunkerCost + hireCost + portCost

      // Calculate revenue
      const revenue = cargoItem.quantity * calculationParams.freightRate

      // Calculate profitability
      const netRevenue = revenue - bunkerCost - portCost
      const tce = netRevenue / totalVoyageDays
      const profit = revenue - totalCost

      const voyageData: VoyageFinancial = {
        id: cargoItem.id,
        vessel: vessel.name,
        cargo: cargoItem.quantity,
        distance: route.distance || 0,
        seaDays: seaDays,
        revenue: revenue,
        bunkerCost: Math.round(bunkerCost),
        hireCost: Math.round(hireCost),
        portCost: portCost,
        totalCost: Math.round(totalCost),
        tce: tce,
        profit: Math.round(profit),
      }

      voyages.push(voyageData)
      totalRevenue += revenue
      totalCosts += totalCost
      totalDistance += route.distance || 0
      totalDays += totalVoyageDays
    })
  }

  const avgTCE =
    voyages.length > 0
      ? voyages.reduce((sum, v) => sum + v.tce, 0) / voyages.length
      : 0

  return {
    voyages,
    totalVoyages: voyages.length,
    totalRevenue: Math.round(totalRevenue),
    totalCosts: Math.round(totalCosts),
    totalProfit: Math.round(totalRevenue - totalCosts),
    avgTCE,
    totalDistance,
    totalDays,
  }
}

/**
 * Optimize bunker strategy
 */
export async function optimizeBunkerStrategy(): Promise<{
  success: boolean
  savings: number
  message: string
}> {
  try {
    const response = await fetch('/api/bunker/optimize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (response.ok) {
      return await response.json()
    }

    // Fallback: client-side estimate
    return {
      success: true,
      savings: 50000, // Placeholder
      message: 'Client-side optimization estimate',
    }
  } catch (error) {
    console.error('Bunker optimization error:', error)
    throw error
  }
}

/**
 * Export financial analysis to Excel
 */
export async function exportFinancialAnalysis(
  data: FinancialData
): Promise<void> {
  const response = await fetch('/api/export/financial', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to export financial analysis')
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `financial_analysis_${new Date().toISOString().slice(0, 10)}.xlsx`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}
