import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'
import { Search, Mail, Lock, DollarSign } from 'lucide-vue-next'
import BaseInput from './BaseInput.vue'

const meta: Meta<typeof BaseInput> = {
  title: 'UI/Forms/BaseInput',
  component: BaseInput,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['text', 'email', 'password', 'number', 'tel', 'url', 'search'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'pos'],
      description: 'Input size (pos = POS touch mode 52px)',
    },
    disabled: { control: 'boolean' },
    readonly: { control: 'boolean' },
    required: { control: 'boolean' },
    label: { control: 'text' },
    placeholder: { control: 'text' },
    hint: { control: 'text' },
    error: { control: 'text' },
  },
}

export default meta
type Story = StoryObj<typeof BaseInput>

// Basic
export const Default: Story = {
  args: {
    label: 'Isim',
    placeholder: 'Adinizi giriniz',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// With Hint
export const WithHint: Story = {
  args: {
    label: 'E-posta',
    placeholder: 'ornek@firma.com',
    hint: 'Is e-postanizi giriniz',
    type: 'email',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// With Error
export const WithError: Story = {
  args: {
    label: 'E-posta',
    placeholder: 'ornek@firma.com',
    error: 'Gecersiz e-posta formati',
    type: 'email',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('invalid-email')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// Required Field
export const Required: Story = {
  args: {
    label: 'Zorunlu Alan',
    placeholder: 'Bu alan zorunludur',
    required: true,
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// Disabled
export const Disabled: Story = {
  args: {
    label: 'Deaktif',
    placeholder: 'Duzenlenemez',
    disabled: true,
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('Sabit deger')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// With Icon
export const WithIcon: Story = {
  args: {
    label: 'Ara',
    placeholder: 'Ara...',
    icon: Search as any,
    type: 'search',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// Email with Icon
export const EmailWithIcon: Story = {
  args: {
    label: 'E-posta',
    placeholder: 'ornek@firma.com',
    icon: Mail as any,
    type: 'email',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// Password
export const Password: Story = {
  args: {
    label: 'Sifre',
    placeholder: '********',
    icon: Lock as any,
    type: 'password',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// Sizes
export const Small: Story = {
  args: {
    label: 'Kucuk Input',
    placeholder: 'Kucuk',
    size: 'sm',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

export const Large: Story = {
  args: {
    label: 'Buyuk Input',
    placeholder: 'Buyuk',
    size: 'lg',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

export const POSMode: Story = {
  args: {
    label: 'POS Modu',
    placeholder: 'Dokunmatik ekran icin',
    size: 'pos',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
  parameters: {
    docs: {
      description: {
        story: 'Touch-friendly input for POS screens with 52px height',
      },
    },
  },
}

// Number Input (Currency)
export const Currency: Story = {
  args: {
    label: 'Tutar',
    placeholder: '0,00',
    icon: DollarSign as any,
    type: 'number',
    hint: 'TL cinsinden giriniz',
  },
  render: (args) => ({
    components: { BaseInput },
    setup() {
      const value = ref('')
      return { args, value }
    },
    template: '<BaseInput v-bind="args" v-model="value" />',
  }),
}

// All States Showcase
export const AllStates: Story = {
  render: () => ({
    components: { BaseInput },
    setup() {
      const v1 = ref('')
      const v2 = ref('')
      const v3 = ref('invalid')
      const v4 = ref('Sabit')
      return { v1, v2, v3, v4, Search }
    },
    template: `
      <div class="space-y-4 max-w-md">
        <BaseInput label="Normal" placeholder="Normal input" v-model="v1" />
        <BaseInput label="With Hint" placeholder="Input with hint" hint="Bu bir ipucu" v-model="v2" />
        <BaseInput label="With Error" placeholder="Error state" error="Hata mesaji" v-model="v3" />
        <BaseInput label="Disabled" placeholder="Disabled input" disabled v-model="v4" />
      </div>
    `,
  }),
}
