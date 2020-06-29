/* eslint-disable camelcase */
export interface LoginData {
  code: string
}

export interface PasswordData {
  password: string
}

export interface LoginDataPW {
  email: string
  password: string
  appId: string
}

export interface IUserState {
  _id: string
  department: string
  email: string
  avatar: string
  name: string
  token: string
  webeye: number
  roles: string[]
  [prop: string]: any
}

export interface IBillConfig {
  total: number
  items: {
    cp_code: string
    cp_name: string
    percentage: number
    base: number
  }[]
}

export interface IBillItem {
  earn: number
  name: string
  pv: number
}

export interface IBill {
  base_revision: number
  cp_code: string
  cp_name: string
  earn: number
  items?: IBillItem[]
  pv: number
}

export interface IBillQuery {
  bill_date: string
  novel: boolean
}

export interface IExportBillQuery {
  bill_date: string
  pv?: boolean
  is_novel?: boolean
  provider?: string
}
