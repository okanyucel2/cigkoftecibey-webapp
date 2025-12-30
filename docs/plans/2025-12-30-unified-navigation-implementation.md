# Unified Navigation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Simplify navigation from 9 menu items to 4 main categories with vertical sub-navigation, establishing consistent design system across all views.

**Architecture:**
1. Create new `VerticalNav` component for tabbed navigation
2. Create `GiderlerView` and `GelirlerView` as tab container components
3. Update router with new routes
4. Update sidebar menu
5. Migrate existing views into new tab structure

**Tech Stack:** Vue 3 Composition API, TypeScript, Vue Router 4, Pinia

---

## Task 1: Create VerticalNav Component

**Files:**
- Create: `src/components/ui/VerticalNav.vue`
- Modify: `src/components/ui/index.ts`

**Step 1: Create VerticalNav.vue component**

```vue
<script setup lang="ts">
import { ref } from 'vue'

export interface NavItem {
  id: string
  label: string
  icon?: string
  subItems?: NavItem[]
}

interface Props {
  items: NavItem[]
  modelValue: string
  collapsible?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const expandedItems = ref<Set<string>>(new Set())

function toggleExpand(id: string) {
  if (props.expandedItems.has(id)) {
    props.expandedItems.delete(id)
  } else {
    props.expandedItems.add(id)
  }
  // Force reactivity
  props.expandedItems = new Set(props.expandedItems)
}

function selectItem(id: string) {
  emit('update:modelValue', id)
}

function isActive(item: NavItem): boolean {
  return props.modelValue === item.id ||
    props.modelValue.startsWith(item.id + '/')
}

function isExpanded(id: string): boolean {
  return props.expandedItems.has(id)
}
</script>

<template>
  <nav class="vertical-nav">
    <div v-for="item in items" :key="item.id" class="nav-item">
      <!-- Parent Item -->
      <button
        @click="item.subItems ? toggleExpand(item.id) : selectItem(item.id)"
        :class="[
          'nav-button',
          { 'active': isActive(item), 'has-children': !!item.subItems }
        ]"
      >
        <span v-if="item.icon" class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="item.subItems" class="expand-icon">
          {{ isExpanded(item.id) ? '▼' : '▶' }}
        </span>
      </button>

      <!-- Sub Items -->
      <div v-if="item.subItems && isExpanded(item.id)" class="nav-subitems">
        <button
          v-for="subItem in item.subItems"
          :key="subItem.id"
          @click="selectItem(subItem.id)"
          :class="['nav-button subitem', { 'active': isActive(subItem) }]"
        >
          <span v-if="subItem.icon" class="nav-icon">{{ subItem.icon }}</span>
          <span class="nav-label">{{ subItem.label }}</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.vertical-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  flex-direction: column;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  min-height: 44px;
}

.nav-button:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.nav-button.active {
  background: #dc2626;
  color: white;
}

.nav-button.has-children {
  font-weight: 600;
}

.nav-button.subitem {
  padding-left: 44px;
  font-weight: 400;
  font-size: 13px;
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
}

.expand-icon {
  font-size: 10px;
  transition: transform 0.2s ease;
}

.nav-subitems {
  display: flex;
  flex-direction: column;
  gap: 2px;
  animation: slideDown 0.15s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mobile responsive */
@media (max-width: 640px) {
  .vertical-nav {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .nav-button {
    padding: 8px 16px;
    white-space: nowrap;
    min-height: 40px;
  }

  .nav-button.subitem {
    padding-left: 16px;
  }

  .expand-icon {
    display: none;
  }

  .nav-subitems {
    flex-direction: row;
    animation: none;
  }
}
</style>
```

**Step 2: Export VerticalNav from index.ts**

Add to `src/components/ui/index.ts`:

```typescript
export { default as VerticalNav } from './VerticalNav.vue'
export type { NavItem } from './VerticalNav.vue'
```

**Step 3: Build to verify**

Run: `npm run build`
Expected: No errors, VerticalNav component compiles

