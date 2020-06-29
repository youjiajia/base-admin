<template>
  <div
    class="sidebar-logo-container"
    :class="{'collapse': collapse}"
  >
    <div
      key="collapse"
      class="sidebar-logo-link"
    >
      <img
        v-if="logo"
        :src="logo"
        class="sidebar-logo"
      />
      <h1
        v-if="!collapse"
        class="sidebar-title"
      >{{ title }}</h1>
      <i class="el-icon-arrow-down el-icon--right"></i>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import logo from '@/assets/icon.png';

@Component({
  name: 'SidebarLogo'
})
export default class extends Vue {
  @Prop({ required: true, default: false }) private collapse!: boolean;
  private title: string = '小说分成对账系统';
  private logo: string = logo;
}
</script>

<style lang="scss" scoped>
.sidebarLogoFade-enter-active {
  transition: opacity 1.5s;
}

.sidebarLogoFade-enter,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

.sidebar-logo-container {
  position: relative;
  width: 100%;
  height: 50px;
  line-height: 50px;
  background: $menuBg;
  text-align: center;
  overflow: hidden;

  & .sidebar-logo-link {
    height: 100%;
    width: 100%;
    cursor: pointer;
    & .sidebar-logo {
      width: 32px;
      height: 32px;
      vertical-align: middle;
      margin-right: 12px;
    }

    & .sidebar-title {
      display: inline-block;
      margin: 0;
      color: #fff;
      font-weight: 600;
      line-height: 50px;
      font-size: 14px;
      font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
      vertical-align: middle;
    }
  }

  &.collapse {
    .sidebar-logo {
      margin-right: 0px;
    }
  }
}
</style>
