<template>
  <div :class="{'has-logo': showLogo}">
    <logo
      v-if="showLogo"
      :collapse="isCollapse"
    />
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :collapse="isCollapse"
        :background-color="variables.menuBg"
        :text-color="variables.menuText"
        :active-text-color="variables.menuActiveText"
        :unique-opened="false"
        :collapse-transition="false"
        mode="vertical"
      >
        <sidebar-item
          v-for="menu in menus"
          :key="menu.id"
          :item="menu"
          :base-path="menu.path"
          :is-collapse="isCollapse"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script lang="ts">
import { AppModule } from '@/store/modules/app';
import { Component, Prop, Vue } from 'vue-property-decorator';
import Logo from './Logo.vue'
import SidebarItem from './SidebarItem.vue';
import menus from '@/utils/menus';
import variables from '@/styles/_variables.scss';

@Component({
  name: 'SideBar',
  components: {
    SidebarItem,
    Logo
  }
})
export default class extends Vue {
  private menus = menus;

  get sidebar() {
    return AppModule.sidebar;
  }

  get showLogo() {
    return AppModule.sidebar.showLogo;
  }

  get variables() {
    return variables;
  }

  get isCollapse() {
    return !this.sidebar.opened;
  }
}
</script>

<style lang="scss">
.sidebar-container {
  // reset element-ui css
  .horizontal-collapse-transition {
    transition: 0s width ease-in-out, 0s padding-left ease-in-out, 0s padding-right ease-in-out;
  }

  .scrollbar-wrapper {
    overflow-x: hidden !important;
  }

  .el-scrollbar__view {
    height: 100%;
  }

  .el-scrollbar__bar {
    &.is-vertical {
      right: 0px;
    }

    &.is-horizontal {
      display: none;
    }
  }
}
</style>

<style lang="scss" scoped>
.has-logo {
  .el-scrollbar {
    height: calc(100% - 50px);
  }
}
.el-scrollbar {
  height: 100%;
}

.el-menu {
  border: none;
  height: 100%;
  width: 100% !important;
}
</style>
