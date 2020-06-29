import Cookies from 'js-cookie'

// common
export const getCookie: (key: string) => string | undefined = (key) => Cookies.get(key)
export const setCookie: (key: string, payload: any) => void = (key, payload) => {
  if (typeof payload !== 'string') {
    payload = JSON.stringify(payload)
  }
  Cookies.set(key, payload)
}
export const removeCookie: (key: string) => void = (key) => Cookies.remove(key)

// App
const sidebarStatusKey = 'sidebar_status'
export const getSidebarStatus = () => getCookie(sidebarStatusKey)
export const setSidebarStatus = (sidebarStatus: string) => setCookie(sidebarStatusKey, sidebarStatus)

// User
const tokenKey = 'x-token'
export const getToken = () => getCookie(tokenKey)
export const setToken = (token: string) => setCookie(tokenKey, token)
export const removeToken = () => removeCookie(tokenKey)
