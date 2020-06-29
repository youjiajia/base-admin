import { LoginData, LoginDataPW, PasswordData } from './types'
import request from '@/utils/request'

/**
 * 获取用户信息
 */
export const getUserInfo = () =>
  request.get('/api/userinfo')

/**
   * 登出
   */
export const logout = () =>
  request.post('/api/logout')

/**
 * 用户名密码登录
 * @param data 登录数据
 */
export function login(data: LoginDataPW) {
  return request.post('/api/login', data)
}

/**
 * 飞书登录
 * @param {{code:string}} data 登录信息
 */
export function feishuLogin(data: LoginData) {
  return request.get('/api/lark_login', { params: data });
}

/**
 * 第三方登录
 * @param data 登录数据
 * @param type 登录类型
 */
export function thirdPartLogin(data: LoginData, type = 'lark') {
  switch (type) {
    case 'lark':
      return feishuLogin(data);
    default:
      return Promise.reject(new Error(`You need a ${type} login implatement`));
  }
}

/**
 * 修改密码
 * @param data 密码数据
 */
export function changePassword(data: PasswordData) {
  return request.post('/api/pw_set', data)
}
