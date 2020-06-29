<template>
  <div class="login-container">
    <el-form
      ref="loginForm"
      :model="loginForm"
      :rules="loginRules"
      class="login-form"
      autocomplete="on"
      label-position="left"
    >
      <div class="title-container">
        <h3 class="title">小说分成对账系统</h3>
      </div>
      <template v-if="!hideLoginForm">
        <div style="position:relative;margin-bottom:16px;">
          <div class="tips">
            <span>首次登录请点击飞书登录，注意选择正确的飞书主体</span>
          </div>
        </div>
        <el-form-item prop="email">
          <span class="svg-container">
            <svg-icon name="user" />
          </span>
          <el-input
            ref="email"
            v-model="loginForm.email"
            name="email"
            type="text"
            autocomplete="on"
            placeholder="email"
          />
        </el-form-item>

        <el-form-item prop="password">
          <span class="svg-container">
            <svg-icon name="password" />
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="loginForm.password"
            :type="passwordType"
            placeholder="password"
            name="password"
            autocomplete="on"
            @keyup.enter.native="handleLogin"
          />
          <span
            class="show-pwd"
            @click="showPwd"
          >
            <svg-icon
              :name="passwordType === 'password' ? 'eye-off' : 'eye-on'"
            />
          </span>
        </el-form-item>

        <el-button
          :loading="loading"
          type="primary"
          style="width:100%; margin-bottom:30px;"
          @click.native.prevent="handleLogin"
        >登录</el-button>
      </template>
      <el-row>
        <el-col :span="12">
          <el-button
            type="text"
            style="width:100%; margin-bottom:30px;"
            @click.native.prevent="gotoThirdPartLogin('webeye')"
          >正式员工飞书登录</el-button>
        </el-col>
        <el-col :span="12">
          <el-button
            type="text"
            style="width:100%; margin-bottom:30px;"
            @click.native.prevent="gotoThirdPartLogin('outer')"
          >外部员工飞书登录</el-button>
        </el-col>
      </el-row>
    </el-form>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { Dictionary } from 'vue-router/types/router';
import { Form as ElForm, Input } from 'element-ui';
import { IUserState, LoginDataPW } from '@/api/types';
import { Route } from 'vue-router';
import { UserModule } from '@/store/modules/user';
import { getCookie, getToken, removeCookie, removeToken, setCookie, setToken } from '@/utils/cookies';
import { isInLark } from '@/utils/index';
import { login, thirdPartLogin } from '@/api/users';
import pick from 'lodash/pick';
type ProductType = 'webeye' | 'outer';

@Component({
  name: 'Login'
})
export default class extends Vue {
  private validatePassword = (rule: any, value: string, callback: Function) => {
    if (value.length < 6) {
      callback(new Error('The password can not be less than 6 digits'));
    } else {
      callback();
    }
  };
  private loginRules = {
    password: [{ validator: this.validatePassword, trigger: 'blur' }]
  };
  private passwordType = 'password';
  private loading = false;
  private needLogin = false;
  private larkAppid = {
    webeye: 'cli_9ed5d5bde42a900e',
    outer: 'cli_9e1d009dd4e9d00d'
  };
  private platformAppid = '498af4fd-f94e-4beb-9176-08b9d390bb21';
  private loginBaseUrl = 'https://open.feishu.cn/connect/qrconnect/page/sso/';
  private platformUrl = 'http://lark.geezcomics.com/lark/lark_login';
  private loginType = 'lark';
  private hideLoginForm = false;
  private loginForm: LoginDataPW = {
    email: '',
    password: '',
    appId: this.platformAppid
  };

  get state() {
    const env = process.env.NODE_ENV === 'production' ? 'production' : 'development';
    return {
      webeye: `webeye|${this.platformAppid}|${env}`,
      outer: `jxhz|${this.platformAppid}|${env}`
    };
  }
  get goto() {
    return {
      webeye: `${this.loginBaseUrl}?app_id=${this.larkAppid.webeye}&state=${this.state.webeye}&redirect_uri=${this.platformUrl}`,
      outer: `${this.loginBaseUrl}?app_id=${this.larkAppid.outer}&state=${this.state.outer}&redirect_uri=${this.platformUrl}`
    };
  }