**Step 4: Commit**

```bash
git add src/components/ui/VerticalNav.vue src/components/ui/index.ts
git commit -m "feat(ui): add VerticalNav component for tabbed navigation"
```

---

## Task 2: Create GiderlerView (Container)

**Files:**
- Create: `src/views/Giderler.vue`

**Step 1: Create Giderler.vue with tab structure**

```vue
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VerticalNav from '@/components/ui/VerticalNav.vue'
import type { NavItem } from '@/components/ui/VerticalNav.vue'

// Import existing views (will be refactored in later tasks)
import Purchases from './Purchases.vue'
import StaffMeals from './StaffMeals.vue'
import CourierExpenses from './CourierExpenses.vue'
import Production from './Production.vue'
import Expenses from './Expenses.vue'

const router = useRouter()
const route = useRoute()

// Tab navigation items
const navItems: NavItem[] = [
  {
    id: 'mal-alim',
    label: 'Mal Alımları',
    icon: '📦'
  },
  {
    id: 'hizmet-alim',
    label: 'Hizmet Alımları',
    icon: '🍽️',
    subItems: [
      { id: 'hizmet-alim/personel-ias', label: 'Personel İaşe' },
      { id: 'hizmet-alim/kurye', label: 'Kurye Hizmetleri' }
    ]
  },
  {
    id: 'uretim',
    label: 'Üretim',
    icon: '🥙'
  },
  {
    id: 'genel',
    label: 'Genel Giderler',
    icon: '📋'
  }
]

// Active tab from route or default
const activeTab = computed({
  get: () => {
    const path = route.path.replace('/giderler/', '')
    return path || 'mal-alim'
  },
  set: (value) => {
    router.push(`/giderler/${value}`)
  }
})

// Auto-expand parent tab when navigating to sub-tab
watch(activeTab, (newTab) => {
  if (newTab.includes('/')) {
    const parentId = newTab.split('/')[0]
    // Ensure parent is expanded
  }
}, { immediate: true })

// Current view component
const currentView = computed(() => {
  switch (activeTab.value) {
    case 'mal-alim':
      return Purchases
    case 'hizmet-alim/personel-ias':
      return StaffMeals
    case 'hizmet-alim/kurye':
      return CourierExpenses
    case 'uretim':
      return Production
    case 'genel':
      return Expenses
    default:
      return Purchases
  }
})
</script>

<template>
  <div class="giderler-view">
    <div class="giderler-header">
      <h1 class="page-title">💸 Giderler</h1>
      <p class="page-description">Mal alımları, hizmet giderleri, üretim ve işletme giderleri</p>
    </div>

    <div class="giderler-content">
      <!-- Vertical Navigation -->
      <aside class="giderler-nav">
        <VerticalNav v-model="activeTab" :items="navItems" />
      </aside>

      <!-- Content Area -->
      <main class="giderler-main">
        <component :is="currentView" :key="activeTab" />
      </main>
    </div>
  </div>
</template>

<style scoped>
.giderler-view {
  min-height: 100%;
}

.giderler-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  font-family: 'font-display', sans-serif;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.giderler-content {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
  align-items: start;
}

.giderler-nav {
  position: sticky;
  top: 0;
}

.giderler-main {
  min-width: 0;
}

@media (max-width: 1024px) {
  .giderler-content {
    grid-template-columns: 1fr;
  }

  .giderler-nav {
    position: static;
  }
}
</style>
```

**Step 2: Build to verify**

Run: `npm run build`
Expected: No errors

**Step 3: Commit**

```bash
git add src/views/Giderler.vue
git commit -m "feat(view): create GiderlerView with tab navigation container"
```

---

## Task 3: Create GelirlerView (Container)

**Files:**
- Create: `src/views/Gelirler.vue`

**Step 1: Create Gelirler.vue with tab structure**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VerticalNav from '@/components/ui/VerticalNav.vue'
import type { NavItem } from '@/components/ui/VerticalNav.vue'

