import { Message, MessageBox } from 'element-ui'
import { UserModule } from '@/store/modules/user'
import axios from 'axios'

const service = axios.create({
  baseURL: process.env.VUE_APP_BASE_API,
  timeout: 5000
})

// Request interceptors
service.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    Promise.reject(error)
  }
)

// Response interceptors
service.interceptors.response.use(
  (response) => {
    if (response.data.success) {
      return Promise.resolve<any>(response.data.data);
    }
    const errMsg = response.data.msg || response.data.message;
    if (errMsg === 'need login') {
      UserModule.LogOut();
    }
    return Promise.reject<any>(new Error(errMsg));
  },
  (error: any) => {
    Message({
      message: error.message,
      type: 'error',
      duration: 5 * 1000
    })
    return Promise.reject(error)
  }
)

export default service
