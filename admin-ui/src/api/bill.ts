import { IBill, IBillConfig, IBillQuery, IExportBillQuery } from './types'
import request from '@/utils/request'

/**
 * 获取账单详情
 * @param query 查询参数
 */
export function getBillDetail(query: IBillQuery) {
  return request.post<any, IBill[]>('/api/bill_detail', query)
}

/**
 * 获取账单配置
 * @param query 查询参数
 */
// eslint-disable-next-line camelcase
export function getBillConfig(query: { bill_date: string }) {
  return request.post<any, IBillConfig>('/api/config_detail ', query)
}

/**
 * 更新账单配置
 * @param data 账单配置
 */
export function updateBillConfig(data: IBillConfig) {
  return request.post<any, any>('/api/config_update', data)
}

/**
 * 导出账单
 * @param url 导出地址
 */
export function exportBill(url: string) {
  window.open(url)
}

export const BillExportBaseURL = '/api/bill_export'