// Import existing views
import UnifiedSales from './UnifiedSales.vue'
import CashDifference from './CashDifference.vue'

const router = useRouter()
const route = useRoute()

// Tab navigation items
const navItems: NavItem[] = [
  {
    id: 'kasa',
    label: 'Kasa Hareketleri',
    icon: '💰'
  },
  {
    id: 'kasa-farki',
    label: 'Kasa Farkı',
    icon: '💵'
  }
]

// Active tab from route or default
const activeTab = computed({
  get: () => {
    const path = route.path.replace('/gelirler/', '')
    return path || 'kasa'
  },
  set: (value) => {
    router.push(`/gelirler/${value}`)
  }
})

// Current view component
const currentView = computed(() => {
  switch (activeTab.value) {
    case 'kasa':
      return UnifiedSales
    case 'kasa-farki':
      return CashDifference
    default:
      return UnifiedSales
  }
})
</script>

<template>
  <div class="gelirler-view">
    <div class="gelirler-header">
      <h1 class="page-title">💰 Gelirler</h1>
      <p class="page-description">Kasa hareketleri ve kasa farkı analizi</p>
    </div>

    <div class="gelirler-content">
      <!-- Vertical Navigation -->
      <aside class="gelirler-nav">
        <VerticalNav v-model="activeTab" :items="navItems" />
      </aside>

      <!-- Content Area -->
      <main class="gelirler-main">
        <component :is="currentView" :key="activeTab" />
      </main>
    </div>
  </div>
</template>

<style scoped>
.gelirler-view {
  min-height: 100%;
}

.gelirler-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  font-family: 'font-display', sans-serif;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.gelirler-content {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
  align-items: start;
}

.gelirler-nav {
  position: sticky;
  top: 0;
}

.gelirler-main {
  min-width: 0;
}

