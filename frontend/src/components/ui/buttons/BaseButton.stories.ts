import type { Meta, StoryObj } from '@storybook/vue3'
import { Plus, Save, Trash2, ChevronRight } from 'lucide-vue-next'
import BaseButton from './BaseButton.vue'

const meta: Meta<typeof BaseButton> = {
  title: 'UI/Buttons/BaseButton',
  component: BaseButton,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger', 'ghost', 'success'],
      description: 'Button variant',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'pos'],
      description: 'Button size (pos = POS touch mode 52px)',
    },
    type: {
      control: 'select',
      options: ['button', 'submit', 'reset'],
    },
    disabled: { control: 'boolean' },
    loading: { control: 'boolean' },
    iconRight: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof BaseButton>

// Basic variants
export const Primary: Story = {
  args: {
    variant: 'primary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Kaydet</BaseButton>',
  }),
}

export const Secondary: Story = {
  args: {
    variant: 'secondary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Iptal</BaseButton>',
  }),
}

export const Danger: Story = {
  args: {
    variant: 'danger',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Sil</BaseButton>',
  }),
}

export const Ghost: Story = {
  args: {
    variant: 'ghost',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Detay</BaseButton>',
  }),
}

export const Success: Story = {
  args: {
    variant: 'success',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Onayla</BaseButton>',
  }),
}

// Sizes
export const Small: Story = {
  args: {
    size: 'sm',
    variant: 'primary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Kucuk Buton</BaseButton>',
  }),
}

export const Large: Story = {
  args: {
    size: 'lg',
    variant: 'primary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Buyuk Buton</BaseButton>',
  }),
}

export const POSMode: Story = {
  args: {
    size: 'pos',
    variant: 'primary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">POS Buton (52px)</BaseButton>',
  }),
  parameters: {
    docs: {
      description: {
        story: 'Touch-friendly button for POS screens with 52px height (minimum touch target)',
      },
    },
  },
}

// States
export const Loading: Story = {
  args: {
    loading: true,
    variant: 'primary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Kaydediliyor...</BaseButton>',
  }),
}

export const Disabled: Story = {
  args: {
    disabled: true,
    variant: 'primary',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Deaktif</BaseButton>',
  }),
}

// With Icons
export const WithIconLeft: Story = {
  args: {
    variant: 'primary',
    icon: Plus,
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Yeni Ekle</BaseButton>',
  }),
}

export const WithIconRight: Story = {
  args: {
    variant: 'secondary',
    icon: ChevronRight,
    iconRight: true,
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args">Devam Et</BaseButton>',
  }),
}

export const IconOnly: Story = {
  args: {
    variant: 'ghost',
    icon: Trash2,
    size: 'sm',
  },
  render: (args) => ({
    components: { BaseButton },
    setup() { return { args } },
    template: '<BaseButton v-bind="args" />',
  }),
}

// All Variants Showcase
export const AllVariants: Story = {
  render: () => ({
    components: { BaseButton },
    setup() {
      return { Save, Trash2, Plus }
    },
    template: `
      <div class="flex flex-wrap gap-4">
        <BaseButton variant="primary">Primary</BaseButton>
        <BaseButton variant="secondary">Secondary</BaseButton>
        <BaseButton variant="danger">Danger</BaseButton>
        <BaseButton variant="ghost">Ghost</BaseButton>
        <BaseButton variant="success">Success</BaseButton>
      </div>
    `,
  }),
}
