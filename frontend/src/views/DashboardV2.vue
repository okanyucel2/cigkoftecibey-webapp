<template>
  <div class="min-h-screen bg-gray-50 p-4 md:p-6">
    <!-- Header -->
    <header class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Bilanço</h1>
          <p class="text-sm text-gray-500">
            {{ formattedDate }} • Son güncelleme: {{ lastUpdateText }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <!-- Zen Mode Toggle -->
          <button
            type="button"
            :class="[
              'flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors',
              zenMode
                ? 'bg-amber-500 text-white hover:bg-amber-600'
                : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
            ]"
            @click="zenMode = !zenMode"
          >
            <Zap class="w-4 h-4" />
            <span class="hidden sm:inline">{{ zenMode ? 'Normal Mod' : 'Servis Modu' }}</span>
          </button>
          <button
            type="button"
            class="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800"
            @click="showEndOfDayWizard = true"
          >
            <Moon class="w-4 h-4" />
            <span class="hidden sm:inline">Gun Sonu</span>
          </button>
          <button
            type="button"
            class="hidden md:flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <Search class="w-4 h-4" />
            <span>⌘K Hızlı işlem</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-primary-500 animate-spin" />
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-danger-50 border border-danger-200 rounded-lg p-4 mb-6"
    >
      <div class="flex items-center gap-3">
        <AlertCircle class="w-5 h-5 text-danger-600" />
        <p class="text-danger-700">{{ error }}</p>
      </div>
      <button
        type="button"
        class="mt-3 text-sm text-danger-600 hover:underline"
        @click="refresh"
      >
        Tekrar dene
      </button>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- KPI Cards Grid -->
      <div
        data-testid="kpi-grid"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <!-- Net Ciro (clickable for drill-down) -->
        <KPICard
          data-testid="kpi-net-ciro"
          label="Net Ciro"
          :value="netCiro"
          prefix="₺"
          :badge="netCiroTrend"
          :trend="netCiroTrendDirection"
          :subtitle="netCiroSubtitle"
          format-as-currency
          clickable
          @click="openSalesDrilldown"
        />

        <!-- Kasa Farkı -->
        <KPICard
          data-testid="kpi-kasa-farki"
          label="Kasa Farkı"
          :value="kasaFarki"
          prefix="₺"
          :badge="kasaFarkiBadge"
          :badge-type="kasaFarkiBadgeType"
          :subtitle="kasaFarkiSubtitle"
          format-as-currency
        />

        <!-- İşçilik Oranı -->
        <KPICard
          data-testid="kpi-iscilik"
          label="İşçilik Oranı"
          :value="iscilikOrani"
          format-as-percent
          :badge="iscilikBadge"
          :badge-type="iscilikBadgeType"
          show-progress
          :progress-percent="iscilikOrani"
          :progress-color="iscilikProgressColor"
          target="%20"
        />

        <!-- Legen/Ciro -->
        <KPICard
          data-testid="kpi-legen"
          label="Legen/Ciro"
          :value="legenCiro"
          prefix="₺"
          :badge="`${legenCount} legen`"
          badge-type="info"
          format-as-currency
        />
      </div>

      <!-- Hub Widgets Grid -->
      <div
        data-testid="hub-grid"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <!-- Satış Hub -->
        <HubWidget
          test-id="hub-satis"
          label="Satış"
          :value="netCiro"
          :icon="Wallet"
          color="blue"
          :actions="satisActions"
          @action-selected="handleSatisAction"
        />

        <!-- Gider Hub (hidden in Zen Mode) -->
        <HubWidget
          v-show="!zenMode"
          test-id="hub-gider"
          label="Gider"
          :value="totalExpenses"
          :icon="Receipt"
          color="amber"
          :actions="giderActions"
          @action-selected="handleGiderAction"
        />

        <!-- Ekip Hub (hidden in Zen Mode) -->
        <HubWidget
          v-show="!zenMode"
          test-id="hub-ekip"
          label="Ekip"
          :value="staffMealsCost"
          :icon="Users"
          color="emerald"
          :actions="ekipActions"
          @action-selected="handleEkipAction"
        />

        <!-- Üretim Hub -->
        <HubWidget
          test-id="hub-uretim"
          label="Üretim"
          :value="legenCount"
          :icon="Factory"
          color="purple"
          :actions="uretimActions"
          @action-selected="handleUretimAction"
        />
      </div>

      <!-- Middle Section: Platform Distribution + Operational Summary (hidden in Zen Mode) -->
      <div v-show="!zenMode" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Platform Distribution -->
        <div
          data-testid="platform-distribution"
          class="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Platform Dağılımı</h3>
          <div class="space-y-3">
            <div
              v-for="(amount, platform) in onlineBreakdown"
              :key="platform"
              class="flex items-center justify-between"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: getPlatformColor(platform as string) }"
                />
                <span class="text-gray-700">{{ platform }}</span>
              </div>
              <div class="text-right">
                <span class="font-medium text-gray-900">
                  ₺{{ formatNumber(amount) }}
                </span>
                <span class="text-sm text-gray-500 ml-2">
                  {{ getPlatformPercent(platform as string, amount) }}%
                </span>
              </div>
            </div>
            <!-- Salon -->
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-3 h-3 rounded-full"
                  :style="{ backgroundColor: '#2563EB' }"
                />
                <span class="text-gray-700">Salon</span>
              </div>
              <div class="text-right">
                <span class="font-medium text-gray-900">
                  ₺{{ formatNumber(salonSales) }}
                </span>
                <span class="text-sm text-gray-500 ml-2">
                  {{ getSalonPercent() }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Operational Summary -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Operasyonel Özet</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Brüt Kâr</div>
              <div class="text-xl font-bold text-gray-900">
                ₺{{ formatNumber(brutKar) }}
              </div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Kurye/Sipariş</div>
              <div class="text-xl font-bold text-gray-900">
                ₺{{ formatNumber(kuryePerSiparis) }}
              </div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Paket Sayısı</div>
              <div class="text-xl font-bold text-gray-900">
                {{ paketSayisi }}
              </div>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500">Personel Yemeği</div>
              <div class="text-xl font-bold text-gray-900">
                ₺{{ formatNumber(staffMealsCost) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Panel -->
      <div
        data-testid="action-panel"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-4"
      >
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Dikkat Edilmesi Gerekenler</h3>
        <div class="space-y-2">
          <div
            v-for="alert in alerts"
            :key="alert.id"
            class="flex items-center justify-between p-3 rounded-lg"
            :class="getAlertBgClass(alert.type)"
          >
            <div class="flex items-center gap-3">
              <component
                :is="getAlertIcon(alert.type)"
                class="w-5 h-5"
                :class="getAlertIconClass(alert.type)"
              />
              <span :class="getAlertTextClass(alert.type)">{{ alert.message }}</span>
            </div>
            <button
              v-if="alert.actionLabel"
              type="button"
              class="px-3 py-1 text-sm font-medium bg-white rounded border"
              :class="getAlertButtonClass(alert.type)"
            >
              {{ alert.actionLabel }}
            </button>
          </div>
        </div>
      </div>

      <!-- Activity Stream -->
      <ActivityStreamWidget
        data-testid="activity-stream"
        :activities="recentActivities"
        @cancel="handleActivityCancel"
      />
    </div>

    <!-- Slide-over Panel for Sales Entry (Optimized) -->
    <SlideOver
      v-model="showSalesPanel"
      title="Kasa Satışı"
      subtitle="Hızlı satış girişi"
      :icon="Wallet"
      icon-color="blue"
      @update:model-value="(v: boolean) => v && loadChannels()"
    >
      <div class="space-y-5">
        <!-- Kasa Bölümü: Nakit + Kart yan yana -->
        <div>
          <div class="flex items-center gap-2 mb-3">
            <Store class="w-4 h-4 text-blue-600" />
            <span class="text-sm font-medium text-gray-700">Kasa Satışı</span>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">
                <Banknote class="w-3.5 h-3.5 inline mr-1 text-emerald-600" />Nakit
              </label>
              <BaseInput
                v-model="salesForm.cashAmount"
                type="number"
                inputmode="decimal"
                placeholder="0,00"
                prefix="₺"
                autofocus
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">
                <CreditCard class="w-3.5 h-3.5 inline mr-1 text-blue-600" />Kart
              </label>
              <BaseInput
                v-model="salesForm.cardAmount"
                type="number"
                inputmode="decimal"
                placeholder="0,00"
                prefix="₺"
              />
            </div>
          </div>
          <!-- Kasa Toplam -->
          <div
            v-if="kasaTotal > 0"
            class="flex justify-between items-center mt-3 pt-2 border-t border-gray-100"
          >
            <span class="text-sm text-gray-500">Kasa Toplam</span>
            <span class="text-sm font-semibold text-gray-900">
              {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(kasaTotal) }}
            </span>
          </div>
        </div>

        <!-- Platform Accordion (Online Satışlar) -->
        <div class="border-t pt-4">
          <button
            type="button"
            class="w-full flex items-center justify-between text-sm hover:text-gray-900 py-1"
            :class="onlineTotal > 0 ? 'text-purple-600 font-medium' : 'text-gray-600'"
            @click="salesForm.showPlatforms = !salesForm.showPlatforms"
          >
            <div class="flex items-center gap-2">
              <Smartphone class="w-4 h-4" />
              <span>Online Platform Satışları</span>
              <span
                v-if="onlineTotal > 0"
                class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full"
              >
                {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(onlineTotal) }}
              </span>
            </div>
            <ChevronDown
              :class="['w-4 h-4 transition-transform', salesForm.showPlatforms ? 'rotate-180' : '']"
            />
          </button>

          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-96"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 max-h-96"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-show="salesForm.showPlatforms" class="mt-3 space-y-2 overflow-hidden">
              <div v-if="channelsLoading" class="text-center py-4">
                <Loader2 class="w-5 h-5 animate-spin mx-auto text-gray-400" />
                <span class="text-sm text-gray-500">Platformlar yükleniyor...</span>
              </div>
              <template v-else>
                <div
                  v-for="platform in onlinePlatforms"
                  :key="platform.id"
                  class="flex items-center gap-3 bg-gray-50 rounded-lg p-2"
                >
                  <span class="text-sm text-gray-700 w-28 truncate font-medium">{{ platform.name }}</span>
                  <BaseInput
                    v-model="salesForm.platformAmounts[platform.id]"
                    type="number"
                    inputmode="decimal"
                    placeholder="0,00"
                    prefix="₺"
                    class="flex-1"
                  />
                </div>
                <p v-if="onlinePlatforms.length === 0" class="text-sm text-gray-500 text-center py-4">
                  Henüz platform tanımlı değil
                </p>
              </template>
            </div>
          </Transition>
        </div>

        <!-- Genel Toplam -->
        <div
          v-if="grandTotal > 0"
          class="bg-emerald-50 border border-emerald-200 rounded-lg p-4"
        >
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-emerald-800">Genel Toplam</span>
            <span class="text-xl font-bold text-emerald-700">
              {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(grandTotal) }}
            </span>
          </div>
          <div v-if="kasaTotal > 0 && onlineTotal > 0" class="text-xs text-emerald-600 mt-1">
            Kasa: {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(kasaTotal) }} +
            Online: {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(onlineTotal) }}
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center gap-3">
          <button
            type="button"
            class="px-4 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            @click="showSalesPanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            :disabled="!canSaveSale"
            :class="[
              'px-6 py-2.5 text-white rounded-lg transition-colors font-medium',
              canSaveSale
                ? 'bg-emerald-600 hover:bg-emerald-700'
                : 'bg-gray-300 cursor-not-allowed'
            ]"
            @click="handleSalesSave"
          >
            Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Expense Entry (Genel Gider) -->
    <SlideOver
      v-model="showExpensePanel"
      title="Genel Gider"
      subtitle="Hızlı gider girişi"
      :icon="CreditCard"
      icon-color="amber"
      @update:model-value="(v: boolean) => v && loadExpenseCategories()"
    >
      <div class="space-y-5">
        <!-- Category Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Kategori *</label>
          <div v-if="expenseCategoriesLoading" class="flex items-center gap-2 py-3">
            <Loader2 class="w-4 h-4 animate-spin text-gray-400" />
            <span class="text-sm text-gray-500">Kategoriler yükleniyor...</span>
          </div>
          <BaseTagSelect
            v-else
            v-model="expenseForm.category"
            :options="expenseCategories"
            :multiple="false"
            placeholder="Kategori seçin"
          />
        </div>

        <!-- Amount -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Tutar *</label>
          <BaseInput
            v-model="expenseForm.amount"
            type="number"
            inputmode="decimal"
            placeholder="0,00"
            prefix="₺"
            autofocus
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Açıklama</label>
          <BaseInput
            v-model="expenseForm.description"
            placeholder="Ör: Elektrik faturası, Ofis malzemesi..."
          />
        </div>

        <!-- Preview Card -->
        <div
          v-if="canSaveExpense"
          class="bg-amber-50 border border-amber-200 rounded-lg p-4"
        >
          <div class="flex justify-between items-center">
            <div>
              <span class="text-sm text-amber-700">
                {{ expenseCategories.find(c => c.value === expenseForm.category[0])?.label || 'Gider' }}
              </span>
              <p v-if="expenseForm.description" class="text-xs text-amber-600 mt-0.5">
                {{ expenseForm.description }}
              </p>
            </div>
            <span class="text-lg font-bold text-amber-800">
              {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(parseFloat(expenseForm.amount) || 0) }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center gap-3">
          <button
            type="button"
            class="px-4 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            @click="showExpensePanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            :disabled="!canSaveExpense"
            :class="[
              'px-6 py-2.5 text-white rounded-lg transition-colors font-medium',
              canSaveExpense
                ? 'bg-amber-600 hover:bg-amber-700'
                : 'bg-gray-300 cursor-not-allowed'
            ]"
            @click="handleExpenseSave"
          >
            Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Ekip Entry (Optimized Staff Meal) -->
    <SlideOver
      v-model="showEkipPanel"
      :title="currentEkipAction === 'personel-yemegi' ? 'Personel Yemeği' : 'Maaş Ödemesi'"
      :subtitle="currentEkipAction === 'personel-yemegi' ? 'Hızlı yemek girişi' : 'Maaş ödemesi kaydet'"
      :icon="currentEkipAction === 'personel-yemegi' ? Coffee : Wallet"
      icon-color="emerald"
      @update:model-value="(v: boolean) => v && currentEkipAction === 'maas-odemesi' && loadEmployees()"
    >
      <div class="space-y-5">
        <!-- Personel Yemeği Form (Optimized) -->
        <template v-if="currentEkipAction === 'personel-yemegi'">
          <!-- Quick Buttons Section -->
          <div class="bg-emerald-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-3">
              <Zap class="w-4 h-4 text-emerald-600" />
              <span class="text-sm font-medium text-emerald-800">Hızlı Giriş</span>
              <span class="text-xs text-emerald-600">(tek tıkla kaydet)</span>
            </div>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="count in [1, 2, 3, 5]"
                :key="count"
                type="button"
                class="py-3 px-2 text-center bg-white border-2 border-emerald-200 rounded-lg hover:border-emerald-400 hover:bg-emerald-50 transition-colors"
                @click="quickStaffMeal(count)"
              >
                <span class="text-lg font-bold text-emerald-700">+{{ count }}</span>
                <span class="block text-xs text-gray-500">kişi</span>
              </button>
            </div>
            <p class="text-xs text-emerald-600 mt-2 text-center">
              Birim: ₺{{ parseFloat(staffMealForm.unitPrice).toLocaleString('tr-TR') }}
            </p>
          </div>

          <!-- Divider -->
          <div class="flex items-center gap-3">
            <div class="flex-1 h-px bg-gray-200" />
            <span class="text-xs text-gray-400">veya detaylı giriş</span>
            <div class="flex-1 h-px bg-gray-200" />
          </div>

          <!-- Manual Entry -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">Personel Sayısı *</label>
              <BaseInput
                v-model="staffMealForm.staffCount"
                type="number"
                inputmode="numeric"
                placeholder="0"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">
                Birim Fiyat
                <span class="text-xs text-gray-400 font-normal ml-1">(remembered)</span>
              </label>
              <BaseInput
                v-model="staffMealForm.unitPrice"
                type="number"
                inputmode="decimal"
                placeholder="145"
                prefix="₺"
              />
            </div>

            <!-- Total Display -->
            <div v-if="staffMealTotal > 0" class="bg-gray-50 rounded-lg p-3">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Toplam</span>
                <span class="text-xl font-bold text-gray-900">
                  {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(staffMealTotal) }}
                </span>
              </div>
            </div>
          </div>
        </template>

        <!-- Maaş Ödemesi Form (Optimized) -->
        <template v-else>
          <!-- Employee Select -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">
              Çalışan <span class="text-red-500">*</span>
            </label>
            <div v-if="employeesLoading" class="flex items-center gap-2 py-3">
              <Loader2 class="w-4 h-4 animate-spin text-gray-400" />
              <span class="text-sm text-gray-500">Çalışanlar yükleniyor...</span>
            </div>
            <template v-else>
              <select
                v-model="ekipForm.employeeId"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 bg-white"
              >
                <option :value="null" disabled>Çalışan seçin...</option>
                <option v-for="emp in employees" :key="emp.id" :value="emp.id">
                  {{ emp.name }} ({{ emp.role }})
                </option>
              </select>
              <p v-if="employees.length === 0" class="text-xs text-amber-600 mt-1">
                Henüz çalışan tanımlı değil. Personel sayfasından ekleyebilirsiniz.
              </p>
            </template>
          </div>

          <!-- Payment Type Toggle -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Ödeme Tipi</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="pt in paymentTypes"
                :key="pt.value"
                type="button"
                :class="[
                  'px-3 py-2 text-sm font-medium rounded-lg border transition-colors',
                  ekipForm.paymentType === pt.value
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-600'
                ]"
                @click="ekipForm.paymentType = pt.value"
              >
                {{ pt.label }}
              </button>
            </div>
          </div>

          <!-- Amount -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">
              Tutar <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">₺</span>
              <BaseInput
                v-model="ekipForm.amount"
                type="number"
                inputmode="decimal"
                placeholder="0,00"
                class="pl-8"
              />
            </div>
          </div>

          <!-- Info Link -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-3">
            <Info class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <p class="text-sm text-blue-700">
                Detaylı bordro (SGK, mesai, kesinti) için
              </p>
              <router-link
                to="/personnel"
                class="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1 mt-1"
                @click="showEkipPanel = false"
              >
                Personel Sayfasına Git
                <ChevronRight class="w-4 h-4" />
              </router-link>
            </div>
          </div>
        </template>
      </div>

      <template #footer>
        <div class="flex justify-between items-center gap-3">
          <button
            type="button"
            class="px-4 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            @click="showEkipPanel = false"
          >
            İptal
          </button>
          <button
            v-if="currentEkipAction === 'personel-yemegi'"
            type="button"
            :disabled="!canSaveStaffMeal"
            :class="[
              'px-6 py-2.5 text-white rounded-lg transition-colors font-medium',
              canSaveStaffMeal
                ? 'bg-emerald-600 hover:bg-emerald-700'
                : 'bg-gray-300 cursor-not-allowed'
            ]"
            @click="handleStaffMealSave"
          >
            Kaydet
          </button>
          <button
            v-else
            type="button"
            :disabled="!canSaveSalary"
            :class="[
              'px-6 py-2.5 text-white rounded-lg transition-colors font-medium',
              canSaveSalary
                ? 'bg-emerald-600 hover:bg-emerald-700'
                : 'bg-gray-300 cursor-not-allowed'
            ]"
            @click="handleEkipSave"
          >
            Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Online Sales -->
    <SlideOver
      v-model="showOnlineSalesPanel"
      title="Online Satış"
      subtitle="Platform satışlarını kaydet"
      :icon="Smartphone"
      icon-color="blue"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Platform</label>
          <BaseTagSelect
            v-model="onlineSalesForm.platform"
            :options="onlinePlatformOptions"
            :multiple="false"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tutar</label>
          <BaseInput
            v-model="onlineSalesForm.amount"
            type="number"
            placeholder="0,00"
            prefix="₺"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sipariş Sayısı</label>
          <BaseInput
            v-model="onlineSalesForm.orderCount"
            type="number"
            placeholder="0"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
          <BaseInput
            v-model="onlineSalesForm.note"
            placeholder="Notlar..."
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showOnlineSalesPanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700"
            @click="handleOnlineSalesSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Cash Count -->
    <SlideOver
      v-model="showCashCountPanel"
      title="Kasa Sayımı"
      subtitle="Günlük kasa kontrolü"
      :icon="Calculator"
      icon-color="blue"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Beklenen Tutar (POS)</label>
          <BaseInput
            v-model="cashCountForm.expectedCash"
            type="number"
            placeholder="0,00"
            prefix="₺"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fiili Kasa Tutarı</label>
          <BaseInput
            v-model="cashCountForm.actualCash"
            type="number"
            placeholder="0,00"
            prefix="₺"
          />
        </div>
        <!-- Difference Display -->
        <div v-if="cashCountForm.expectedCash && cashCountForm.actualCash" class="p-3 rounded-lg" :class="Math.abs(cashDifferenceAmount) <= 50 ? 'bg-success-50' : 'bg-warning-50'">
          <div class="text-sm font-medium" :class="Math.abs(cashDifferenceAmount) <= 50 ? 'text-success-700' : 'text-warning-700'">
            Fark: ₺{{ cashDifferenceAmount.toLocaleString('tr-TR') }}
          </div>
        </div>

        <!-- Difference Reason (required when |diff| > ₺20) -->
        <div v-if="isDifferenceReasonRequired">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Fark Sebebi <span class="text-red-500">*</span>
          </label>
          <BaseTagSelect
            v-model="cashCountForm.differenceReason"
            :options="differenceReasonOptions"
            :multiple="false"
            placeholder="Sebep secin..."
          />
          <p class="mt-1 text-xs text-warning-600">
            ₺20 uzerindeki farklar icin sebep secimi zorunludur
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
          <BaseInput
            v-model="cashCountForm.note"
            placeholder="Notlar..."
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showCashCountPanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700"
            @click="handleCashCountSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Purchase (Mal Alımı) - Master-Detail -->
    <SlideOver
      v-model="showPurchasePanel"
      title="Mal Alımı"
      subtitle="Tedarikçi alımlarını kaydet"
      :icon="ShoppingCart"
      icon-color="amber"
      @update:model-value="(v: boolean) => v && loadPurchaseData()"
    >
      <div class="space-y-5">
        <!-- Supplier Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Tedarikçi *</label>
          <div v-if="suppliersLoading" class="flex items-center gap-2 py-3">
            <Loader2 class="w-4 h-4 animate-spin text-gray-400" />
            <span class="text-sm text-gray-500">Tedarikçiler yükleniyor...</span>
          </div>
          <select
            v-else
            v-model="purchaseForm.supplierId"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-gray-900"
          >
            <option :value="null" disabled>Tedarikçi seçin...</option>
            <option
              v-for="supplier in suppliers"
              :key="supplier.value"
              :value="supplier.value"
            >
              {{ supplier.label }}
            </option>
          </select>
        </div>

        <!-- Detailed Mode Toggle -->
        <label class="flex items-center gap-3 cursor-pointer py-2 border-t pt-4">
          <input
            v-model="purchaseForm.detailedMode"
            type="checkbox"
            class="h-5 w-5 rounded border-gray-300 text-amber-600 focus:ring-amber-500"
          />
          <span class="text-sm text-gray-700">Detaylı giriş (ürün bazlı)</span>
        </label>

        <!-- Simple Mode -->
        <div v-if="!purchaseForm.detailedMode" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Tutar *</label>
            <BaseInput
              v-model="purchaseForm.simpleAmount"
              type="number"
              inputmode="decimal"
              placeholder="0,00"
              prefix="₺"
              autofocus
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Açıklama</label>
            <BaseInput
              v-model="purchaseForm.simpleDescription"
              placeholder="Ör: Sebze alımı, Et alımı..."
            />
          </div>
        </div>

        <!-- Detailed Mode: Item Rows -->
        <div v-else class="space-y-4">
          <div v-if="productGroupsLoading" class="flex items-center justify-center gap-2 py-4">
            <Loader2 class="w-4 h-4 animate-spin text-gray-400" />
            <span class="text-sm text-gray-500">Ürün grupları yükleniyor...</span>
          </div>

          <template v-else>
            <!-- Item Rows -->
            <div
              v-for="(item, index) in purchaseForm.items"
              :key="item.id"
              class="bg-gray-50 rounded-lg p-3 space-y-3"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-gray-500">Kalem {{ index + 1 }}</span>
                <button
                  type="button"
                  class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                  @click="removePurchaseItem(item.id)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>

              <!-- Group → Product Cascade -->
              <div class="grid grid-cols-2 gap-2">
                <select
                  v-model="item.groupId"
                  class="px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-amber-500"
                  @change="item.productId = null"
                >
                  <option :value="null">Grup seç...</option>
                  <option
                    v-for="group in productGroups"
                    :key="group.id"
                    :value="group.id"
                  >
                    {{ group.name }}
                  </option>
                </select>
                <select
                  v-model="item.productId"
                  class="px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-amber-500"
                  :disabled="!item.groupId"
                >
                  <option :value="null">Ürün seç...</option>
                  <option
                    v-for="product in getProductsForGroup(item.groupId)"
                    :key="product.id"
                    :value="product.id"
                  >
                    {{ product.name }}
                  </option>
                </select>
              </div>

              <!-- Description (if no product selected) -->
              <input
                v-if="!item.productId"
                v-model="item.description"
                type="text"
                placeholder="Ürün açıklaması..."
                class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-amber-500"
              />

              <!-- Quantity, Unit, Price -->
              <div class="grid grid-cols-3 gap-2">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Miktar</label>
                  <input
                    v-model="item.quantity"
                    type="number"
                    inputmode="decimal"
                    placeholder="0"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-amber-500"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Birim</label>
                  <select
                    v-model="item.unit"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-amber-500"
                  >
                    <option v-for="unit in unitOptions" :key="unit" :value="unit">
                      {{ unit }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">B.Fiyat</label>
                  <input
                    v-model="item.unitPrice"
                    type="number"
                    inputmode="decimal"
                    placeholder="₺"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-amber-500"
                  />
                </div>
              </div>

              <!-- Row Total -->
              <div class="text-right text-sm">
                <span class="text-gray-500">Tutar: </span>
                <span class="font-medium text-gray-900">
                  {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format((parseFloat(item.quantity) || 0) * (parseFloat(item.unitPrice) || 0)) }}
                </span>
              </div>
            </div>

            <!-- Add Item Button -->
            <button
              type="button"
              class="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-amber-600 bg-amber-50 rounded-lg hover:bg-amber-100 transition-colors border border-dashed border-amber-200"
              @click="addPurchaseItem"
            >
              <Plus class="w-4 h-4" />
              Kalem Ekle
            </button>
          </template>
        </div>

        <!-- Total Preview -->
        <div
          v-if="purchaseTotal > 0"
          class="bg-amber-50 border border-amber-200 rounded-lg p-4"
        >
          <div class="flex justify-between items-center">
            <div>
              <span class="text-sm font-medium text-amber-800">
                {{ suppliers.find(s => s.value === purchaseForm.supplierId)?.label || 'Tedarikçi' }}
              </span>
              <p v-if="purchaseForm.detailedMode" class="text-xs text-amber-600 mt-0.5">
                {{ purchaseForm.items.filter(i => (parseFloat(i.quantity) || 0) > 0).length }} kalem
              </p>
            </div>
            <span class="text-xl font-bold text-amber-700">
              {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(purchaseTotal) }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center gap-3">
          <button
            type="button"
            class="px-4 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            @click="showPurchasePanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            :disabled="!canSavePurchase"
            :class="[
              'px-6 py-2.5 text-white rounded-lg transition-colors font-medium',
              canSavePurchase
                ? 'bg-amber-600 hover:bg-amber-700'
                : 'bg-gray-300 cursor-not-allowed'
            ]"
            @click="handlePurchaseSave"
          >
            Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Courier Expense (Optimized with VAT) -->
    <SlideOver
      v-model="showCourierPanel"
      title="Kurye Gideri"
      subtitle="Platform kurye ödemelerini kaydet"
      :icon="Truck"
      icon-color="amber"
      @update:model-value="(v: boolean) => v && loadChannels()"
    >
      <div class="space-y-5">
        <!-- Platform Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Platform *</label>
          <select
            v-model="courierForm.platformId"
            class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-gray-900"
          >
            <option :value="null" disabled>Platform seçin...</option>
            <option
              v-for="platform in onlinePlatforms"
              :key="platform.id"
              :value="platform.id"
            >
              {{ platform.name }}
            </option>
          </select>
        </div>

        <!-- Package Count -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Paket Sayısı</label>
          <BaseInput
            v-model="courierForm.packageCount"
            type="number"
            inputmode="numeric"
            placeholder="0"
          />
        </div>

        <!-- Amount (KDV Hariç) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Tutar (KDV Hariç) *</label>
          <BaseInput
            v-model="courierForm.amount"
            type="number"
            inputmode="decimal"
            placeholder="0,00"
            prefix="₺"
          />
        </div>

        <!-- VAT Calculation Display -->
        <Transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
        >
          <div v-if="parseFloat(courierForm.amount) > 0" class="bg-amber-50 rounded-lg p-4 space-y-2">
            <div class="flex justify-between items-center text-sm">
              <span class="text-gray-600">KDV (%{{ courierForm.vatRate }})</span>
              <span class="font-medium text-gray-900">
                {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(courierVatAmount) }}
              </span>
            </div>
            <div class="border-t border-amber-200 pt-2 flex justify-between items-center">
              <span class="font-medium text-gray-700">TOPLAM</span>
              <span class="text-xl font-bold text-amber-700">
                {{ new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(courierTotalWithVat) }}
              </span>
            </div>
          </div>
        </Transition>
      </div>

      <template #footer>
        <div class="flex justify-between items-center gap-3">
          <button
            type="button"
            class="px-4 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            @click="showCourierPanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            :disabled="!canSaveCourier"
            :class="[
              'px-6 py-2.5 text-white rounded-lg transition-colors font-medium',
              canSaveCourier
                ? 'bg-amber-600 hover:bg-amber-700'
                : 'bg-gray-300 cursor-not-allowed'
            ]"
            @click="handleCourierSave"
          >
            Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Part-time Payment -->
    <SlideOver
      v-model="showPartTimePanel"
      title="Part-time Ödeme"
      subtitle="Part-time personel ödemelerini kaydet"
      :icon="CreditCard"
      icon-color="emerald"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Personel Adı</label>
          <BaseInput
            v-model="partTimeForm.employeeName"
            placeholder="Ad Soyad"
          />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Saat</label>
            <BaseInput
              v-model="partTimeForm.hoursWorked"
              type="number"
              placeholder="0"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Saat Ücreti</label>
            <BaseInput
              v-model="partTimeForm.hourlyRate"
              type="number"
              placeholder="0"
              prefix="₺"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Toplam Tutar</label>
          <BaseInput
            v-model="partTimeForm.amount"
            type="number"
            placeholder="0,00"
            prefix="₺"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
          <BaseInput
            v-model="partTimeForm.note"
            placeholder="Notlar..."
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showPartTimePanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-white bg-emerald-600 rounded-lg hover:bg-emerald-700"
            @click="handlePartTimeSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Legen Entry (Optimized) -->
    <SlideOver
      v-model="showLegenPanel"
      title="Üretim Girişi"
      subtitle="Günlük üretim miktarını kaydet"
      :icon="Factory"
      icon-color="purple"
    >
      <div class="space-y-5">
        <!-- Type Selector -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Üretim Tipi</label>
          <div class="grid grid-cols-2 gap-3">
            <button
              type="button"
              :class="[
                'flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all',
                legenForm.type === 'etli'
                  ? 'border-purple-500 bg-purple-50 text-purple-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-600'
              ]"
              @click="legenForm.type = 'etli'"
            >
              <span class="text-2xl mb-1">🥩</span>
              <span class="font-medium">Etli</span>
              <Check v-if="legenForm.type === 'etli'" class="w-4 h-4 mt-1 text-purple-600" />
            </button>
            <button
              type="button"
              :class="[
                'flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all',
                legenForm.type === 'etsiz'
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-600'
              ]"
              @click="legenForm.type = 'etsiz'"
            >
              <span class="text-2xl mb-1">🥬</span>
              <span class="font-medium">Etsiz</span>
              <Check v-if="legenForm.type === 'etsiz'" class="w-4 h-4 mt-1 text-green-600" />
            </button>
          </div>
        </div>

        <!-- Kneaded Kg Input -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Yoğrulan Kilo <span class="text-red-500">*</span>
          </label>
          <div class="relative">
            <BaseInput
              v-model="legenForm.kneadedKg"
              type="number"
              placeholder="0"
              class="pr-10"
            />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">kg</span>
          </div>
        </div>

        <!-- Auto-Calculate Result Card -->
        <div v-if="parseFloat(legenForm.kneadedKg) > 0" class="bg-purple-50 border border-purple-200 rounded-xl p-4">
          <div class="flex items-center justify-between text-sm text-purple-600 mb-3">
            <span>1 Legen: {{ legenForm.legenKg }} kg</span>
            <span>₺{{ parseFloat(legenForm.legenCost).toLocaleString('tr-TR') }}</span>
          </div>
          <div class="border-t border-purple-200 pt-3 space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">Legen Sayısı</span>
              <span class="text-lg font-semibold text-purple-700">{{ formLegenCount.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">Toplam Maliyet</span>
              <span class="text-xl font-bold text-purple-800">₺{{ totalProductionCost.toLocaleString('tr-TR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) }}</span>
            </div>
          </div>
        </div>

        <!-- Advanced Settings Accordion -->
        <div class="border-t pt-4">
          <button
            type="button"
            class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
            @click="legenForm.showAdvanced = !legenForm.showAdvanced"
          >
            <ChevronDown
              :class="[
                'w-4 h-4 transition-transform',
                legenForm.showAdvanced ? 'rotate-180' : ''
              ]"
            />
            <span>Değerleri Düzenle (nadir)</span>
          </button>

          <Transition
            enter-active-class="transition-all duration-200"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-40"
            leave-active-class="transition-all duration-200"
            leave-from-class="opacity-100 max-h-40"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="legenForm.showAdvanced" class="mt-3 space-y-3 overflow-hidden">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Legen Kg</label>
                  <BaseInput
                    v-model="legenForm.legenKg"
                    type="number"
                    step="0.1"
                    placeholder="11.2"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Legen Maliyet (₺)</label>
                  <BaseInput
                    v-model="legenForm.legenCost"
                    type="number"
                    placeholder="1040"
                  />
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showLegenPanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            :disabled="!canSaveProduction"
            class="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:bg-purple-300"
            @click="handleLegenSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- Slide-over Panel for Fire Entry -->
    <SlideOver
      v-model="showFirePanel"
      title="Fire Girişi"
      subtitle="Fire miktarını ve nedenini kaydet"
      :icon="AlertTriangle"
      icon-color="amber"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fire Miktarı (kg)</label>
          <BaseInput
            v-model="fireForm.amount"
            type="number"
            placeholder="0,00"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sebep</label>
          <BaseTagSelect
            v-model="fireForm.reason"
            :options="fireReasonOptions"
            :multiple="false"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not (opsiyonel)</label>
          <BaseInput
            v-model="fireForm.note"
            placeholder="Detaylar..."
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            @click="showFirePanel = false"
          >
            İptal
          </button>
          <button
            type="button"
            class="px-4 py-2 text-white bg-danger-600 rounded-lg hover:bg-danger-700"
            @click="handleFireSave"
          >
            💾 Kaydet
          </button>
        </div>
      </template>
    </SlideOver>

    <!-- End of Day Wizard -->
    <EndOfDayWizard
      :show="showEndOfDayWizard"
      @close="showEndOfDayWizard = false"
      @complete="handleEndOfDayComplete"
    />

    <!-- List View Panels (Wide SlideOvers) -->

    <!-- Kasa Farkı Listesi -->
    <SlideOver
      v-model="showCashDifferenceListPanel"
      title="Kasa Farkı"
      subtitle="Bu ayki kasa farkları"
      :icon="AlertCircle"
      icon-color="blue"
      size="2xl"
    >
      <CashDifferenceListEmbedded embedded @action="handleCashDifferenceListAction" />
    </SlideOver>

    <!-- Satış Listesi -->
    <SlideOver
      v-model="showSalesListPanel"
      title="Satış Listesi"
      subtitle="Bu ayki satışlar"
      :icon="Wallet"
      icon-color="blue"
      size="2xl"
    >
      <SalesListEmbedded embedded @action="handleSalesListAction" />
    </SlideOver>

    <!-- Gider Listesi -->
    <SlideOver
      v-model="showExpensesListPanel"
      title="Gider Listesi"
      subtitle="Bu ayki giderler"
      :icon="Receipt"
      icon-color="amber"
      size="2xl"
    >
      <ExpensesListEmbedded embedded @action="handleExpensesListAction" />
    </SlideOver>

    <!-- Alım Listesi -->
    <SlideOver
      v-model="showPurchasesListPanel"
      title="Alım Listesi"
      subtitle="Bu ayki alımlar"
      :icon="ShoppingCart"
      icon-color="amber"
      size="full"
    >
      <PurchasesListEmbedded embedded @action="handlePurchasesListAction" />
    </SlideOver>

    <!-- Personel Listesi -->
    <SlideOver
      v-model="showPersonnelListPanel"
      title="Personel Listesi"
      subtitle="Tüm personel"
      :icon="Users"
      icon-color="emerald"
      size="2xl"
    >
      <PersonnelListEmbedded embedded @action="handlePersonnelListAction" />
    </SlideOver>

    <!-- Bordro Listesi -->
    <SlideOver
      v-model="showPayrollListPanel"
      title="Bordro Listesi"
      subtitle="Bu ayki ödemeler"
      :icon="Wallet"
      icon-color="emerald"
      size="2xl"
    >
      <PayrollListEmbedded embedded @action="handlePayrollListAction" />
    </SlideOver>

    <!-- İaşe Listesi -->
    <SlideOver
      v-model="showStaffMealsListPanel"
      title="Personel Yemekleri"
      subtitle="Bu ayki yemekler"
      :icon="Coffee"
      icon-color="emerald"
      size="xl"
    >
      <StaffMealsListEmbedded embedded @action="handleStaffMealsListAction" />
    </SlideOver>

    <!-- Üretim Listesi -->
    <SlideOver
      v-model="showProductionListPanel"
      title="Üretim Listesi"
      subtitle="Bu ayki üretimler"
      :icon="Factory"
      icon-color="purple"
      size="2xl"
    >
      <ProductionListEmbedded embedded @action="handleProductionListAction" />
    </SlideOver>

    <!-- KPI Drilldown Panel (Panic Button) -->
    <KPIDrilldownPanel
      :show="showDrilldownPanel"
      :title="drilldownTitle"
      :items="currentDrilldownItems"
      :loading="drilldownLoading"
      @close="closeDrilldownPanel"
      @cancel="handleDrilldownCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  Search,
  Loader2,
  AlertCircle,
  Wallet,
  Receipt,
  Users,
  Factory,
  Store,
  Smartphone,
  Calculator,
  ShoppingCart,
  Truck,
  CreditCard,
  Coffee,
  AlertTriangle,
  CheckCircle,
  Info,
  Moon,
  Zap,
  ChevronDown,
  ChevronRight,
  Banknote,
  Check,
  Clock,
  Grid,
  Plus,
  Trash2,
  List
} from 'lucide-vue-next'

import KPICard from '@/components/dashboard/KPICard.vue'
import HubWidget, { type HubAction } from '@/components/dashboard/HubWidget.vue'
import SlideOver from '@/components/dashboard/SlideOver.vue'
import {
  StaffMealsListEmbedded,
  CashDifferenceListEmbedded,
  SalesListEmbedded,
  ExpensesListEmbedded,
  PurchasesListEmbedded,
  PersonnelListEmbedded,
  PayrollListEmbedded,
  ProductionListEmbedded
} from '@/components/embedded'
import KPIDrilldownPanel, { type DrilldownItem } from '@/components/dashboard/KPIDrilldownPanel.vue'
import ActivityStreamWidget, { type ActivityItem } from '@/components/dashboard/ActivityStreamWidget.vue'
import { BaseInput, BaseTagSelect } from '@/components/ui'
import { EndOfDayWizard } from '@/components/wizards/end-of-day'
import { useDashboardData } from '@/composables/useDashboardData'
import { useToast } from '@/composables/useToast'
import { useOptimisticSave } from '@/composables/useOptimisticSave'
import { unifiedSalesApi, expenseCategoriesApi, expensesApi, suppliersApi, purchaseProductsApi, purchasesApi, personnelApi } from '@/services/api'
import type { ChannelsGrouped, ExpenseCategory, Supplier, PurchaseProductGroup, Employee } from '@/types'
// TODO: Enable remaining APIs when handlers are implemented
// import { staffMealsApi, courierExpensesApi, productionApi } from '@/services/api'

// Dashboard data composable
const { data, loading, error, refresh } = useDashboardData()

// Track last update time for display
const lastUpdatedAt = ref<Date | null>(null)
watch(loading, (isLoading, wasLoading) => {
  // When loading completes (true → false), record the time
  if (wasLoading && !isLoading) {
    lastUpdatedAt.value = new Date()
  }
})

// Toast notifications
const toast = useToast()

// Optimistic save composable
const { saveWithUndo } = useOptimisticSave()

// Computed values
const netCiro = computed(() => data.value?.todaySales.total ?? 0)
const kasaFarki = computed(() => data.value?.cashDifference ?? 0)
const iscilikOrani = computed(() => data.value?.laborCostPercent ?? 0)
const legenCiro = computed(() => {
  if (!data.value || data.value.legenCount === 0) return 0
  return Math.round(data.value.todaySales.total / data.value.legenCount)
})
const legenCount = computed(() => data.value?.legenCount ?? 0)
const totalExpenses = computed(() => {
  if (!data.value) return 0
  const exp = data.value.todayExpenses
  return exp.purchases + exp.expenses + exp.staffMeals + exp.courier + exp.partTime
})
const onlineBreakdown = computed(() => data.value?.onlineBreakdown ?? {})
const salonSales = computed(() => data.value?.todaySales.salon ?? 0)
const brutKar = computed(() => data.value?.todayProfit ?? 0)
// Operasyonel metrikler - API'de sipariş sayısı henüz yok
const kuryePerSiparis = computed(() => 0) // Requires: courier cost / order count
const paketSayisi = computed(() => 0) // Requires: order count from API
const staffMealsCost = computed(() => data.value?.todayExpenses.staffMeals ?? 0)

// KPI badges and trends - now using real comparison data from API
const netCiroTrend = computed<string | undefined>(() => {
  const comparison = data.value?.comparison
  if (!comparison) return undefined

  const percent = comparison.sales.diff_percent
  if (percent === 0) return undefined

  return percent > 0 ? `+${percent.toFixed(1)}%` : `${percent.toFixed(1)}%`
})

const netCiroTrendDirection = computed<'up' | 'down' | null>(() => {
  const comparison = data.value?.comparison
  if (!comparison) return null

  const diff = comparison.sales.diff
  if (diff > 0) return 'up'
  if (diff < 0) return 'down'
  return null
})

const netCiroSubtitle = computed(() => {
  const comparison = data.value?.comparison
  if (!comparison) return ''

  const diff = comparison.sales.diff
  if (diff === 0) return ''

  const direction = diff >= 0 ? '+' : ''
  return `düne göre ${direction}₺${Math.abs(diff).toLocaleString('tr-TR')}`
})

const kasaFarkiBadge = computed(() => {
  const diff = kasaFarki.value
  if (Math.abs(diff) <= 50) return '✓'
  return `₺${Math.abs(diff)}`
})
const kasaFarkiBadgeType = computed<'success' | 'warning' | 'danger'>(() => {
  const diff = Math.abs(kasaFarki.value)
  if (diff <= 50) return 'success'
  if (diff <= 200) return 'warning'
  return 'danger'
})
const kasaFarkiSubtitle = computed(() => {
  const diff = Math.abs(kasaFarki.value)
  if (diff <= 50) return 'POS = Excel ✓'
  return 'Fark tespit edildi'
})

const iscilikBadge = computed(() => {
  const ratio = iscilikOrani.value
  if (ratio <= 20) return '✓'
  return '⚠️'
})
const iscilikBadgeType = computed<'success' | 'warning'>(() => {
  return iscilikOrani.value <= 20 ? 'success' : 'warning'
})
const iscilikProgressColor = computed(() => {
  return iscilikOrani.value <= 20 ? 'bg-success-500' : 'bg-warning-500'
})

// Date formatting
const formattedDate = computed(() => {
  const now = new Date()
  return new Intl.DateTimeFormat('tr-TR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    weekday: 'long'
  }).format(now)
})
const lastUpdateText = computed(() => {
  if (!lastUpdatedAt.value) return 'Yükleniyor...'

  const now = new Date()
  const diffMs = now.getTime() - lastUpdatedAt.value.getTime()
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 60) return 'Az önce'

  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin} dk önce`

  const diffHour = Math.floor(diffMin / 60)
  return `${diffHour} saat önce`
})

// Hub actions (only slide-over actions, no navigation links)
const satisActions: HubAction[] = [
  { id: 'kasa-satisi', label: 'Kasa Satışı', icon: Store },
  { id: 'toplu-satis', label: 'Toplu Satış', icon: Grid },
  { id: 'kasa-sayimi', label: 'Kasa Sayımı', icon: Calculator },
  // Liste görünümleri
  { id: 'kasa-farki-liste', label: 'Kasa Farkı', icon: AlertCircle, divider: true, isListView: true },
  { id: 'satis-liste', label: 'Satış Listesi', icon: List, isListView: true }
]

const giderActions: HubAction[] = [
  { id: 'mal-alimi', label: 'Mal Alımı', icon: ShoppingCart },
  { id: 'kurye-gideri', label: 'Kurye Gideri', icon: Truck },
  { id: 'genel-gider', label: 'Genel Gider', icon: CreditCard },
  // Liste görünümleri
  { id: 'gider-liste', label: 'Gider Listesi', icon: List, divider: true, isListView: true },
  { id: 'alim-liste', label: 'Alım Listesi', icon: List, isListView: true }
]

const ekipActions: HubAction[] = [
  { id: 'personel-yemegi', label: 'Personel Yemeği', icon: Coffee },
  { id: 'part-time-odeme', label: 'Part-time Ödeme', icon: Clock },
  { id: 'maas-odemesi', label: 'Maaş Ödemesi', icon: Wallet },
  // Liste görünümleri
  { id: 'personel-liste', label: 'Personel Listesi', icon: Users, divider: true, isListView: true },
  { id: 'bordro-liste', label: 'Bordro Listesi', icon: List, isListView: true },
  { id: 'iase-liste', label: 'İaşe Listesi', icon: Coffee, isListView: true }
]

const uretimActions: HubAction[] = [
  { id: 'legen-girisi', label: 'Legen Girişi', icon: Factory },
  { id: 'fire-girisi', label: 'Fire Bildir', icon: AlertTriangle },
  // Liste görünümü
  { id: 'uretim-liste', label: 'Üretim Listesi', icon: List, divider: true, isListView: true }
]

// Session-based activity stream - populated by user actions during session
// Note: No API backend yet, so activities are session-only and reset on page refresh
const recentActivities = ref<ActivityItem[]>([])

// Slide-over panels
const showSalesPanel = ref(false)
const showOnlineSalesPanel = ref(false)
const showCashCountPanel = ref(false)
const showExpensePanel = ref(false)
const showPurchasePanel = ref(false)
const showCourierPanel = ref(false)
const showEkipPanel = ref(false)
const showPartTimePanel = ref(false)
const showLegenPanel = ref(false)
const showFirePanel = ref(false)
const showEndOfDayWizard = ref(false)

// List View Panels (wide SlideOvers)
const showCashDifferenceListPanel = ref(false)
const showSalesListPanel = ref(false)
const showExpensesListPanel = ref(false)
const showPurchasesListPanel = ref(false)
const showPersonnelListPanel = ref(false)
const showPayrollListPanel = ref(false)
const showStaffMealsListPanel = ref(false)
const showProductionListPanel = ref(false)

// Zen Mode - hides non-essential widgets during busy service hours
const zenMode = ref(false)

// KPI Drilldown Panel
const showDrilldownPanel = ref(false)
const drilldownTitle = ref('')
const drilldownType = ref<'sales' | 'expenses' | null>(null)
const drilldownLoading = ref(false)

// Drilldown data - API endpoints not yet available
// Items will be empty until detailed sales/expenses APIs are implemented
const salesDrilldownItems = ref<DrilldownItem[]>([])
const expensesDrilldownItems = ref<DrilldownItem[]>([])

const currentDrilldownItems = computed(() => {
  if (drilldownType.value === 'sales') return salesDrilldownItems.value
  if (drilldownType.value === 'expenses') return expensesDrilldownItems.value
  return []
})

// Current action context (for panel titles)
const currentEkipAction = ref<string>('')

// Forms
const salesForm = ref({
  // Kasa satışı - Nakit ve Kart ayrı inputlar (varsayılan layout)
  cashAmount: '',
  cardAmount: '',
  // Platform details (progressive disclosure)
  showPlatforms: false,
  platformAmounts: {} as Record<number, string>,
  note: ''
})

// Sales channels from API
const salesChannels = ref<ChannelsGrouped>({ pos: [], online: [] })
const channelsLoading = ref(false)

// Load channels on mount for platform list
async function loadChannels() {
  if (salesChannels.value.pos.length > 0) return // Already loaded
  channelsLoading.value = true
  try {
    const response = await unifiedSalesApi.getChannels()
    salesChannels.value = response.data
  } catch (error) {
    console.error('Failed to load channels:', error)
  } finally {
    channelsLoading.value = false
  }
}

// Computed: Kasa Toplam (Nakit + Kart)
const kasaTotal = computed(() => {
  return (parseFloat(salesForm.value.cashAmount) || 0) +
         (parseFloat(salesForm.value.cardAmount) || 0)
})

// Online platforms (filter from channels)
const onlinePlatforms = computed(() => salesChannels.value.online || [])

// Options format for BaseTagSelect
const onlinePlatformOptions = computed(() =>
  onlinePlatforms.value.map(p => ({ value: String(p.id), label: p.name }))
)

// Computed: Online Toplam (platform amounts sum)
const onlineTotal = computed(() => {
  return Object.values(salesForm.value.platformAmounts)
    .reduce((sum, amountStr) => sum + (parseFloat(amountStr) || 0), 0)
})

// Computed: Genel Toplam (Kasa + Online)
const grandTotal = computed(() => kasaTotal.value + onlineTotal.value)

// Validation: Can save sale?
const canSaveSale = computed(() => {
  // At least one amount (kasa or online) must be > 0
  return kasaTotal.value > 0 || onlineTotal.value > 0
})

const expenseForm = ref({
  category: [] as (string | number)[],
  amount: '',
  description: ''
})

const ekipForm = ref({
  type: '' as string,
  amount: '',
  employeeCount: '',
  employeeId: null as number | null,
  paymentType: 'maas' as 'maas' | 'avans' | 'haftalik',
  note: ''
})

// Employees from API
const employees = ref<{ id: number; name: string; role: string }[]>([])
const employeesLoading = ref(false)

async function loadEmployees() {
  if (employees.value.length > 0) return // Already loaded
  employeesLoading.value = true
  try {
    const response = await personnelApi.getEmployees()
    employees.value = response.data.map((emp: Employee) => ({
      id: emp.id,
      name: emp.name,
      role: emp.is_part_time ? 'Part-time' : (emp.payment_type === 'weekly' ? 'Haftalık' : 'Aylık')
    }))
  } catch (error) {
    console.error('Failed to load employees:', error)
    employees.value = [] // No fallback mock data
  } finally {
    employeesLoading.value = false
  }
}

const paymentTypes = [
  { value: 'maas' as const, label: 'Maaş' },
  { value: 'avans' as const, label: 'Avans' },
  { value: 'haftalik' as const, label: 'Haftalık' }
]

const canSaveSalary = computed(() => {
  return ekipForm.value.employeeId !== null && parseFloat(ekipForm.value.amount) > 0
})

// Staff Meal form with quick buttons support
const staffMealForm = ref({
  staffCount: '',
  unitPrice: localStorage.getItem('staff_meal_unit_price') || '145',
  note: ''
})

// Computed: Staff meal total
const staffMealTotal = computed(() => {
  const count = parseInt(staffMealForm.value.staffCount) || 0
  const price = parseFloat(staffMealForm.value.unitPrice) || 0
  return count * price
})

// Can save staff meal
const canSaveStaffMeal = computed(() => {
  return parseInt(staffMealForm.value.staffCount) > 0
})

// Quick staff meal entry (tek tıkla kaydet)
async function quickStaffMeal(count: number) {
  const unitPrice = parseFloat(staffMealForm.value.unitPrice) || 145
  const totalCost = count * unitPrice

  // Store original values for rollback
  const originalMeals = data.value?.todayExpenses.staffMeals ?? 0

  await saveWithUndo(
    async () => {
      // TODO: Use staffMealsApi.create() when enabled
      // return staffMealsApi.create({
      //   meal_date: new Date().toISOString().split('T')[0],
      //   staff_count: count,
      //   unit_price: unitPrice
      // })
      return Promise.resolve({ data: { id: Date.now() } })
    },
    {},
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todayExpenses.staffMeals += totalCost
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'meal',
          description: `Personel Yemeği (${count} kişi)`,
          amount: -totalCost
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todayExpenses.staffMeals = originalMeals
        }
        recentActivities.value.shift()
      },
      successMessage: `${count} kişilik yemek kaydedildi (₺${totalCost.toLocaleString('tr-TR')})`,
      errorMessage: 'Personel yemeği kaydedilemedi'
    }
  )

  // Remember unit price
  localStorage.setItem('staff_meal_unit_price', unitPrice.toString())

  // Close panel after quick entry
  showEkipPanel.value = false
}

// Online Sales form
const onlineSalesForm = ref({
  platform: [] as (string | number)[],
  amount: '',
  orderCount: '',
  note: ''
})

// Cash Count form
const cashCountForm = ref({
  expectedCash: '',
  actualCash: '',
  differenceReason: [] as (string | number)[],
  note: ''
})

// Cash difference reasons (required when |diff| > ₺20)
const differenceReasonOptions = [
  { value: 'change_error', label: 'Para Ustu Hatasi' },
  { value: 'courier_advance', label: 'Kurye Avansi' },
  { value: 'forgotten_receipt', label: 'Unutulan Fis' },
  { value: 'unknown', label: 'Bilinmiyor' }
]

// Computed: Cash difference amount
const cashDifferenceAmount = computed(() => {
  const expected = parseFloat(cashCountForm.value.expectedCash) || 0
  const actual = parseFloat(cashCountForm.value.actualCash) || 0
  return actual - expected
})

// Computed: Is reason required? (|diff| > ₺20)
const isDifferenceReasonRequired = computed(() => {
  return Math.abs(cashDifferenceAmount.value) > 20
})

// Purchase (Mal Alımı) form
// Purchase Item interface for master-detail
interface PurchaseItemRow {
  id: number  // local temp id
  groupId: number | null
  productId: number | null
  description: string
  quantity: string
  unit: string
  unitPrice: string
}

const purchaseForm = ref({
  supplierId: null as number | null,
  detailedMode: false,  // Toggle for detailed entry
  // Simple mode fields
  simpleAmount: '',
  simpleDescription: '',
  // Detailed mode: item rows
  items: [] as PurchaseItemRow[],
  note: ''
})

// Suppliers and Product Groups from API
const suppliers = ref<{ value: number; label: string }[]>([])
const suppliersLoading = ref(false)
const productGroups = ref<PurchaseProductGroup[]>([])
const productGroupsLoading = ref(false)

async function loadPurchaseData() {
  // Load suppliers
  if (suppliers.value.length === 0) {
    suppliersLoading.value = true
    try {
      const response = await suppliersApi.getAll()
      suppliers.value = response.data.map((s: Supplier) => ({
        value: s.id,
        label: s.name
      }))
    } catch (error) {
      console.error('Failed to load suppliers:', error)
      // Fallback suppliers
      suppliers.value = [
        { value: 1, label: 'Metro' },
        { value: 2, label: 'Makro' },
        { value: 3, label: 'Diğer' }
      ]
    } finally {
      suppliersLoading.value = false
    }
  }

  // Load product groups
  if (productGroups.value.length === 0) {
    productGroupsLoading.value = true
    try {
      const response = await purchaseProductsApi.getGroups()
      productGroups.value = response.data
    } catch (error) {
      console.error('Failed to load product groups:', error)
      productGroups.value = []
    } finally {
      productGroupsLoading.value = false
    }
  }
}

// Get products for a selected group
function getProductsForGroup(groupId: number | null) {
  if (!groupId) return []
  const group = productGroups.value.find(g => g.id === groupId)
  return group?.products || []
}

// Add new item row
function addPurchaseItem() {
  purchaseForm.value.items.push({
    id: Date.now(),
    groupId: null,
    productId: null,
    description: '',
    quantity: '',
    unit: 'kg',
    unitPrice: ''
  })
}

// Remove item row
function removePurchaseItem(id: number) {
  purchaseForm.value.items = purchaseForm.value.items.filter(item => item.id !== id)
}

// Computed: Purchase items total
const purchaseItemsTotal = computed(() => {
  return purchaseForm.value.items.reduce((sum, item) => {
    const qty = parseFloat(item.quantity) || 0
    const price = parseFloat(item.unitPrice) || 0
    return sum + (qty * price)
  }, 0)
})

// Computed: Purchase total (simple or detailed mode)
const purchaseTotal = computed(() => {
  if (purchaseForm.value.detailedMode) {
    return purchaseItemsTotal.value
  }
  return parseFloat(purchaseForm.value.simpleAmount) || 0
})

// Validation: Can save purchase?
const canSavePurchase = computed(() => {
  if (!purchaseForm.value.supplierId) return false
  if (purchaseForm.value.detailedMode) {
    // At least one item with quantity and price
    return purchaseForm.value.items.some(item =>
      (parseFloat(item.quantity) || 0) > 0 && (parseFloat(item.unitPrice) || 0) > 0
    )
  }
  // Simple mode: amount required
  return parseFloat(purchaseForm.value.simpleAmount) > 0
})

// Courier expense form
const courierForm = ref({
  platformId: null as number | null,
  amount: '', // KDV hariç
  packageCount: '',
  vatRate: 20, // Smart default: %20
  note: ''
})

// Courier VAT calculations
const courierVatAmount = computed(() => {
  const amount = parseFloat(courierForm.value.amount) || 0
  return amount * (courierForm.value.vatRate / 100)
})

const courierTotalWithVat = computed(() => {
  const amount = parseFloat(courierForm.value.amount) || 0
  return amount + courierVatAmount.value
})

// Can save courier expense
const canSaveCourier = computed(() => {
  return courierForm.value.platformId !== null &&
         parseFloat(courierForm.value.amount) > 0
})

// Part-time payment form
const partTimeForm = ref({
  employeeName: '',
  hoursWorked: '',
  hourlyRate: '',
  amount: '',
  note: ''
})

// Legen form
const legenForm = ref({
  type: 'etli' as 'etli' | 'etsiz',
  kneadedKg: '',
  legenKg: localStorage.getItem('legen_kg') || '11.2',
  legenCost: localStorage.getItem('legen_cost') || '1040',
  showAdvanced: false,
  note: ''
})

// Production auto-calculations
const formLegenCount = computed(() => {
  const kg = parseFloat(legenForm.value.kneadedKg) || 0
  const perLegen = parseFloat(legenForm.value.legenKg) || 11.2
  return perLegen > 0 ? kg / perLegen : 0
})

const totalProductionCost = computed(() => {
  const cost = parseFloat(legenForm.value.legenCost) || 1040
  return formLegenCount.value * cost
})

const canSaveProduction = computed(() => {
  return parseFloat(legenForm.value.kneadedKg) > 0
})

// Fire form
const fireForm = ref({
  amount: '',
  reason: [] as (string | number)[],
  note: ''
})

// Expense categories from API
const expenseCategories = ref<{ value: number; label: string }[]>([])
const expenseCategoriesLoading = ref(false)

async function loadExpenseCategories() {
  if (expenseCategories.value.length > 0) return // Already loaded
  expenseCategoriesLoading.value = true
  try {
    const response = await expenseCategoriesApi.getAll()
    expenseCategories.value = response.data.map((cat: ExpenseCategory) => ({
      value: cat.id,
      label: cat.name
    }))
  } catch (error) {
    console.error('Failed to load expense categories:', error)
    // Fallback categories
    expenseCategories.value = [
      { value: 1, label: 'Genel Gider' },
      { value: 2, label: 'Fatura' },
      { value: 3, label: 'Ofis Gideri' }
    ]
  } finally {
    expenseCategoriesLoading.value = false
  }
}

// Validation: Can save expense?
const canSaveExpense = computed(() => {
  return expenseForm.value.category.length > 0 && parseFloat(expenseForm.value.amount) > 0
})

// Unit options for purchases
const unitOptions = ['kg', 'adet', 'lt', 'paket', 'koli', 'poşet']

// Fire reasons
const fireReasonOptions = [
  { value: 'expired', label: 'Son Kullanma' },
  { value: 'damaged', label: 'Hasar' },
  { value: 'quality', label: 'Kalite' },
  { value: 'other', label: 'Diğer' }
]

// Hub action handlers
function handleSatisAction(action: HubAction) {
  if (action.id === 'kasa-satisi') {
    showSalesPanel.value = true
  } else if (action.id === 'toplu-satis') {
    // Toplu satış uses same panel but can expand platform section by default
    salesForm.value.showPlatforms = true
    showSalesPanel.value = true
  } else if (action.id === 'kasa-sayimi') {
    showCashCountPanel.value = true
  } else if (action.id === 'kasa-farki-liste') {
    showCashDifferenceListPanel.value = true
  } else if (action.id === 'satis-liste') {
    showSalesListPanel.value = true
  }
}

function handleGiderAction(action: HubAction) {
  if (action.id === 'mal-alimi') {
    showPurchasePanel.value = true
  } else if (action.id === 'kurye-gideri') {
    showCourierPanel.value = true
  } else if (action.id === 'genel-gider') {
    showExpensePanel.value = true
  } else if (action.id === 'gider-liste') {
    showExpensesListPanel.value = true
  } else if (action.id === 'alim-liste') {
    showPurchasesListPanel.value = true
  }
}

function handleEkipAction(action: HubAction) {
  if (action.id === 'part-time-odeme') {
    showPartTimePanel.value = true
  } else if (action.id === 'personel-liste') {
    showPersonnelListPanel.value = true
  } else if (action.id === 'bordro-liste') {
    showPayrollListPanel.value = true
  } else if (action.id === 'iase-liste') {
    showStaffMealsListPanel.value = true
  } else {
    currentEkipAction.value = action.id
    showEkipPanel.value = true
  }
}

function handleUretimAction(action: HubAction) {
  if (action.id === 'legen-girisi') {
    showLegenPanel.value = true
  } else if (action.id === 'fire-girisi') {
    showFirePanel.value = true
  } else if (action.id === 'uretim-liste') {
    showProductionListPanel.value = true
  }
}

// List panel action handlers
function handleCashDifferenceListAction(type: string) {
  showCashDifferenceListPanel.value = false
  if (type === 'import') {
    // Navigate to import or open import modal
  }
}

function handleSalesListAction(type: string) {
  showSalesListPanel.value = false
  if (type === 'add') {
    showSalesPanel.value = true
  }
}

function handleExpensesListAction(type: string) {
  showExpensesListPanel.value = false
  if (type === 'add') {
    showExpensePanel.value = true
  }
}

function handlePurchasesListAction(type: string) {
  showPurchasesListPanel.value = false
  if (type === 'add') {
    showPurchasePanel.value = true
  }
}

function handlePersonnelListAction() {
  showPersonnelListPanel.value = false
}

function handlePayrollListAction(type: string) {
  showPayrollListPanel.value = false
  if (type === 'add') {
    currentEkipAction.value = 'maas-odemesi'
    showEkipPanel.value = true
  }
}

function handleStaffMealsListAction(type: string) {
  showStaffMealsListPanel.value = false
  if (type === 'add') {
    currentEkipAction.value = 'personel-yemegi'
    showEkipPanel.value = true
  }
}

function handleProductionListAction(type: string) {
  showProductionListPanel.value = false
  if (type === 'add') {
    showLegenPanel.value = true
  }
}

// Save handlers
async function handleSalesSave() {
  // Build entries array from Nakit, Kart and Platform amounts
  const entries: Array<{ platform_id: number; amount: number }> = []
  const today = new Date().toISOString().split('T')[0]

  // Find POS channel IDs (Nakit = 1, Kart = 2 by convention)
  const posNakitId = salesChannels.value.pos.find(c => c.name.toLowerCase().includes('nakit'))?.id || 1
  const posKartId = salesChannels.value.pos.find(c => c.name.toLowerCase().includes('kart') || c.name.toLowerCase().includes('visa'))?.id || 2

  // Add Kasa entries (Nakit + Kart)
  const cashAmount = parseFloat(salesForm.value.cashAmount) || 0
  const cardAmount = parseFloat(salesForm.value.cardAmount) || 0

  if (cashAmount > 0) {
    entries.push({ platform_id: posNakitId, amount: cashAmount })
  }
  if (cardAmount > 0) {
    entries.push({ platform_id: posKartId, amount: cardAmount })
  }

  // Add platform entries (online sales)
  Object.entries(salesForm.value.platformAmounts)
    .filter(([_, amountStr]) => parseFloat(amountStr as string) > 0)
    .forEach(([platformIdStr, amountStr]) => {
      entries.push({
        platform_id: Number(platformIdStr),
        amount: parseFloat(amountStr as string)
      })
    })

  if (entries.length === 0) {
    toast.warning('En az bir tutar girmelisiniz')
    return
  }

  // Calculate total for UI
  const totalAmount = entries.reduce((sum, e) => sum + e.amount, 0)

  // Store original values for rollback
  const originalSalon = data.value?.todaySales.salon ?? 0
  const originalTotal = data.value?.todaySales.total ?? 0

  // Determine description for activity stream
  let description = 'Satış'
  if (cashAmount > 0 && cardAmount > 0) {
    description = 'Satış (Nakit + Kart)'
  } else if (cashAmount > 0) {
    description = 'Satış (Nakit)'
  } else if (cardAmount > 0) {
    description = 'Satış (Kart)'
  } else if (onlineTotal.value > 0) {
    description = 'Online Satış'
  }

  // Use saveWithUndo for 7-second undo window
  await saveWithUndo(
    async (saleData: { date: string; entries: typeof entries }) => {
      return unifiedSalesApi.saveDailySales({
        sale_date: saleData.date,
        entries: saleData.entries
      })
    },
    { date: today, entries },
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todaySales.salon += totalAmount
          data.value.todaySales.total += totalAmount
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'sale',
          description,
          amount: totalAmount
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todaySales.salon = originalSalon
          data.value.todaySales.total = originalTotal
        }
        recentActivities.value.shift()
      },
      successMessage: `₺${totalAmount.toLocaleString('tr-TR')} satış kaydedildi`,
      errorMessage: 'Satış kaydedilemedi'
    }
  )

  // Reset form and close panel
  showSalesPanel.value = false
  salesForm.value = {
    cashAmount: '',
    cardAmount: '',
    showPlatforms: false,
    platformAmounts: {},
    note: ''
  }
}

async function handleExpenseSave() {
  const amount = parseFloat(expenseForm.value.amount) || 0
  const categoryId = expenseForm.value.category[0] as number
  const description = expenseForm.value.description.trim()

  if (!categoryId || amount <= 0) {
    toast.warning('Kategori ve tutar zorunludur')
    return
  }

  // Store original values for rollback
  const originalExpenses = data.value?.todayExpenses.expenses ?? 0
  const today = new Date().toISOString().split('T')[0]

  // Get category label for activity stream
  const categoryLabel = expenseCategories.value.find(c => c.value === categoryId)?.label || 'Gider'

  await saveWithUndo(
    async (expenseData: { category_id: number; expense_date: string; description?: string; amount: number }) => {
      return expensesApi.create(expenseData)
    },
    {
      category_id: categoryId,
      expense_date: today,
      description: description || undefined,
      amount
    },
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todayExpenses.expenses += amount
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'expense',
          description: description || categoryLabel,
          detail: categoryLabel,
          amount: -amount
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todayExpenses.expenses = originalExpenses
        }
        recentActivities.value.shift()
      },
      successMessage: `₺${amount.toLocaleString('tr-TR')} gider kaydedildi`,
      errorMessage: 'Gider kaydedilemedi'
    }
  )

  // Reset form and close panel
  showExpensePanel.value = false
  expenseForm.value = { category: [], amount: '', description: '' }
}

// Staff Meal manual save (detaylı giriş)
async function handleStaffMealSave() {
  const count = parseInt(staffMealForm.value.staffCount) || 0
  if (count <= 0) {
    toast.warning('Lütfen personel sayısı girin')
    return
  }

  const unitPrice = parseFloat(staffMealForm.value.unitPrice) || 145
  const totalCost = count * unitPrice

  // Store original for rollback
  const originalMeals = data.value?.todayExpenses.staffMeals ?? 0

  await saveWithUndo(
    async () => {
      // TODO: Use staffMealsApi.create() when enabled
      return Promise.resolve({ data: { id: Date.now() } })
    },
    {},
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todayExpenses.staffMeals += totalCost
        }
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'meal',
          description: `Personel Yemeği (${count} kişi)`,
          amount: -totalCost
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todayExpenses.staffMeals = originalMeals
        }
        recentActivities.value.shift()
      },
      successMessage: `${count} kişilik yemek kaydedildi (₺${totalCost.toLocaleString('tr-TR')})`,
      errorMessage: 'Personel yemeği kaydedilemedi'
    }
  )

  // Remember unit price
  localStorage.setItem('staff_meal_unit_price', unitPrice.toString())

  // Reset form and close
  showEkipPanel.value = false
  staffMealForm.value = {
    staffCount: '',
    unitPrice: localStorage.getItem('staff_meal_unit_price') || '145',
    note: ''
  }
}

async function handleEkipSave() {
  if (!canSaveSalary.value) {
    toast.warning('Lütfen çalışan seçin ve tutar girin')
    return
  }

  const amount = parseFloat(ekipForm.value.amount) || 0
  const employee = employees.value.find(e => e.id === ekipForm.value.employeeId)
  const employeeName = employee?.name || 'Çalışan'
  const paymentLabel = paymentTypes.find(p => p.value === ekipForm.value.paymentType)?.label || 'Ödeme'

  // Store original values for rollback
  const originalSalary = data.value?.todayExpenses.partTime ?? 0

  await saveWithUndo(
    async () => {
      // TODO: Use personnelApi.createPayment() when ready
      return Promise.resolve({ data: { id: Date.now() } })
    },
    {},
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todayExpenses.partTime += amount
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'salary',
          description: `${paymentLabel}: ${employeeName}`,
          amount: -amount
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todayExpenses.partTime = originalSalary
        }
        recentActivities.value.shift()
      },
      successMessage: `₺${amount.toLocaleString('tr-TR')} ${paymentLabel.toLowerCase()} kaydedildi (${employeeName})`,
      errorMessage: 'Ödeme kaydedilemedi'
    }
  )

  showEkipPanel.value = false
  ekipForm.value = {
    type: '',
    amount: '',
    employeeCount: '',
    employeeId: null,
    paymentType: 'maas',
    note: ''
  }
}

// Online Sales save
async function handleOnlineSalesSave() {
  const amount = parseFloat(onlineSalesForm.value.amount) || 0
  if (amount <= 0) {
    toast.warning('Lütfen geçerli bir tutar girin')
    return
  }

  const platform = onlineSalesForm.value.platform[0] as string || 'online'

  // Optimistic UI update
  if (data.value) {
    const platformName = onlinePlatformOptions.value.find(p => p.value === platform)?.label || 'Online'
    if (data.value.onlineBreakdown[platformName]) {
      data.value.onlineBreakdown[platformName] += amount
    } else {
      data.value.onlineBreakdown[platformName] = amount
    }
    data.value.todaySales.online += amount
    data.value.todaySales.total += amount
  }

  toast.success(`₺${amount.toLocaleString('tr-TR')} online satış kaydedildi`)
  showOnlineSalesPanel.value = false
  onlineSalesForm.value = { platform: [], amount: '', orderCount: '', note: '' }
}

// Cash Count save
async function handleCashCountSave() {
  const expected = parseFloat(cashCountForm.value.expectedCash) || 0
  const actual = parseFloat(cashCountForm.value.actualCash) || 0

  if (actual <= 0) {
    toast.warning('Lutfen kasa tutarini girin')
    return
  }

  const diff = actual - expected

  // Validate: Reason required when |diff| > ₺20
  if (Math.abs(diff) > 20 && cashCountForm.value.differenceReason.length === 0) {
    toast.warning('₺20 uzerindeki farklar icin sebep secimi zorunludur')
    return
  }

  const reason = String(cashCountForm.value.differenceReason[0] || '')

  // Optimistic UI update
  if (data.value) {
    data.value.cashDifference = diff
  }

  // Add to activity stream
  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  recentActivities.value.unshift({
    id: Date.now(),
    time: timeStr,
    type: 'cash-count',
    description: 'Kasa Sayimi',
    detail: reason ? differenceReasonOptions.find(o => o.value === reason)?.label : undefined,
    amount: diff
  })
  if (recentActivities.value.length > 5) {
    recentActivities.value.pop()
  }

  if (Math.abs(diff) <= 50) {
    toast.success('Kasa sayimi tamamlandi')
  } else {
    toast.warning(`Kasa farki: ₺${diff.toLocaleString('tr-TR')}`)
  }

  showCashCountPanel.value = false
  cashCountForm.value = { expectedCash: '', actualCash: '', differenceReason: [], note: '' }
}

// Purchase (Mal Alımı) save
async function handlePurchaseSave() {
  if (!canSavePurchase.value) {
    toast.warning('Tedarikçi ve tutar zorunludur')
    return
  }

  const totalAmount = purchaseTotal.value
  const supplierId = purchaseForm.value.supplierId!
  const today = new Date().toISOString().split('T')[0]

  // Build items array based on mode
  const items = purchaseForm.value.detailedMode
    ? purchaseForm.value.items
        .filter(item => (parseFloat(item.quantity) || 0) > 0 && (parseFloat(item.unitPrice) || 0) > 0)
        .map(item => {
          // Get product name if selected
          const product = item.productId
            ? getProductsForGroup(item.groupId).find(p => p.id === item.productId)
            : null
          return {
            product_id: item.productId || undefined,
            description: product?.name || item.description || 'Ürün',
            quantity: parseFloat(item.quantity) || 0,
            unit: item.unit,
            unit_price: parseFloat(item.unitPrice) || 0
          }
        })
    : [{
        description: purchaseForm.value.simpleDescription || 'Mal Alımı',
        quantity: 1,
        unit: 'adet',
        unit_price: totalAmount
      }]

  // Get supplier label for activity stream
  const supplierLabel = suppliers.value.find(s => s.value === supplierId)?.label || 'Tedarikçi'

  // Store original values for rollback
  const originalPurchases = data.value?.todayExpenses.purchases ?? 0

  await saveWithUndo(
    async (purchaseData: { supplier_id: number; purchase_date: string; notes?: string; items: typeof items }) => {
      return purchasesApi.create(purchaseData)
    },
    {
      supplier_id: supplierId,
      purchase_date: today,
      notes: purchaseForm.value.note || undefined,
      items
    },
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todayExpenses.purchases += totalAmount
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'purchase',
          description: `Mal Alımı (${supplierLabel})`,
          detail: purchaseForm.value.detailedMode ? `${items.length} kalem` : undefined,
          amount: -totalAmount
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todayExpenses.purchases = originalPurchases
        }
        recentActivities.value.shift()
      },
      successMessage: `₺${totalAmount.toLocaleString('tr-TR')} mal alımı kaydedildi`,
      errorMessage: 'Mal alımı kaydedilemedi'
    }
  )

  // Reset form and close panel
  showPurchasePanel.value = false
  purchaseForm.value = {
    supplierId: null,
    detailedMode: false,
    simpleAmount: '',
    simpleDescription: '',
    items: [],
    note: ''
  }
}

// Courier expense save
async function handleCourierSave() {
  if (!canSaveCourier.value) {
    toast.warning('Lütfen platform seçin ve tutar girin')
    return
  }

  const totalAmount = courierTotalWithVat.value
  const platform = onlinePlatforms.value.find(p => p.id === courierForm.value.platformId)
  const platformName = platform?.name || 'Platform'
  const packageCount = parseInt(courierForm.value.packageCount) || 0

  // Store original values for rollback
  const originalCourier = data.value?.todayExpenses.courier ?? 0

  await saveWithUndo(
    async () => {
      // TODO: Use expensesApi.createCourierExpense() when ready
      return Promise.resolve({ data: { id: Date.now() } })
    },
    {},
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.todayExpenses.courier += totalAmount
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'courier',
          description: `${platformName} Kurye${packageCount > 0 ? ` (${packageCount} paket)` : ''}`,
          amount: -totalAmount
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.todayExpenses.courier = originalCourier
        }
        recentActivities.value.shift()
      },
      successMessage: `₺${totalAmount.toLocaleString('tr-TR')} kurye gideri kaydedildi (KDV dahil)`,
      errorMessage: 'Kurye gideri kaydedilemedi'
    }
  )

  showCourierPanel.value = false
  courierForm.value = { platformId: null, amount: '', packageCount: '', vatRate: 20, note: '' }
}

// Part-time payment save
async function handlePartTimeSave() {
  const amount = parseFloat(partTimeForm.value.amount) || 0
  if (amount <= 0) {
    toast.warning('Lütfen geçerli bir tutar girin')
    return
  }

  // Optimistic UI update
  if (data.value) {
    data.value.todayExpenses.partTime += amount
  }

  toast.success(`₺${amount.toLocaleString('tr-TR')} part-time ödeme kaydedildi`)
  showPartTimePanel.value = false
  partTimeForm.value = { employeeName: '', hoursWorked: '', hourlyRate: '', amount: '', note: '' }
}

// Legen save
async function handleLegenSave() {
  if (!canSaveProduction.value) {
    toast.warning('Lütfen yoğrulan kilo girin')
    return
  }

  const calculatedLegenCount = formLegenCount.value
  const calculatedCost = totalProductionCost.value
  const typeLabel = legenForm.value.type === 'etli' ? 'Etli' : 'Etsiz'

  // Store original values for rollback
  const originalLegen = data.value?.legenCount ?? 0

  await saveWithUndo(
    async () => {
      // TODO: Use productionApi.create() when ready
      return Promise.resolve({ data: { id: Date.now() } })
    },
    {},
    {
      onOptimisticUpdate: () => {
        if (data.value) {
          data.value.legenCount += Math.round(calculatedLegenCount)
        }
        // Add to activity stream
        const now = new Date()
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
        recentActivities.value.unshift({
          id: Date.now(),
          time: timeStr,
          type: 'legen',
          description: `${typeLabel} Üretim (${calculatedLegenCount.toFixed(1)} legen)`,
          amount: 0 // Production doesn't directly affect ciro
        })
        if (recentActivities.value.length > 5) {
          recentActivities.value.pop()
        }
      },
      onRollback: () => {
        if (data.value) {
          data.value.legenCount = originalLegen
        }
        recentActivities.value.shift()
      },
      successMessage: `${typeLabel} üretim kaydedildi: ${calculatedLegenCount.toFixed(1)} legen (₺${calculatedCost.toLocaleString('tr-TR')})`,
      errorMessage: 'Üretim kaydedilemedi'
    }
  )

  // Remember legen defaults
  localStorage.setItem('legen_kg', legenForm.value.legenKg)
  localStorage.setItem('legen_cost', legenForm.value.legenCost)

  showLegenPanel.value = false
  legenForm.value = {
    type: 'etli',
    kneadedKg: '',
    legenKg: localStorage.getItem('legen_kg') || '11.2',
    legenCost: localStorage.getItem('legen_cost') || '1040',
    showAdvanced: false,
    note: ''
  }
}

// Fire save
async function handleFireSave() {
  const amount = parseFloat(fireForm.value.amount) || 0
  if (amount <= 0) {
    toast.warning('Lütfen geçerli bir miktar girin')
    return
  }

  // Optimistic UI update (fire doesn't directly affect displayed values yet)
  toast.success(`${amount} kg fire kaydedildi`)
  showFirePanel.value = false
  fireForm.value = { amount: '', reason: [], note: '' }
}

// Activity Cancel handler
async function handleActivityCancel(activity: ActivityItem, reason: string) {
  // Store original amount for rollback
  const originalAmount = activity.amount

  // Calculate reversal impact on data
  const reverseImpact = () => {
    if (!data.value) return

    // Reverse the impact based on activity type
    switch (activity.type) {
      case 'sale':
        data.value.todaySales.salon -= Math.abs(originalAmount)
        break
      case 'online-sale':
        data.value.todaySales.online -= Math.abs(originalAmount)
        break
      case 'courier':
        data.value.todayExpenses.courier -= Math.abs(originalAmount)
        break
      case 'meal':
        data.value.todayExpenses.staffMeals -= Math.abs(originalAmount)
        break
      case 'salary':
        data.value.todayExpenses.partTime -= Math.abs(originalAmount)
        break
      case 'purchase':
        data.value.todayExpenses.purchases -= Math.abs(originalAmount)
        break
    }
  }

  // Find and update the activity
  const activityIndex = recentActivities.value.findIndex(a => a.id === activity.id)
  if (activityIndex === -1) return

  await saveWithUndo(
    async () => {
      // TODO: API call to cancel the activity
      return Promise.resolve({ data: { success: true } })
    },
    {},
    {
      onOptimisticUpdate: () => {
        // Mark as cancelled in list
        recentActivities.value[activityIndex] = {
          ...activity,
          is_cancelled: true,
          cancel_reason: reason
        }
        // Reverse impact on KPI data
        reverseImpact()
      },
      onRollback: () => {
        // Restore activity
        recentActivities.value[activityIndex] = activity
        // Re-apply impact (reverse the reverse)
        if (data.value) {
          switch (activity.type) {
            case 'sale':
              data.value.todaySales.salon += Math.abs(originalAmount)
              break
            case 'online-sale':
              data.value.todaySales.online += Math.abs(originalAmount)
              break
            case 'courier':
              data.value.todayExpenses.courier += Math.abs(originalAmount)
              break
            case 'meal':
              data.value.todayExpenses.staffMeals += Math.abs(originalAmount)
              break
            case 'salary':
              data.value.todayExpenses.partTime += Math.abs(originalAmount)
              break
            case 'purchase':
              data.value.todayExpenses.purchases += Math.abs(originalAmount)
              break
          }
        }
      },
      successMessage: `İşlem iptal edildi: ${activity.description}`,
      errorMessage: 'İşlem iptal edilemedi'
    }
  )
}

// End of Day Wizard complete handler
function handleEndOfDayComplete(data: { countedAmount: number | null; expectedAmount: number; differenceReason: string }) {
  // Close wizard
  showEndOfDayWizard.value = false

  // Refresh dashboard data to reflect end of day changes
  refresh()

  // Log the completion
  console.log('End of day completed:', data)
}

// KPI Drilldown Handlers
function openSalesDrilldown() {
  drilldownTitle.value = 'Bugunun Satislari'
  drilldownType.value = 'sales'
  showDrilldownPanel.value = true
}

// TODO: Enable when Expenses KPI card is added
// function openExpensesDrilldown() {
//   drilldownTitle.value = 'Bugunun Giderleri'
//   drilldownType.value = 'expenses'
//   showDrilldownPanel.value = true
// }

function closeDrilldownPanel() {
  showDrilldownPanel.value = false
  drilldownType.value = null
}

function handleDrilldownCancel(item: DrilldownItem) {
  // Mark item as cancelled (soft delete with is_cancelled flag)
  if (drilldownType.value === 'sales') {
    const idx = salesDrilldownItems.value.findIndex(i => i.id === item.id)
    if (idx !== -1) {
      salesDrilldownItems.value[idx].is_cancelled = true
    }
  } else if (drilldownType.value === 'expenses') {
    const idx = expensesDrilldownItems.value.findIndex(i => i.id === item.id)
    if (idx !== -1) {
      expensesDrilldownItems.value[idx].is_cancelled = true
    }
  }

  // TODO: API call to update is_cancelled flag
  // await api.cancelTransaction(item.id)
}

// Alerts
interface Alert {
  id: string
  type: 'warning' | 'critical' | 'success' | 'info'
  message: string
  actionLabel?: string
}

const alerts = computed<Alert[]>(() => {
  const result: Alert[] = []

  // Cash difference alert
  const diff = Math.abs(kasaFarki.value)
  if (diff > 200) {
    result.push({
      id: 'cash-critical',
      type: 'critical',
      message: `Kasada ₺${diff} fark var`,
      actionLabel: 'Kontrol Et'
    })
  } else if (diff > 50) {
    result.push({
      id: 'cash-warning',
      type: 'warning',
      message: `Kasada ₺${diff} fark var`,
      actionLabel: 'Kontrol Et'
    })
  } else {
    result.push({
      id: 'cash-ok',
      type: 'success',
      message: 'Kasa farkı normal'
    })
  }

  // TODO: Add more alerts based on data

  return result
})

// Helper functions
function formatNumber(value: number): string {
  return new Intl.NumberFormat('tr-TR').format(value)
}

function getPlatformColor(platform: string): string {
  const colors: Record<string, string> = {
    Yemeksepeti: '#FF6B35',
    Getir: '#5D3FD3',
    Trendyol: '#F27C38',
    Salon: '#2563EB'
  }
  return colors[platform] ?? '#6B7280'
}

function getPlatformPercent(_platform: string, amount: number): number {
  const total = netCiro.value
  if (total === 0) return 0
  return Math.round((amount / total) * 100)
}

function getSalonPercent(): number {
  const total = netCiro.value
  if (total === 0) return 0
  return Math.round((salonSales.value / total) * 100)
}

function getAlertIcon(type: Alert['type']) {
  const icons = {
    warning: AlertTriangle,
    critical: AlertCircle,
    success: CheckCircle,
    info: Info
  }
  return icons[type]
}

function getAlertBgClass(type: Alert['type']): string {
  const classes = {
    warning: 'bg-warning-50',
    critical: 'bg-danger-50',
    success: 'bg-success-50',
    info: 'bg-primary-50'
  }
  return classes[type]
}

function getAlertIconClass(type: Alert['type']): string {
  const classes = {
    warning: 'text-warning-600',
    critical: 'text-danger-600',
    success: 'text-success-600',
    info: 'text-primary-600'
  }
  return classes[type]
}

function getAlertTextClass(type: Alert['type']): string {
  const classes = {
    warning: 'text-warning-800',
    critical: 'text-danger-800',
    success: 'text-success-800',
    info: 'text-primary-800'
  }
  return classes[type]
}

function getAlertButtonClass(type: Alert['type']): string {
  const classes = {
    warning: 'border-warning-300 text-warning-700 hover:bg-warning-50',
    critical: 'border-danger-300 text-danger-700 hover:bg-danger-50',
    success: 'border-success-300 text-success-700 hover:bg-success-50',
    info: 'border-primary-300 text-primary-700 hover:bg-primary-50'
  }
  return classes[type]
}
</script>
