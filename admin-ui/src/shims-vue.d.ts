declare module '*.vue' {
  import Vue from 'vue'
  export default Vue
}

declare module '*.png'

declare type CVue = Vue & { [prop: string]: any }
