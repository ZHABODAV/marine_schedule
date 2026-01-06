<template>
  <div class="voyage-builder">
    <div class="builder-header">
      <h1>Voyage Builder</h1>
      <p class="subtitle">Create a new voyage using our step-by-step wizard</p>
    </div>

    <!-- Wizard Steps -->
    <div class="wizard-steps">
      <div 
        v-for="(step, index) in steps" 
        :key="index"
        class="step"
        :class="{
          'active': currentStep === index,
          'completed': index < currentStep,
          'disabled': index > currentStep
        }"
      >
        <div class="step-indicator">
          <span v-if="index < currentStep" class="checkmark"></span>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-label">
          <span class="step-title">{{ step.title }}</span>
          <span class="step-description">{{ step.description }}</span>
        </div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="wizard-content">
      <form @submit.prevent="handleNext">
        <!-- Step 1: Basic Information -->
        <div v-if="currentStep === 0" class="step-content">
          <h2>Basic Information</h2>
          
          <div class="form-group">
            <label for="module">Module *</label>
            <select id="module" v-model="formData.module" required>
              <option value="">Select a module</option>
              <option value="olya">Olya</option>
              <option value="balakovo">Balakovo</option>
              <option value="deepsea">Deep Sea</option>
            </select>
            <span v-if="validationErrors.module" class="error">{{ validationErrors.module }}</span>
          </div>

          <div class="form-group">
            <label for="vessel">Vessel *</label>
            <select id="vessel" v-model="formData.vesselId" required @change="onVesselChange">
              <option value="">Select a vessel</option>
              <option v-for="vessel in vessels" :key="vessel.id" :value="vessel.id">
                {{ vessel.name }} ({{ vessel.type }}) - Capacity: {{ vessel.capacity || 'N/A' }} tons
              </option>
            </select>
            <span v-if="validationErrors.vesselId" class="error">{{ validationErrors.vesselId }}</span>
            <!-- Real-time capacity info -->
            <div v-if="selectedVessel" class="vessel-info">
              <span class="info-label">Deadweight:</span> {{ selectedVessel.capacity || 'N/A' }} tons
              <span class="info-label" style="margin-left: 1rem;">Speed:</span> {{ selectedVessel.speed || 'N/A' }} knots
            </div>
          </div>

          <div class="form-group">
            <label for="startDate">Start Date *</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="formData.startDate" 
              required
              :min="minDate"
            />
            <span v-if="validationErrors.startDate" class="error">{{ validationErrors.startDate }}</span>
          </div>

          <div class="form-group">
            <label for="voyageType">Voyage Type</label>
            <select id="voyageType" v-model="formData.voyageType">
              <option value="standard">Standard</option>
              <option value="ballast">Ballast</option>
              <option value="laden">Laden</option>
            </select>
          </div>
        </div>

        <!-- Step 2: Route Configuration -->
        <div v-if="currentStep === 1" class="step-content">
          <h2>Route Configuration</h2>

          <div class="route-toolbar">
            <div class="form-group" style="margin-bottom: 0;">
              <label for="route">Select Route / Template</label>
              <select id="route" v-model="selectedRoute" @change="onRouteChange">
                <option value="">Custom Route</option>
                <optgroup label="Standard Routes">
                  <option v-for="route in routes" :key="route.id" :value="route.id">
                    {{ route.name }} ({{ route.distance || 0 }} nm)
                  </option>
                </optgroup>
                <optgroup label="Templates" v-if="templates.length > 0">
                  <option v-for="template in templates" :key="`template_${template.id}`" :value="`template_${template.id}`">
                    {{ template.name }} - {{ template.estimatedDays }} days
                  </option>
                </optgroup>
              </select>
            </div>

            <!-- Bulk Operations Buttons -->
            <div class="bulk-operations">
              <button type="button" class="btn-icon" @click="showBulkDeleteDialog" :disabled="selectedLegs.length === 0" title="Delete Selected">
                Delete ({{ selectedLegs.length }})
              </button>
              <button type="button" class="btn-icon" @click="duplicateSelectedLegs" :disabled="selectedLegs.length === 0" title="Duplicate Selected">
                Duplicate ({{ selectedLegs.length }})
              </button>
              <button type="button" class="btn-icon" @click="optimizeRoute" :disabled="formData.legs.length < 2" title="Optimize Route">
                Optimize
              </button>
            </div>
          </div>

          <!-- Capacity Validation Alert -->
          <div v-if="capacityValidation.exceeded" class="alert alert-error">
            Total cargo ({{ capacityValidation.totalCargo }} tons) exceeds vessel capacity ({{ capacityValidation.vesselCapacity }} tons)!
            Overload: {{ capacityValidation.overload }} tons
          </div>
          <div v-else-if="capacityValidation.totalCargo > 0" class="alert alert-success">
             Cargo within limits: {{ capacityValidation.totalCargo }} / {{ capacityValidation.vesselCapacity }} tons
            ({{ capacityValidation.utilizationPercent }}% utilization)
          </div>

          <!-- Route Optimization Suggestions -->
          <div v-if="optimizationSuggestions.length > 0" class="optimization-panel">
            <h4>Route Optimization Suggestions</h4>
            <div class="suggestions-list">
              <div v-for="(suggestion, idx) in optimizationSuggestions" :key="idx" class="suggestion-item">
                <span class="suggestion-icon">{{ suggestion.icon }}</span>
                <span class="suggestion-text">{{ suggestion.message }}</span>
                <button v-if="suggestion.action" type="button" class="btn-apply" @click="applySuggestion(suggestion)">
                  Apply
                </button>
              </div>
            </div>
          </div>

          <!-- Cost Preview -->
          <div v-if="costPreview.total > 0" class="cost-preview">
            <h4>Estimated Voyage Cost</h4>
            <div class="cost-breakdown">
              <div class="cost-item">
                <span>Fuel Cost:</span>
                <span>${{ costPreview.fuel.toLocaleString() }}</span>
              </div>
              <div class="cost-item">
                <span>Port Fees:</span>
                <span>${{ costPreview.portFees.toLocaleString() }}</span>
              </div>
              <div class="cost-item">
                <span>Canal Fees:</span>
                <span>${{ costPreview.canalFees.toLocaleString() }}</span>
              </div>
              <div class="cost-item">
                <span>Other Costs:</span>
                <span>${{ costPreview.other.toLocaleString() }}</span>
              </div>
              <div class="cost-item total">
                <span><strong>Total Estimated Cost:</strong></span>
                <span><strong>${{ costPreview.total.toLocaleString() }}</strong></span>
              </div>
              <div class="cost-item">
                <span>Cost per nm:</span>
                <span>${{ costPreview.perNm.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <div class="route-legs">
            <h3>
              Route Legs 
              <span class="leg-count">({{ formData.legs.length }} legs, {{ totalDistance }} nm, ~{{ estimatedDays }} days)</span>
              <label class="select-all">
                <input type="checkbox" @change="toggleSelectAll" :checked="allLegsSelected" />
                Select All
              </label>
            </h3>
            
            <!-- Draggable Legs -->
            <draggable
              v-model="formData.legs"
              item-key="id"
              handle=".drag-handle"
              animation="200"
              ghost-class="ghost"
              @start="onDragStart"
              @end="onDragEnd"
              class="legs-container"
              tag="div"
            >
              <template #item="{ element: leg, index }">
                <div class="leg-item" :class="{ 'selected': selectedLegs.includes(index) }">
                  <div class="leg-header">
                    <input 
                      type="checkbox" 
                      :checked="selectedLegs.includes(index)" 
                      @change="toggleLegSelection(index)"
                      class="leg-checkbox"
                    />
                    <span class="drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="leg-number">Leg {{ index + 1 }}</span>
                    <div class="leg-actions">
                      <button
                        type="button"
                        class="btn-icon-small"
                        @click="duplicateLeg(index)"
                        title="Duplicate leg"
                      >
                        
                      </button>
                      <button 
                        type="button" 
                        class="remove-leg-btn" 
                        @click="removeLeg(index)"
                        v-if="formData.legs.length > 1"
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  <div class="leg-fields">
                    <div class="form-group">
                      <label>Type *</label>
                      <select v-model="leg.type" required @change="onLegTypeChange(index)">
                        <option value="loading">Loading</option>
                        <option value="transit">Transit</option>
                        <option value="discharge">Discharge</option>
                        <option value="ballast">Ballast</option>
                        <option value="canal">Canal</option>
                        <option value="bunker">Bunker</option>
                        <option value="waiting">Waiting</option>
                      </select>
                    </div>

                    <div class="form-group">
                      <label>From Port</label>
                      <input type="text" v-model="leg.from" placeholder="Start port" />
                    </div>

                    <div class="form-group">
                      <label>To Port</label>
                      <input type="text" v-model="leg.to" placeholder="End port" />
                    </div>

                    <div class="form-group">
                      <label>Distance (nm)</label>
                      <input 
                        type="number" 
                        v-model.number="leg.distance" 
                        min="0" 
                        step="0.1" 
                        placeholder="Distance"
                        @input="recalculateCosts"
                      />
                    </div>

                    <div class="form-group">
                      <label>Duration (hours)</label>
                      <input 
                        type="number" 
                        v-model.number="leg.duration" 
                        min="0" 
                        step="0.1" 
                        placeholder="Duration"
                      />
                    </div>

                    <div class="form-group" v-if="['loading', 'discharge'].includes(leg.type)">
                      <label>Cargo (tons)</label>
                      <input 
                        type="number" 
                        v-model.number="leg.cargo" 
                        min="0" 
                        step="0.1" 
                        placeholder="Cargo amount"
                        @input="validateCapacity"
                      />
                    </div>
                  </div>
                </div>
              </template>
            </draggable>

            <button type="button" class="add-leg-btn" @click="addLeg">
              + Add Leg
            </button>
          </div>
        </div>

        <!-- Step 3: Cargo Details (Optional) -->
        <div v-if="currentStep === 2" class="step-content">
          <h2>Cargo Details</h2>

          <div class="form-group">
            <label for="cargo">Cargo Commitment</label>
            <select id="cargo" v-model="formData.commitmentId">
              <option value="">None</option>
              <option v-for="cargo in cargoList" :key="cargo.id" :value="cargo.id">
                {{ cargo.commodity }} - {{ cargo.quantity }} tons
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="totalCargo">Total Cargo (tons)</label>
            <input 
              type="number" 
              id="totalCargo" 
              v-model.number="formData.totalCargo" 
              min="0" 
              step="0.1" 
              placeholder="Total cargo amount"
            />
          </div>

          <div class="form-group">
            <label for="notes">Notes</label>
            <textarea 
              id="notes" 
              v-model="formData.notes" 
              rows="4" 
              placeholder="Enter any additional notes..."
            ></textarea>
          </div>
        </div>

        <!-- Step 4: Review & Submit -->
        <div v-if="currentStep === 3" class="step-content">
          <h2>Review & Submit</h2>

          <div class="review-section">
            <h3>Basic Information</h3>
            <div class="review-item">
              <span class="review-label">Module:</span>
              <span class="review-value">{{ formData.module || 'Not selected' }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Vessel:</span>
              <span class="review-value">{{ getVesselName(formData.vesselId) || 'Not selected' }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Start Date:</span>
              <span class="review-value">{{ formatDate(formData.startDate) }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Type:</span>
              <span class="review-value">{{ formData.voyageType }}</span>
            </div>
          </div>

          <div class="review-section">
            <h3>Route Summary</h3>
            <div class="review-item">
              <span class="review-label">Total Legs:</span>
              <span class="review-value">{{ formData.legs.length }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Total Distance:</span>
              <span class="review-value">{{ totalDistance }} nm</span>
            </div>
            <div class="review-item">
              <span class="review-label">Estimated Duration:</span>
              <span class="review-value">{{ estimatedDuration }} hours (~{{ estimatedDays }} days)</span>
            </div>
            <div class="review-item">
              <span class="review-label">Total Cargo:</span>
              <span class="review-value">{{ capacityValidation.totalCargo }} tons</span>
            </div>
          </div>

          <div class="review-section">
            <h3>Cost Estimate</h3>
            <div class="review-item">
              <span class="review-label">Fuel Cost:</span>
              <span class="review-value">${{ costPreview.fuel.toLocaleString() }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Port & Canal Fees:</span>
              <span class="review-value">${{ (costPreview.portFees + costPreview.canalFees).toLocaleString() }}</span>
            </div>
            <div class="review-item">
              <span class="review-label">Total Estimated Cost:</span>
              <span class="review-value"><strong>${{ costPreview.total.toLocaleString() }}</strong></span>
            </div>
          </div>

          <div v-if="formData.commitmentId || formData.totalCargo || formData.notes" class="review-section">
            <h3>Additional Details</h3>
            <div class="review-item" v-if="formData.totalCargo">
              <span class="review-label">Manual Cargo Entry:</span>
              <span class="review-value">{{ formData.totalCargo }} tons</span>
            </div>
            <div class="review-item" v-if="formData.notes">
              <span class="review-label">Notes:</span>
              <span class="review-value">{{ formData.notes }}</span>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="wizard-actions">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="handlePrevious" 
            v-if="currentStep > 0"
          >
            Previous
          </button>
          
          <button 
            type="submit" 
            class="btn btn-primary" 
            v-if="currentStep < steps.length - 1"
          >
            Next
          </button>
          
          <button 
            type="button" 
            class="btn btn-success" 
            @click="handleSubmit" 
            v-if="currentStep === steps.length - 1"
            :disabled="submitting"
          >
            {{ submitting ? 'Creating...' : 'Create Voyage' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useVesselStore } from '@/stores/vessel'
import { useVoyageStore } from '@/stores/voyage'
import { useCargoStore } from '@/stores/cargo'
import { useRouteStore } from '@/stores/route'
import type { VoyageLeg } from '@/types/voyage.types'
import draggable from 'vuedraggable'
import axios from 'axios'

// Debug: Check if draggable component is loaded
console.log('🔍 DEBUG: vuedraggable component loaded:', draggable)
console.log('🔍 DEBUG: vuedraggable type:', typeof draggable)

const router = useRouter()
const vesselStore = useVesselStore()
const voyageStore = useVoyageStore()
const cargoStore = useCargoStore()
const routeStore = useRouteStore()

const steps = [
  { title: 'Basic Info', description: 'Vessel and dates' },
  { title: 'Route', description: 'Configure route legs' },
  { title: 'Cargo', description: 'Cargo details' },
  { title: 'Review', description: 'Review and submit' }
]

const currentStep = ref(0)
const submitting = ref(false)
const selectedRoute = ref('')
const drag = ref(false)
const selectedLegs = ref<number[]>([])
const templates = ref<any[]>([])
const distanceMatrix = ref<Record<string, any>>({})

interface VoyageFormData {
  module: string
  vesselId: string
  startDate: string
  voyageType: string
  legs: VoyageLeg[]
  commitmentId?: string
  totalCargo?: number
  notes?: string
}

const formData = ref<VoyageFormData>({
  module: '',
  vesselId: '',
  startDate: '',
  voyageType: 'standard',
  legs: [
    {
      id: generateId(),
      type: 'loading',
      from: '',
      to: '',
      distance: 0,
      duration: 0
    }
  ]
})

const validationErrors = ref<Record<string, string>>({})
const optimizationSuggestions = ref<any[]>([])
const costPreview = ref({
  fuel: 0,
  portFees: 0,
  canalFees: 0,
  other: 0,
  total: 0,
  perNm: 0
})

const vessels = computed(() => vesselStore.vessels)
const routes = computed(() => routeStore.routes)
const cargoList = computed(() => cargoStore.cargoList)

const selectedVessel = computed(() => {
  return vessels.value.find(v => v.id === formData.value.vesselId)
})

const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const totalDistance = computed(() => {
  return formData.value.legs.reduce((sum, leg) => sum + (leg.distance || 0), 0).toFixed(1)
})

const estimatedDuration = computed(() => {
  return formData.value.legs.reduce((sum, leg) => sum + (leg.duration || 0), 0).toFixed(1)
})

const estimatedDays = computed(() => {
  return Math.ceil(parseFloat(estimatedDuration.value) / 24)
})

const allLegsSelected = computed(() => {
  return formData.value.legs.length > 0 && selectedLegs.value.length === formData.value.legs.length
})

// Real-time capacity validation
const capacityValidation = computed(() => {
  const vessel = selectedVessel.value
  const totalCargo = formData.value.legs
    .filter(leg => ['loading', 'discharge'].includes(leg.type))
    .reduce((sum, leg) => sum + (leg.cargo || 0), 0)
  
  const vesselCapacity = vessel?.capacity || 0
  const exceeded = totalCargo > vesselCapacity
  const overload = exceeded ? totalCargo - vesselCapacity : 0
  const utilizationPercent = vesselCapacity > 0 ? Math.round((totalCargo / vesselCapacity) * 100) : 0

  return {
    totalCargo,
    vesselCapacity,
    exceeded,
    overload,
    utilizationPercent
  }
})

function generateId(): number {
  return Date.now() + Math.floor(Math.random() * 10000)
}

function validateStep(step: number): boolean {
  validationErrors.value = {}
  
  switch (step) {
    case 0: // Basic Information
      if (!formData.value.module) {
        validationErrors.value.module = 'Module is required'
      }
      if (!formData.value.vesselId) {
        validationErrors.value.vesselId = 'Vessel is required'
      }
      if (!formData.value.startDate) {
        validationErrors.value.startDate = 'Start date is required'
      }
      break
      
    case 1: // Route Configuration
      if (formData.value.legs.length === 0) {
        validationErrors.value.legs = 'At least one leg is required'
      }
      if (capacityValidation.value.exceeded) {
        validationErrors.value.capacity = 'Total cargo exceeds vessel capacity'
      }
      formData.value.legs.forEach((leg, index) => {
        if (!leg.type) {
          validationErrors.value[`leg_${index}_type`] = 'Leg type is required'
        }
      })
      break
  }
  
  return Object.keys(validationErrors.value).length === 0
}

function handleNext() {
  if (validateStep(currentStep.value)) {
    currentStep.value++
  }
}

function handlePrevious() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function handleSubmit() {
  if (!validateStep(currentStep.value)) {
    return
  }
  
  submitting.value = true
  
  try {
    const voyageData = {
      vesselId: formData.value.vesselId,
      commitmentId: formData.value.commitmentId,
      legs: formData.value.legs,
      startDate: formData.value.startDate,
      status: 'planned' as const
    }
    
    await voyageStore.createVoyage(voyageData)
    router.push('/schedule')
  } catch (error) {
    console.error('Failed to create voyage:', error)
  } finally {
    submitting.value = false
  }
}

function addLeg() {
  formData.value.legs.push({
    id: generateId(),
    type: 'transit',
    from: '',
    to: '',
    distance: 0,
    duration: 0
  })
}

function removeLeg(index: number) {
  if (formData.value.legs.length > 1) {
    formData.value.legs.splice(index, 1)
    selectedLegs.value = selectedLegs.value.filter(i => i !== index).map(i => i > index ? i - 1 : i)
  }
}

function duplicateLeg(index: number) {
  const leg = formData.value.legs[index]
  if (!leg) return
  const duplicated: VoyageLeg = {
    ...leg,
    id: generateId(),
    type: leg.type
  }
  formData.value.legs.splice(index + 1, 0, duplicated)
}

function duplicateSelectedLegs() {
  const sorted = [...selectedLegs.value].sort((a, b) => b - a)
  sorted.forEach(index => {
    duplicateLeg(index)
  })
  selectedLegs.value = []
}

function toggleLegSelection(index: number) {
  const idx = selectedLegs.value.indexOf(index)
  if (idx > -1) {
    selectedLegs.value.splice(idx, 1)
  } else {
    selectedLegs.value.push(index)
  }
}

function toggleSelectAll() {
  if (allLegsSelected.value) {
    selectedLegs.value = []
  } else {
    selectedLegs.value = formData.value.legs.map((_, i) => i)
  }
}

function showBulkDeleteDialog() {
  if (selectedLegs.value.length === 0) return
  
  if (confirm(`Delete ${selectedLegs.value.length} selected leg(s)?`)) {
    const sorted = [...selectedLegs.value].sort((a, b) => b - a)
    sorted.forEach(index => {
      if (formData.value.legs.length > 1) {
        formData.value.legs.splice(index, 1)
      }
    })
    selectedLegs.value = []
  }
}

function onRouteChange() {
  if (selectedRoute.value) {
    // Check if template
    if (selectedRoute.value.startsWith('template_')) {
      const templateId = selectedRoute.value.replace('template_', '')
      const template = templates.value.find(t => t.id === templateId)
      if (template && template.legs) {
        formData.value.legs = template.legs.map((leg: any) => ({
          ...leg,
          id: generateId()
        }))
        recalculateCosts()
      }
    } else {
      // Standard route
      const route = routes.value.find(r => r.id === selectedRoute.value)
      if (route) {
        // Routes may not have legs property, create basic leg based on route
        formData.value.legs = [{
          id: generateId(),
          type: 'transit' as const,
          from: route.from,
          to: route.to,
          distance: route.distance,
          duration: 0
        }]
        recalculateCosts()
      }
    }
  }
}

function onVesselChange() {
  validateCapacity()
  recalculateCosts()
}

function onLegTypeChange(index: number) {
  const leg = formData.value.legs[index]
  if (!leg) return
  if (!['loading', 'discharge'].includes(leg.type)) {
    delete leg.cargo
  }
  recalculateCosts()
}

function validateCapacity() {
  // Computed property handles this automatically
}

function optimizeRoute() {
  optimizationSuggestions.value = []
  
  const legs = formData.value.legs
  
  // Check for inefficient routing
  for (let i = 0; i < legs.length - 1; i++) {
    const current = legs[i]
    const next = legs[i + 1]
    
    if (!current || !next) continue
    
    // Check if next leg's "from" doesn't match current leg's "to"
    if (current.to && next.from && current.to !== next.from) {
      optimizationSuggestions.value.push({
        icon: '',
        message: `Leg ${i + 1} ends at ${current.to} but Leg ${i + 2} starts at ${next.from}. Consider adding a transit leg.`,
        action: 'add_transit',
        data: { index: i + 1, from: current.to, to: next.from }
      })
    }
  }
  
  // Check for consecutive same-type legs
  for (let i = 0; i < legs.length - 1; i++) {
    const current = legs[i]
    const next = legs[i + 1]
    
    if (!current || !next) continue
    
    if (current.type === next.type && current.type === 'transit') {
      optimizationSuggestions.value.push({
        icon: '',
        message: `Legs ${i + 1} and ${i + 2} are both transit legs. Consider merging them.`,
        action: 'merge_legs',
        data: { index: i }
      })
    }
  }
  
  // Check for zero-distance legs
  legs.forEach((leg, i) => {
    if (leg.type === 'transit' && (!leg.distance || leg.distance === 0)) {
      optimizationSuggestions.value.push({
        icon: '',
        message: `Leg ${i + 1} is a transit leg with zero distance. Please verify.`,
        action: null,
        data: null
      })
    }
  })
  
  // Utilization suggestions
  const util = capacityValidation.value.utilizationPercent
  if (util < 50) {
    optimizationSuggestions.value.push({
      icon: '',
      message: `Low vessel utilization (${util}%). Consider adding more cargo or using a smaller vessel.`,
      action: null,
      data: null
    })
  } else if (util > 90 && util <= 100) {
    optimizationSuggestions.value.push({
      icon: '',
      message: `Excellent vessel utilization (${util}%)!`,
      action: null,
      data: null
    })
  }
}

function applySuggestion(suggestion: any) {
  if (suggestion.action === 'add_transit') {
    const { index, from, to } = suggestion.data
    const distance = getDistanceBetweenPorts(from, to)
    formData.value.legs.splice(index, 0, {
      id: generateId(),
      type: 'transit',
      from,
      to,
      distance,
      duration: calculateDuration(distance)
    })
    optimizationSuggestions.value = optimizationSuggestions.value.filter(s => s !== suggestion)
    recalculateCosts()
  } else if (suggestion.action === 'merge_legs') {
    const { index } = suggestion.data
    const leg1 = formData.value.legs[index]
    const leg2 = formData.value.legs[index + 1]
    
    if (!leg1 || !leg2) return
    
    leg1.to = leg2.to
    leg1.distance = (leg1.distance || 0) + (leg2.distance || 0)
    leg1.duration = (leg1.duration || 0) + (leg2.duration || 0)
    
    formData.value.legs.splice(index + 1, 1)
    optimizationSuggestions.value = optimizationSuggestions.value.filter(s => s !== suggestion)
    recalculateCosts()
  }
}

function getDistanceBetweenPorts(from: string, to: string): number {
  // Use distance matrix if available
  const key = `${from}-${to}`
  if (distanceMatrix.value[key]) {
    return distanceMatrix.value[key]
  }
  // Default estimate based on common routes (placeholder)
  return 500
}

function calculateDuration(distance: number): number {
  const vessel = selectedVessel.value
  const speed = vessel?.speed || 12 // Default 12 knots
  return Math.round((distance / speed) * 10) / 10
}

function recalculateCosts() {
  const vessel = selectedVessel.value
  if (!vessel) {
    costPreview.value = { fuel: 0, portFees: 0, canalFees: 0, other: 0, total: 0, perNm: 0 }
    return
  }
  
  let fuelCost = 0
  let portFees = 0
  let canalFees = 0
  
  const fuelPricePerTon = 600 // USD
  const fuelConsumptionPerNm = 0.3 // tons per nm (estimated)
  const portFeeAverage = 5000 // USD per port call
  const canalFeeAverage = 50000 // USD per canal transit
  
  formData.value.legs.forEach(leg => {
    // Fuel costs
    if (leg.type === 'transit' && leg.distance) {
      fuelCost += leg.distance * fuelConsumptionPerNm * fuelPricePerTon
    }
    
    // Port fees
    if (['loading', 'discharge'].includes(leg.type)) {
      portFees += portFeeAverage
    }
    
    // Canal fees
    if (leg.type === 'canal') {
      canalFees += canalFeeAverage
    }
  })
  
  const other = 0
  const total = fuelCost + portFees + canalFees + other
  const distance = parseFloat(totalDistance.value)
  const perNm = distance > 0 ? total / distance : 0
  
  costPreview.value = {
    fuel: Math.round(fuelCost),
    portFees: Math.round(portFees),
    canalFees: Math.round(canalFees),
    other,
    total: Math.round(total),
    perNm
  }
}

function getVesselName(id: string): string {
  const vessel = vessels.value.find(v => v.id === id)
  return vessel ? vessel.name : ''
}

function formatDate(dateStr: string): string {
  if (!dateStr) return 'Not set'
  return new Date(dateStr).toLocaleDateString()
}

// Load voyage templates
async function loadTemplates() {
  try {
    const response = await axios.get('/data/voyage_templates.json')
    templates.value = response.data || []
  } catch (error) {
    console.error('Failed to load templates:', error)
    templates.value = []
  }
}

// Load distance matrix from available data sources
async function loadDistanceMatrix() {
  try {
    const module = formData.value.module
    if (!module) return
    
    // Load distances based on module
    const response = await axios.get(`/input/${module}/distances_${module}.csv`)
    const csvData = response.data
    
    // Parse CSV and build distance matrix
    const lines = csvData.split('\n')
    const matrix: Record<string, number> = {}
    
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(',')
      if (parts.length >= 3) {
        const from = parts[0]?.trim()
        const to = parts[1]?.trim()
        const distance = parseFloat(parts[2]?.trim())
        
        if (from && to && !isNaN(distance)) {
          matrix[`${from}-${to}`] = distance
          matrix[`${to}-${from}`] = distance // Bidirectional
        }
      }
    }
    
    distanceMatrix.value = matrix
  } catch (error) {
    console.warn('Could not load distance matrix:', error)
  }
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    vesselStore.fetchVessels(),
    routeStore.fetchRoutes(),
    cargoStore.fetchCargo(),
    loadTemplates(),
    loadDistanceMatrix()
  ])
})

// Watch module change to filter vessels and reload distance matrix
watch(() => formData.value.module, async (newModule) => {
  if (newModule) {
    await Promise.all([
      vesselStore.fetchVessels(newModule),
      loadDistanceMatrix()
    ])
  }
})

// Watch legs for real-time updates
watch(() => formData.value.legs, () => {
  validateCapacity()
  recalculateCosts()
}, { deep: true })
</script>

<style scoped>
.voyage-builder {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.builder-header {
  text-align: center;
  margin-bottom: 3rem;
}

h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1.125rem;
  margin: 0;
}

.wizard-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3rem;
  position: relative;
}

.wizard-steps::before {
  content: '';
  position: absolute;
  top: 30px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--border-color);
  z-index: 0;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
}

.step-indicator {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--bg-secondary);
  border: 3px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.25rem;
  color: var(--text-muted);
  transition: all 0.3s;
}

.step.active .step-indicator {
  border-color: var(--accent-primary);
  background: var(--accent-primary);
  color: white;
}

.step.completed .step-indicator {
  border-color: var(--accent-primary);
  background: var(--accent-primary);
  color: white;
}

.step.disabled .step-indicator {
  opacity: 0.5;
}

.checkmark {
  font-size: 1.5rem;
}

.step-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.step-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.step-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.wizard-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: var(--shadow-sm);
}