  get from(): string {
    return (this.$route.query as Dictionary<string>).from;
  }

  get code() {
    return this.$route.query.code;
  }

  created() {
    this.needLogin = false;
    // 如果有 sessionid 则默认为是已登录
    if (getToken()) {
      this.gotoNextPage();
      return;
    }

    // 如果有 from 字段,暂存到 localStorage
    if (this.from) {
      localStorage.setItem('$_login_from', this.from);
    }
    // 有code,表示是登录平台回跳的页面,尝试利用 code 验证登录
    if (this.code) {
      this.thirdPartLogin();
      return;
    }
    // 如果在飞书内部,跳转到飞书登录
    if (!getCookie('sessionid') && !this.code && isInLark()) {
      this.hideLoginForm = true;
      return;
    }
    this.needLogin = true;
  }

  mounted() {
    if (this.loginForm.email === '') {
      (this.$refs.email as Input).focus();
    } else if (this.loginForm.password === '') {
      (this.$refs.password as Input).focus();
    }
  }

  private showPwd() {
    if (this.passwordType === 'password') {
      this.passwordType = '';
    } else {
      this.passwordType = 'password';
    }
    this.$nextTick(() => {
      (this.$refs.password as Input).focus();
    });
  }

  private async handleLogin() {
    try {
      const valid = await (this.$refs.loginForm as ElForm).validate();
      if (valid) {
        this.loading = true;
        await login(this.loginForm);
        this.loading = false;
        this.gotoNextPage();
      } else {
        return false;
      }
    } catch (e) {
      this.loading = false;
      console.error(e);
      this.$message.error(e.message);
    }
  }
  gotoNextPage() {
    // 如果有from,从哪里来的,跳回到哪里
    let __from = localStorage.getItem('$_login_from');
    // console.log(__from);
    localStorage.removeItem('$_login_from');
    __from = this.from || __from || '';
    // console.log(__from);
    if (__from) {
      this.$router.push({ path: __from });
    } else {
      this.$router.push({ path: '/' });
    }
  }
  private gotoThirdPartLogin(type: ProductType) {
    window.location.href = this.goto[type];
  }
  async thirdPartLogin(this: CVue) {
    try {
      const userInfo = await thirdPartLogin(
        {
          code: this.code
        },
        this.type
      );
      this.$store.commit(
        'SET_USER_INFO',
        pick(userInfo, ['_id', 'department', 'email', 'avatar', 'name', 'token', 'roles', 'webeye']) as IUserState
      );
      this.gotoNextPage();
    } catch (e) {
      this.$message.error(e);
    }
  }
}
</script>

<style lang="scss">
// References: https://www.zhangxinxu.com/wordpress/2018/01/css-caret-color-first-line/
@supports (-webkit-mask: none) and (not (cater-color: $loginCursorColor)) {
  .login-container .el-input {
    input {
      color: $loginCursorColor;
    }
    input::first-line {
      color: $lightGray;
    }
  }
}

.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      height: 47px;
      background: transparent;
      border: 0px;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $lightGray;
      caret-color: $loginCursorColor;
      -webkit-appearance: none;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $loginBg inset !important;
        -webkit-text-fill-color: #fff !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }
}
</style>

<style lang="scss" scoped>
.login-container {
  height: 100%;
  width: 100%;
  overflow: hidden;
  background-color: $loginBg;

  .login-form {
    position: relative;
    width: 520px;
    max-width: 100%;
    padding: 160px 35px 0;
    margin: 0 auto;
    overflow: hidden;
  }

  .tips {
    font-size: 14px;
    color: $lightGray;
    margin-bottom: 10px;
    text-align: center;
    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $darkGray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $lightGray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $darkGray;
    cursor: pointer;
    user-select: none;
  }
}
</style>