@media (max-width: 1024px) {
  .gelirler-content {
    grid-template-columns: 1fr;
  }

  .gelirler-nav {
    position: static;
  }
}
</style>
```

**Step 2: Build to verify**

Run: `npm run build`
Expected: No errors

**Step 3: Commit**

```bash
git add src/views/Gelirler.vue
git commit -m "feat(view): create GelirlerView with tab navigation container"
```

---

## Task 4: Update Router Configuration

**Files:**
- Modify: `src/router/index.ts`

**Step 1: Add new routes for Giderler and Gelirler**

Replace the children array in `src/router/index.ts` with:

```typescript
children: [
  {
    path: '',
    name: 'bilanco',
    component: () => import('@/views/Bilanco.vue')
  },
  // NEW: Giderler with nested routes
  {
    path: 'giderler',
    name: 'giderler',
    redirect: '/giderler/mal-alim'
  },
  {
    path: 'giderler/:tab',
    name: 'giderler-tab',
    component: () => import('@/views/Giderler.vue')
  },
  // NEW: Gelirler with nested routes
  {
    path: 'gelirler',
    name: 'gelirler',
    redirect: '/gelirler/kasa'
  },
  {
    path: 'gelirler/:tab',
    name: 'gelirler-tab',
    component: () => import('@/views/Gelirler.vue')
  },
  // Personnel (updated with sub-tabs)
  {
    path: 'personnel/:tab?',
    name: 'personnel',
    component: () => import('@/views/Personnel.vue')
  },
  // OLD: Legacy routes (redirect to new structure)
  {
    path: 'purchases',
    redirect: '/giderler/mal-alim'
  },
  {
    path: 'purchases/new',
    redirect: '/giderler/mal-alim'
  },
  {
    path: 'purchases/:id/edit',
    redirect: '/giderler/mal-alim'
  },
  {
    path: 'expenses',
    redirect: '/giderler/genel'
  },
  {
    path: 'expenses/new',
    redirect: '/giderler/genel'
  },
  {
    path: 'production',
    redirect: '/giderler/uretim'
  },
  {
    path: 'staff-meals',
    redirect: '/giderler/hizmet-alim/personel-ias'
  },
  {
    path: 'courier-expenses',
    redirect: '/giderler/hizmet-alim/kurye'
  },
  {
    path: 'sales',
    redirect: '/gelirler/kasa'
  },
  {
    path: 'kasa-farki',
    redirect: '/gelirler/kasa-farki'
  },
  // Admin routes (unchanged)
  {
    path: 'import',
    name: 'import-hub',
    component: () => import('@/views/ImportHub.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: 'settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: 'Sistem Ayarlari', requiresSuperAdmin: true }
  },
  {
    path: 'invitation-codes',
    name: 'invitation-codes',
    component: () => import('@/views/InvitationCodes.vue'),
    meta: { title: 'Davet Kodlari', requiresOwner: true }
  }
]
```

**Step 2: Build to verify**

Run: `npm run build`
Expected: No router errors, all redirects work

**Step 3: Commit**

```bash
git add src/router/index.ts
git commit -m "feat(router): add Giderler/Gelirler routes with legacy redirects"
```

---

## Task 5: Update Sidebar Menu (Layout.vue)

**Files:**
- Modify: `src/views/Layout.vue`

**Step 1: Replace menuItems array**

Find and replace the `menuItems` array in `src/views/Layout.vue` with:

```typescript
const menuItems = [
  { path: '/', name: 'Bilanço', icon: '📊' },
  { path: '/giderler', name: 'Giderler', icon: '💸' },
  { path: '/gelirler', name: 'Gelirler', icon: '💰' },
  { path: '/personnel', name: 'Personel', icon: '👥' }
]
```

**Step 2: Build and verify**

Run: `npm run build`
Expected: No errors

**Step 3: Test in browser**

Run: `npm run dev`
Navigate to http://localhost:5173
Expected: Sidebar shows 4 menu items instead of 9

**Step 4: Commit**

```bash
git add src/views/Layout.vue
git commit -m "feat(layout): update sidebar to 4-item menu (Giderler, Gelirler, Personnel)"
```

---

## Task 6: Remove Page Headers from Nested Views

**Files:**
- Modify: `src/views/Purchases.vue`
- Modify: `src/views/StaffMeals.vue`
- Modify: `src/views/CourierExpenses.vue`
- Modify: `src/views/Production.vue`
- Modify: `src/views/Expenses.vue`
- Modify: `src/views/UnifiedSales.vue`
- Modify: `src/views/CashDifference.vue`

**Step 1: Remove page titles from each view**

For each file, find and remove the page title section (usually `<h1>` or similar at the top).
Keep the UnifiedFilterBar and content, but remove duplicate page headers.

Example for Purchases.vue - remove this section:
```vue
<h1 class="text-2xl font-bold">Mal Alımı</h1>
```

**Step 2: Build to verify**

Run: `npm run build`
Expected: No errors, pages render without titles inside tab container

**Step 3: Commit**

```bash
git add src/views/Purchases.vue src/views/StaffMeals.vue src/views/CourierExpenses.vue src/views/Production.vue src/views/Expenses.vue src/views/UnifiedSales.vue src/views/CashDifference.vue
git commit -m "refactor(view): remove duplicate page headers from nested views"
```

---

## Task 7: Update Personnel View for Consistency

**Files:**
- Modify: `src/views/Personnel.vue`

**Step 1: Add page header matching new design**

Add at the top of the template in Personnel.vue (inside the main div):

```vue
<div class="personnel-header">
  <h1 class="page-title">👤 Personel Yönetimi</h1>
  <p class="page-description">Çalışan bilgileri, maaş ödemeleri ve part-time giderleri</p>
