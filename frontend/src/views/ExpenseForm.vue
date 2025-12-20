<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { ExpenseCategory } from '@/types'
import { expenseCategoriesApi, expensesApi } from '@/services/api'

const router = useRouter()

const categories = ref<ExpenseCategory[]>([])
const selectedCategoryId = ref<number | null>(null)
const expenseDate = ref(new Date().toISOString().split('T')[0])
const description = ref('')
const amount = ref<number>(0)
const loading = ref(true)
const submitting = ref(false)

onMounted(async () => {
  try {
    const { data } = await expenseCategoriesApi.getAll()
    categories.value = data
  } catch (error) {
    console.error('Failed to load categories:', error)
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  if (!selectedCategoryId.value) {
    alert('Lutfen kategori secin')
    return
  }

  if (!amount.value || amount.value <= 0) {
    alert('Lutfen gecerli bir tutar girin')
    return
  }

  submitting.value = true
  try {
    await expensesApi.create({
      category_id: selectedCategoryId.value,
      expense_date: expenseDate.value,
      description: description.value || undefined,
      amount: amount.value
    })
    router.push('/expenses')
  } catch (error) {
    console.error('Failed to create expense:', error)
    alert('Gider kaydedilemedi!')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-display font-bold text-gray-900">Yeni Gider</h1>
      <router-link to="/expenses" class="btn btn-ghost">
        ← Geri
      </router-link>
    </div>

    <form @submit.prevent="handleSubmit" class="card space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="category_id" class="block text-sm font-medium text-gray-700 mb-1">
            Kategori *
          </label>
          <select id="category_id" v-model="selectedCategoryId" class="input" required>
            <option :value="null">Kategori Secin</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
              <span v-if="cat.is_fixed"> (Sabit)</span>
            </option>
          </select>
        </div>
        <div>
          <label for="expense_date" class="block text-sm font-medium text-gray-700 mb-1">
            Tarih *
          </label>
          <input id="expense_date" v-model="expenseDate" type="date" class="input" required />
        </div>
      </div>

      <div>
        <label for="amount" class="block text-sm font-medium text-gray-700 mb-1">
          Tutar (TL) *
        </label>
        <input id="amount" v-model.number="amount" type="number" step="0.01" min="0" class="input text-2xl font-bold"
          placeholder="0.00" required />
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
          Aciklama
        </label>
        <textarea id="description" v-model="description" rows="3" class="input" placeholder="Opsiyonel aciklama..." />
      </div>

      <div class="flex justify-end gap-3 pt-4 border-t">
        <router-link to="/expenses" class="btn btn-secondary">
          Iptal
        </router-link>
        <button type="submit" :disabled="submitting" class="btn btn-primary">
          {{ submitting ? 'Kaydediliyor...' : 'Kaydet' }}
        </button>
      </div>
    </form>
  </div>
</template>
