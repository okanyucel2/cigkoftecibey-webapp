/**
 * Icon registry using emojis for simplicity
 *
 * Benefits:
 * - No additional dependencies
 * - Consistent across platforms
 * - Familiar to users
 * - Can migrate to SVG icons later if needed
 */

export const ICONS = {
  // Navigation / Pages
  expenses: '💸',
  purchases: '🛒',
  personnel: '👥',
  production: '🏭',
  sales: '🛎️',
  staffMeals: '🍽️',
  courierExpenses: '🚴',
  cashDifference: '💵',
  bilanco: '📊',
  reports: '📈',
  settings: '⚙️',
  home: '🏠',

  // Tabs - Personnel
  employees: '👤',
  payroll: '💳',
  parttime: '⏱️',

  // Tabs - General
  list: '📋',
  details: '📝',
  analytics: '📊',

  // Actions
  add: '➕',
  edit: '✏️',
  delete: '🗑️',
  save: '💾',
  cancel: '✕',
  confirm: '✅',
  search: '🔍',
  filter: '🔽',
  sort: '🔀',
  export: '📤',
  import: '📥',
  refresh: '🔄',
  download: '⬇️',
  upload: '⬆️',
  print: '🖨️',
  copy: '📋',
  paste: '📌',
  close: '✕',
  menu: '☰',
  more: '⋯',
  ai: '✨',
  notification: '🔔',

  // Status
  success: '✅',
  warning: '⚠️',
  error: '❌',
  info: 'ℹ️',
  loading: '⏳',
  pending: '⏳',
  active: '🟢',
  inactive: '⚫',
  offline: '🔴',
  online: '🟢',

  // Time presets
  today: '📅',
  yesterday: '📆',
  thisWeek: '📅',
  last7: '📈',
  last30: '📉',
  last90: '📉',
  thisMonth: '📊',
  lastMonth: '📊',
  thisQuarter: '📊',
  thisYear: '📈',
  custom: '✏️',

  // Categories
  food: '🍔',
  beverage: '🥤',
  raw: '🌾',
  packaging: '📦',
  cleaning: '🧹',
  rent: '🏢',
  utilities: '💡',
  insurance: '🛡️',
  marketing: '📣',
  transportation: '🚗',
  communication: '📞',
  other: '📦',

  // Money
  money: '💰',
  cash: '💵',
  card: '💳',
  wallet: '👛',
  bank: '🏦',
  transaction: '🧾',

  // People
  person: '👤',
  people: '👥',
  chef: '👨‍🍳',
  waiter: '🧑‍�waiter',
  customer: '🧑‍🤝‍🧑',
  supplier: '🏭',
  courier: '🚴',

  // Products
  product: '📦',
  inventory: '📊',
  stock: '📦',
  recipe: '📜',

  // Charts
  chart: '📊',
  trendUp: '📈',
  trendDown: '📉',
  pie: '🥧',
  bar: '📊',

  // Feedback
  star: '⭐',
  starEmpty: '☆',
  heart: '❤️',
  thumbsUp: '👍',
  thumbsDown: '👎',
} as const

export type IconName = keyof typeof ICONS

/**
 * Check if a string is a valid icon name
 */
export function isValidIcon(name: string): name is IconName {
  return name in ICONS
}

/**
 * Get an icon by name, return fallback if not found
 */
export function getIcon(name: string, fallback: string = '•'): string {
  return ICONS[name as IconName] || fallback
}
