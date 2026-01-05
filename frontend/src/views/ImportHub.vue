<template>
  <div class="space-y-6" data-testid="import-hub-page">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold" data-testid="import-hub-title">Import Hub</h1>
      <div class="flex gap-2">
        <button
          @click="activeTab = 'import'"
          :class="[
            'px-4 py-2 rounded-lg',
            activeTab === 'import' ? 'bg-blue-600 text-white' : 'bg-gray-100'
          ]"
        >
          Yeni Import
        </button>
        <button
          @click="activeTab = 'history'"
          :class="[
            'px-4 py-2 rounded-lg',
            activeTab === 'history' ? 'bg-blue-600 text-white' : 'bg-gray-100'
          ]"
        >
          Gecmis
        </button>
      </div>
    </div>

    <!-- Import Tab -->
    <div v-if="activeTab === 'import'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Kasa Raporu Import -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold mb-4">Kasa Raporu</h2>
        <p class="text-gray-600 mb-4">Excel dosyasi ve POS resmi yukleyerek gunluk kasa verilerini import edin.</p>
        <router-link
          to="/gelirler/kasa-farki?import=true"
          data-testid="import-hub-kasa-raporu-btn"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Import Et
        </router-link>
      </div>

      <!-- Bulk Expense Import (Future) -->
      <div class="bg-white rounded-lg shadow p-6 opacity-50">
        <h2 class="text-lg font-semibold mb-4">Toplu Gider Import</h2>
        <p class="text-gray-600 mb-4">Excel'den toplu gider aktarimi. (Yakinda)</p>
        <button disabled class="px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed">
          Yakinda
        </button>
      </div>
    </div>

    <!-- History Tab -->
    <div v-if="activeTab === 'history'" class="bg-white rounded-lg shadow">
      <div class="p-4 border-b flex gap-4 flex-wrap">
        <select v-model="historyFilter.import_type" class="border rounded px-3 py-2">
          <option value="">Tum Turler</option>
          <option value="kasa_raporu">Kasa Raporu</option>
          <option value="expense">Gider</option>
        </select>
        <input
          type="date"
          v-model="historyFilter.start_date"
          class="border rounded px-3 py-2"
        />
        <input
          type="date"
          v-model="historyFilter.end_date"
          class="border rounded px-3 py-2"
        />
        <button @click="loadHistory" class="px-4 py-2 bg-blue-600 text-white rounded">
          Filtrele
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Tarih</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Tur</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Dosya</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Durum</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Islemler</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="h in history" :key="h.id">
              <td class="px-4 py-3 text-sm">{{ formatDate(h.import_date) }}</td>
              <td class="px-4 py-3 text-sm">{{ h.import_type }}</td>
              <td class="px-4 py-3 text-sm">{{ h.source_filename || '-' }}</td>
              <td class="px-4 py-3 text-sm">
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs',
                    h.status === 'completed' ? 'bg-green-100 text-green-800' :
                    h.status === 'undone' ? 'bg-gray-100 text-gray-800' :
                    'bg-yellow-100 text-yellow-800'
                  ]"
                >
                  {{ h.status }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm">
                <button
                  v-if="h.status === 'completed'"
                  @click="undoImport(h.id)"
                  class="text-red-600 hover:underline"
                >
                  Geri Al
                </button>
              </td>
            </tr>
            <tr v-if="history.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-gray-500">
                Henuz import gecmisi yok
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { importHistoryApi } from '@/services/api'

const activeTab = ref<'import' | 'history'>('import')
const history = ref<any[]>([])
const historyFilter = ref({
  import_type: '',
  start_date: '',
  end_date: ''
})

const loadHistory = async () => {
  try {
    const params: Record<string, string> = {}
    if (historyFilter.value.import_type) params.import_type = historyFilter.value.import_type
    if (historyFilter.value.start_date) params.start_date = historyFilter.value.start_date
    if (historyFilter.value.end_date) params.end_date = historyFilter.value.end_date

    const response = await importHistoryApi.getAll(params)
    history.value = response.data
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const undoImport = async (id: number) => {
  if (!confirm('Bu import geri alinacak. Emin misiniz?')) return

  try {
    await importHistoryApi.undo(id)
    await loadHistory()
  } catch (error) {
    console.error('Failed to undo import:', error)
    alert('Import geri alinamadi')
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('tr-TR')
}

onMounted(() => {
  loadHistory()
})
</script>
