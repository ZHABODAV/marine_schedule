<template>
  <div class="settings">
    <div class="settings-header">
      <h1>Settings</h1>
      <p class="subtitle">Configure your application preferences</p>
    </div>

    <div class="settings-content">
      <!-- General Settings -->
      <div class="settings-section">
        <h2>General</h2>
        <div class="settings-group">
          <div class="setting-item">
            <label for="language">Language</label>
            <select id="language" v-model="settings.language">
              <option value="en">English</option>
              <option value="ru">Русский</option>
            </select>
          </div>

          <div class="setting-item">
            <label for="timezone">Timezone</label>
            <select id="timezone" v-model="settings.timezone">
              <option value="UTC">UTC</option>
              <option value="Europe/Moscow">Europe/Moscow</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Asia/Tokyo">Asia/Tokyo</option>
            </select>
          </div>

          <div class="setting-item">
            <label for="dateformat">Date Format</label>
            <select id="dateformat" v-model="settings.dateFormat">
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Display Settings -->
      <div class="settings-section">
        <h2>Display</h2>
        <div class="settings-group">
          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.darkMode">
              Dark Mode
            </label>
          </div>

          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.compactView">
              Compact View
            </label>
          </div>

          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.showTooltips">
              Show Tooltips
            </label>
          </div>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="settings-section">
        <h2>Notifications</h2>
        <div class="settings-group">
          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.notifications.email">
              Email Notifications
            </label>
          </div>

          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.notifications.push">
              Push Notifications
            </label>
          </div>

          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.notifications.alerts">
              System Alerts
            </label>
          </div>
        </div>
      </div>

      <!-- Module Settings -->
      <div class="settings-section">
        <h2>Modules</h2>
        <div class="settings-group">
          <div class="setting-item">
            <label>Default Module</label>
            <select v-model="settings.defaultModule">
              <option value="all">All Modules</option>
              <option value="olya">Olya</option>
              <option value="balakovo">Balakovo</option>
              <option value="deepsea">Deep Sea</option>
            </select>
          </div>

          <div class="setting-item">
            <label>
              <input type="checkbox" v-model="settings.autoRefresh">
              Auto Refresh Data
            </label>
          </div>

          <div class="setting-item" v-if="settings.autoRefresh">
            <label for="refreshinterval">Refresh Interval (seconds)</label>
            <input 
              type="number" 
              id="refreshinterval" 
              v-model.number="settings.refreshInterval"
              min="30"
              max="600"
            >
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="settings-actions">
        <button class="btn btn-primary" @click="saveSettings">
          Save Settings
        </button>
        <button class="btn btn-secondary" @click="resetSettings">
          Reset to Defaults
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Settings {
  language: string
  timezone: string
  dateFormat: string
  darkMode: boolean
  compactView: boolean
  showTooltips: boolean
  notifications: {
    email: boolean
    push: boolean
    alerts: boolean
  }
  defaultModule: string
  autoRefresh: boolean
  refreshInterval: number
}

const defaultSettings: Settings = {
  language: 'en',
  timezone: 'UTC',
  dateFormat: 'YYYY-MM-DD',
  darkMode: false,
  compactView: false,
  showTooltips: true,
  notifications: {
    email: true,
    push: true,
    alerts: true
  },
  defaultModule: 'all',
  autoRefresh: false,
  refreshInterval: 60
}

const settings = ref<Settings>({ ...defaultSettings })

function loadSettings() {
  const saved = localStorage.getItem('appSettings')
  if (saved) {
    try {
      settings.value = { ...defaultSettings, ...JSON.parse(saved) }
    } catch (e) {
      console.error('Failed to load settings:', e)
      settings.value = { ...defaultSettings }
    }
  }
}

function saveSettings() {
  try {
    localStorage.setItem('appSettings', JSON.stringify(settings.value))
    alert('Settings saved successfully!')
  } catch (e) {
    console.error('Failed to save settings:', e)
    alert('Failed to save settings')
  }
}

function resetSettings() {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    settings.value = { ...defaultSettings }
    saveSettings()
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.settings-header {
  margin-bottom: 2rem;
}

h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #64748b;
  margin: 0;
}

.settings-content {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.settings-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.settings-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.settings-section h2 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.settings-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-item label {
  font-weight: 500;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.setting-item select,
.setting-item input[type="number"] {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.setting-item select:hover,
.setting-item input[type="number"]:hover {
  border-color: #42b983;
}

.setting-item select:focus,
.setting-item input[type="number"]:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.settings-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #42b983;
  color: white;
}

.btn-primary:hover {
  background: #3aa876;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(66, 185, 131, 0.3);
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

@media (max-width: 768px) {
  .settings {
    padding: 1rem;
  }

  .settings-content {
    padding: 1rem;
  }

  .settings-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