.step-content h2 {
  font-size: 1.5rem;
  color: var(--text-primary);
  margin: 0 0 2rem 0;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 1rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
}

.error {
  display: block;
  color: var(--accent-danger);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.vessel-info {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: var(--bg-tertiary);
  border-radius: 4px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.info-label {
  font-weight: 600;
  color: var(--text-primary);
}

.route-toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: flex-end;
}

.route-toolbar .form-group {
  flex: 1;
}

.bulk-operations {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  padding: 0.5rem 1rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  white-space: nowrap;
  transition: background 0.2s;
}

.btn-icon:hover:not(:disabled) {
  background: var(--bg-hover);
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.alert {
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.alert-error {
  background: var(--accent-danger-light);
  border: 1px solid var(--accent-danger);
  color: var(--accent-danger);
}

.alert-success {
  background: rgba(0, 184, 148, 0.1);
  border: 1px solid var(--accent-success);
  color: var(--accent-success);
}

.optimization-panel {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.optimization-panel h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-secondary);
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.suggestion-icon {
  font-size: 1.25rem;
}

.suggestion-text {
  flex: 1;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.btn-apply {
  padding: 0.25rem 0.75rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.2s;
}

.btn-apply:hover {
  background: var(--accent-primary-dark);
}

.cost-preview {
  background: var(--bg-tertiary);
  border: 1px solid var(--accent-warning);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.cost-preview h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: var(--bg-secondary);
  border-radius: 4px;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.cost-item.total {
  background: var(--bg-hover);
  font-size: 1rem;
  margin-top: 0.5rem;
  padding: 0.75rem;
}

.route-legs {
  margin-top: 2rem;
}

.route-legs h3 {
  font-size: 1.125rem;
  color: var(--text-primary);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.leg-count {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: normal;
}

.select-all {
  margin-left: auto;
  font-size: 0.875rem;
  font-weight: normal;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: var(--text-secondary);
}

.legs-container {
  min-height: 100px;
}

.leg-item {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.2s;
}

.leg-item.selected {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
}

.leg-item.ghost {
  opacity: 0.5;
  background: var(--bg-hover);
}

.leg-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.leg-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.drag-handle {
  cursor: grab;
  font-size: 1.25rem;
  color: var(--text-muted);
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.leg-number {
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.leg-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon-small {
  padding: 0.25rem 0.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  color: var(--text-primary);
  transition: background 0.2s;
}

.btn-icon-small:hover {
  background: var(--bg-hover);
}

.remove-leg-btn {
  padding: 0.25rem 0.75rem;
  background: var(--accent-danger);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.remove-leg-btn:hover {
  background: #d63031;
}

.leg-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.add-leg-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.add-leg-btn:hover {
  background: var(--accent-primary-dark);
}

.review-section {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.review-section h3 {
  font-size: 1.125rem;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.review-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-color);
}

.review-item:last-child {
  border-bottom: none;
}

.review-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.review-value {
  color: var(--text-primary);
  font-weight: 500;
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid var(--border-color);
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-primary-dark);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

.btn-success {
  background: var(--accent-success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #00a884;
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .voyage-builder {
    padding: 1rem;
  }

  .wizard-steps {
    flex-direction: column;
    gap: 1rem;
  }

  .wizard-steps::before {
    display: none;
  }

  .step {
    flex-direction: row;
    justify-content: flex-start;
  }

  .step-indicator {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }

  .step-label {
    align-items: flex-start;
    text-align: left;
  }

  .leg-fields {
    grid-template-columns: 1fr;
  }

  .wizard-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .route-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .bulk-operations {
    flex-wrap: wrap;
  }
}
</style>
