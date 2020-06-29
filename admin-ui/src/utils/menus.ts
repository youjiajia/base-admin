import uuidv4 from 'uuid/v4';

export interface IMenuItem {
  title: string
  path?: string
  id?: string
  icon?: string
  type?: string
  [prop: string]: any
}

export interface IMenu extends IMenuItem {
  children?: IMenuItem[]
}

const menus: IMenu[] = [{
  title: '账单管理',
  path: '/bill',
  id: uuidv4(),
  icon: 'dashboard', // can use el-icon or svg-icon
  type: 'link'
}]

export default menus