</div>
```

And add corresponding styles:

```css
.personnel-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  font-family: 'font-display', sans-serif;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}
```

**Step 2: Build to verify**

Run: `npm run build`
Expected: No errors

**Step 3: Commit**

```bash
git add src/views/Personnel.vue
git commit -m "style(personnel): add page header matching new design system"
```

---

## Task 8: Clean Up Unused Form Views

**Files:**
- Delete: `src/views/PurchaseForm.vue`
- Delete: `src/views/ExpenseForm.vue`
- Delete: `src/views/CashDifferenceImport.vue`

**Step 1: Remove unused form view files**

These files are no longer needed since we use modals for entry:

```bash
rm src/views/PurchaseForm.vue
rm src/views/ExpenseForm.vue
rm src/views/CashDifferenceImport.vue
```

**Step 2: Remove routes from router (if any remaining)**

Check `src/router/index.ts` and remove any references to these deleted files.

**Step 3: Build to verify**

Run: `npm run build`
Expected: No import errors

**Step 4: Commit**

```bash
git add src/router/index.ts
git commit -m "chore: remove unused form view files (replaced by modals)"
```

---

## Task 9: Final Testing and Verification

**Files:**
- No file changes
- Manual testing

**Step 1: Start dev server**

Run: `npm run dev`
Open: http://localhost:5173

**Step 2: Test navigation**

Verify each menu item works:
1. Click "💸 Giderler" → Should show Mal Alımları by default
2. Click "🍽️ Hizmet Alımları" → Should expand sub-tabs
3. Click "Personel İaşe" → Should show StaffMeals content
4. Click "Kurye Hizmetleri" → Should show CourierExpenses content
5. Click "🥙 Üretim" → Should show Production content
6. Click "📋 Genel Giderler" → Should show Expenses content

**Step 3: Test Gelirler**

1. Click "💰 Gelirler" → Should show Kasa Hareketleri by default
2. Click "💵 Kasa Farkı" → Should show CashDifference content

**Step 4: Test URL routing**

1. Navigate to `/giderler/hizmet-alim/kurye`
2. Refresh page
3. Expected: Same tab is still active

**Step 5: Test mobile responsiveness**

1. Resize browser to mobile width (<640px)
2. Expected: VerticalNav changes to horizontal scrollable tabs

**Step 6: Test all existing functionality**

1. Create new purchase entry (modal should work)
2. Create new expense entry (modal should work)
3. Filter by date range
4. Verify all data loads correctly

**Step 7: Final commit if any adjustments needed**

```bash
git add .
git commit -m "fix: final adjustments based on testing"
```

---

## Task 10: Update Types and Interfaces

**Files:**
- Modify: `src/types/index.ts` (or wherever types are defined)

**Step 1: Add NavItem type export**

Ensure the NavItem type is exported from types:

```typescript
export interface NavItem {
  id: string
  label: string
  icon?: string
  subItems?: NavItem[]
}
```

**Step 2: Build to verify**

Run: `npm run build`
Expected: No type errors

**Step 3: Commit**

```bash
git add src/types/index.ts
git commit -m "types: export NavItem interface for VerticalNav component"
```

---

## Acceptance Criteria Checklist

After completing all tasks, verify:

- [ ] Sidebar shows exactly 4 menu items (Bilanço, Giderler, Gelirler, Personel)
- [ ] Giderler has 4 sub-tabs with Hizmet Alımları having 2 nested tabs
- [ ] Gelirler has 2 sub-tabs
- [ ] All legacy routes redirect correctly
- [ ] URL routing works with browser back/forward
- [ ] Mobile responsive (horizontal scrollable tabs on mobile)
- [ ] All existing functionality preserved (forms, filters, data)
- [ ] No duplicate page headers
- [ ] Loading/empty states work correctly
- [ ] Build completes without errors

---

## Post-Implementation Notes

1. **Performance Consideration:** The `<component :is>` dynamic rendering may cause brief flashes. Consider adding `<Suspense>` or loading states if needed.

2. **Future Enhancements:**
   - Add keyboard navigation (arrow keys between tabs)
   - Add command palette (Cmd+K) for quick tab switching
   - Persist last visited tab in localStorage
   - Add animation presets for tab transitions

3. **Migration Guide:** Users with old bookmarks will be redirected via the legacy routes. No data migration needed.
