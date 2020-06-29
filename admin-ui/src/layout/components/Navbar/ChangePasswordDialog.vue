<template>
  <el-dialog
    title="密码设置"
    :visible.sync="visible"
    width="30%"
    :before-close="handleClose"
  >
    <el-form
      ref="form"
      :model="form"
      :rules="formRules"
      label-width="80px"
    >
      <el-form-item
        label="密码"
        prop="password"
      >
        <el-input v-model="form.password"></el-input>
      </el-form-item>
      <el-form-item
        label="确认密码"
        prop="repassord"
      >
        <el-input v-model="form.repassord"></el-input>
      </el-form-item>
    </el-form>
    <span
      slot="footer"
      class="dialog-footer"
    >
      <el-button @click="handleClose">取 消</el-button>
      <el-button
        type="primary"
        @click="handleCommit"
      >确 定</el-button>
    </span>
  </el-dialog>
</template>
<script lang="ts">
import { Component, PropSync, Ref, Vue } from 'vue-property-decorator';
import { Form as ElForm } from 'element-ui';
import { changePassword } from '@/api/users';
import { isValidPassword } from '@/utils/validate';

interface PasswordForm {
  password: string;
  repassord: string;
}

@Component({
  name: 'ChangePasswordDialog'
})
export default class extends Vue {
  @PropSync('show', { type: Boolean }) visible!: boolean;

  private validatePassword = (rule: any, value: string, callback: Function) => {
    if (isValidPassword(value)) {
      callback();
    } else {
      callback(new Error('密码必须为6到18位,数字字母符号的组合'));
    }
  };

  private validateRepassword = (rule: any, value: string, callback: Function) => {
    if (value !== this.form.password) {
      callback(new Error('两次输入的密码不相同'));
    } else {
      callback();
    }
  };

  private form: PasswordForm = {
    password: '',
    repassord: ''
  };

  private formRules = {
    password: [{ validator: this.validatePassword, trigger: 'blur' }],
    repassord: [{ validator: this.validateRepassword, trigger: 'blur' }]
  };

  @Ref('form') readonly passwordForm!: ElForm;

  private resetForm() {
    this.form = {
      password: '',
      repassord: ''
    };
  }

  private handleClose() {
    this.resetForm();
    this.visible = false;
  }
  private async handleCommit() {
    try {
      const valid = await this.passwordForm.validate();
      if (valid) {
        await changePassword({ password: this.form.password });
        this.$message.success('密码设置成功');
        this.handleClose();
      } else {
        return false;
      }
    } catch (e) {
      console.error(e.message);
    }
  }
}
</script>
<style lang="scss" scoped>
</style>
