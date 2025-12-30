import axios from './axios'
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
    axios.get<SupplierARSummary[]>('/payments/supplier/ar'),

  getSupplierARDetail: (id: number) =>
    axios.get<SupplierARDetail>(`/payments/supplier/ar/${id}`),

  getSupplierTransactions: (id: number, limit = 100) =>
    axios.get<SupplierTransaction[]>(`/payments/supplier/ar/${id}/transactions`, {
      params: { limit }
    }),

  // ============ Payments ============
  getPayments: (filters?: PaymentFilters) =>
    axios.get<SupplierPayment[]>('/payments/supplier', { params: filters }),

  createPayment: (data: CreatePaymentDTO) =>
    axios.post<SupplierPayment>('/payments/supplier', data),

  getPayment: (id: number) =>
    axios.get<SupplierPayment>(`/payments/supplier/${id}`),

  updatePayment: (id: number, data: Partial<CreatePaymentDTO>) =>
    axios.put<SupplierPayment>(`/payments/supplier/${id}`, data),

  deletePayment: (id: number) =>
    axios.delete(`/payments/supplier/${id}`)
}
