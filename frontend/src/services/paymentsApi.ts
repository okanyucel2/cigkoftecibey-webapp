import api from './api'
import type {
  SupplierARSummary,
  SupplierARDetail,
  SupplierTransaction,
  SupplierPayment,
  CreatePaymentDTO,
  PaymentFilters
} from '@/types'

export const paymentsApi = {
  // ============ Supplier AR ============
  getSupplierAR: () =>
    api.get<SupplierARSummary[]>('/payments/supplier/ar'),

  getSupplierARDetail: (id: number) =>
    api.get<SupplierARDetail>(`/payments/supplier/ar/${id}`),

  getSupplierTransactions: (id: number, limit = 100) =>
    api.get<SupplierTransaction[]>(`/payments/supplier/ar/${id}/transactions`, {
      params: { limit }
    }),

  // ============ Payments ============
  getPayments: (filters?: PaymentFilters) =>
    api.get<SupplierPayment[]>('/payments/supplier', { params: filters }),

  createPayment: (data: CreatePaymentDTO) =>
    api.post<SupplierPayment>('/payments/supplier', data),

  getPayment: (id: number) =>
    api.get<SupplierPayment>(`/payments/supplier/${id}`),

  updatePayment: (id: number, data: Partial<CreatePaymentDTO>) =>
    api.put<SupplierPayment>(`/payments/supplier/${id}`, data),

  deletePayment: (id: number) =>
    api.delete(`/payments/supplier/${id}`)
}
