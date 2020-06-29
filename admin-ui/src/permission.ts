import 'nprogress/nprogress.css'
import { Message } from 'element-ui'
import { Route } from 'vue-router'
import { UserModule } from '@/store/modules/user'
import { getToken } from '@/utils/cookies'
import NProgress from 'nprogress'
import router from './router'

NProgress.configure({ showSpinner: false })

const whiteList = ['/login']

router.beforeEach(async (to: Route, _: Route, next: any) => {
  // Start progress bar
  NProgress.start()

  // Determine whether the user has logged in
  if (getToken()) {
    if (to.path === '/login') {
      // If is logged in, redirect to the home page
      next({ path: '/' })
      NProgress.done()
    } else {
      // Check whether the user has obtained his permission roles
      if (UserModule.name === '') {
        try {
          // Get user info, including roles
          await UserModule.GetUserInfo()
          // Set the replace: true, so the navigation will not leave a history record
          next({ ...to, replace: true })
        } catch (err) {
          // Remove token and redirect to login page
          UserModule.ResetToken()
          Message.error(err || 'Has Error')
          next(`/login?from=${to.path}`)
          NProgress.done()
        }
      } else {
        next()
        NProgress.done()
      }
    }
  } else {
    // Has no token
    if (whiteList.indexOf(to.path) !== -1) {
      // In the free login whitelist, go directly
      next()
      NProgress.done()
    } else {
      // Other pages that do not have permission to access are redirected to the login page.
      next(`/login?from=${to.path}`)
      NProgress.done()
    }
  }
})
