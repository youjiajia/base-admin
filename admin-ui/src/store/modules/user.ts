import { Action, Module, Mutation, VuexModule, getModule } from 'vuex-module-decorators'
import { IUserState } from '@/api/types'
import { getToken, removeToken } from '@/utils/cookies'
import { getUserInfo, logout } from '@/api/users'
import pick from 'lodash/pick';
import store from '@/store'

@Module({ dynamic: true, store, name: 'user' })
class User extends VuexModule implements IUserState {
  public _id = ''
  public department = ''
  public email = ''
  public avatar = ''
  public name = ''
  public token = getToken() || ''
  public webeye = 0
  public roles: string[] = []

  get isAdmin() {
    return this.roles.includes('admin')
  }

  @Mutation
  private SET_ID(id: string) {
    this._id = id;
  }

  @Mutation
  private SET_DEPARTMENT(department: string) {
    this.department = department;
  }

  @Mutation
  private SET_EMAIL(email: string) {
    this.email = email;
  }

  @Mutation
  private SET_AVATAR(avatar: string) {
    this.avatar = avatar
  }

  @Mutation
  private SET_NAME(name: string) {
    this.name = name
  }

  @Mutation
  private SET_ROLES(roles: string[]) {
    this.roles = roles
  }

  @Mutation
  private SET_USER_INFO({ _id = '', department = '', email = '', avatar = '', name = '', token = '', webeye = 0, roles = [] }: IUserState) {
    this._id = _id;
    this.department = department;
    this.email = email;
    this.avatar = avatar;
    this.name = name;
    this.token = token;
    this.webeye = webeye;
    this.roles = roles;
  }

  @Mutation
  private RESET_USER_INFO() {
    this._id = '';
    this.department = '';
    this.email = '';
    this.avatar = '';
    this.name = '';
    this.token = '';
    this.webeye = 0;
    this.roles = [];
  }

  @Action
  public ResetToken() {
    removeToken()
  }

  @Action
  public async GetUserInfo() {
    const data = await getUserInfo()
    if (!data) {
      throw Error('Verification failed, please Login again.')
    }
    this.SET_USER_INFO((pick(data, ['_id', 'department', 'email', 'avatar', 'name', 'token', 'roles', 'webeye']) as IUserState))
  }

  @Action
  public async LogOut() {
    await logout()
    this.RESET_USER_INFO()
    removeToken()
  }
}

export const UserModule = getModule(User)
