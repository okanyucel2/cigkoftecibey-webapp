import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import { CreditCard, Banknote, Smartphone, Building } from 'lucide-vue-next'
import BaseTagSelect from './BaseTagSelect.vue'

const meta: Meta<typeof BaseTagSelect> = {
  title: 'UI/Forms/BaseTagSelect',
  component: BaseTagSelect,
  tags: ['autodocs'],
  argTypes: {
    multiple: {
      control: 'boolean',
      description: 'Allow multiple selections',
    },
    posMode: {
      control: 'boolean',
      description: 'POS mode with larger touch targets',
    },
    label: { control: 'text' },
    hint: { control: 'text' },
  },
}

export default meta
type Story = StoryObj<typeof BaseTagSelect>

// Payment Methods (Restaurant Use Case)
export const PaymentMethods: Story = {
  args: {
    label: 'Odeme Yontemi',
    multiple: false,
    options: [
      { value: 'cash', label: 'Nakit' },
      { value: 'card', label: 'Kredi Karti' },
      { value: 'mobile', label: 'Mobil' },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['cash'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}

// Payment Methods with Icons
export const PaymentMethodsWithIcons: Story = {
  args: {
    label: 'Odeme Yontemi',
    multiple: false,
    options: [
      { value: 'cash', label: 'Nakit', icon: Banknote },
      { value: 'card', label: 'Kredi Karti', icon: CreditCard },
      { value: 'mobile', label: 'Mobil Odeme', icon: Smartphone },
      { value: 'bank', label: 'Havale', icon: Building },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['card'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}

// Categories (Multi-select)
export const Categories: Story = {
  args: {
    label: 'Kategoriler',
    multiple: true,
    hint: 'Birden fazla secebilirsiniz',
    options: [
      { value: 'food', label: 'Yiyecek' },
      { value: 'drink', label: 'Icecek' },
      { value: 'dessert', label: 'Tatli' },
      { value: 'side', label: 'Yan Urun' },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['food', 'drink'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}

// Days of Week
export const DaysOfWeek: Story = {
  args: {
    label: 'Calisma Gunleri',
    multiple: true,
    options: [
      { value: 'mon', label: 'Pzt' },
      { value: 'tue', label: 'Sal' },
      { value: 'wed', label: 'Car' },
      { value: 'thu', label: 'Per' },
      { value: 'fri', label: 'Cum' },
      { value: 'sat', label: 'Cmt' },
      { value: 'sun', label: 'Paz' },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['mon', 'tue', 'wed', 'thu', 'fri'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}

// POS Mode (Touch-Friendly)
export const POSMode: Story = {
  args: {
    label: 'Odeme Yontemi',
    multiple: false,
    posMode: true,
    options: [
      { value: 'cash', label: 'Nakit', icon: Banknote },
      { value: 'card', label: 'Kart', icon: CreditCard },
      { value: 'mobile', label: 'Mobil', icon: Smartphone },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['cash'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
  parameters: {
    docs: {
      description: {
        story: 'Touch-friendly tag selection for POS screens with larger buttons',
      },
    },
  },
}

// Order Types
export const OrderTypes: Story = {
  args: {
    label: 'Siparis Tipi',
    multiple: false,
    options: [
      { value: 'dine_in', label: 'Restoranda' },
      { value: 'takeaway', label: 'Paket' },
      { value: 'delivery', label: 'Kurye' },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['dine_in'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}

// Status Filter
export const StatusFilter: Story = {
  args: {
    label: 'Durum Filtresi',
    multiple: true,
    hint: 'Goruntulemek istediginiz durumlari secin',
    options: [
      { value: 'active', label: 'Aktif' },
      { value: 'pending', label: 'Beklemede' },
      { value: 'completed', label: 'Tamamlandi' },
      { value: 'cancelled', label: 'Iptal' },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>(['active', 'pending'])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}

// Empty State
export const Empty: Story = {
  args: {
    label: 'Seciminiz',
    multiple: true,
    hint: 'Henuz secim yapilmadi',
    options: [
      { value: '1', label: 'Secenek 1' },
      { value: '2', label: 'Secenek 2' },
      { value: '3', label: 'Secenek 3' },
    ],
  },
  render: (args) => ({
    components: { BaseTagSelect },
    setup() {
      const selected = ref<(string | number)[]>([])
      return { args, selected }
    },
    template: '<BaseTagSelect v-bind="args" v-model="selected" />',
  }),
}
