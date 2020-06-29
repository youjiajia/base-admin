<template>
  <div
    :class="['menu-wrapper', isCollapse ? 'simple-mode' : 'full-mode', {'first-level': isFirstLevel}]"
  >
    <template v-if="theOnlyOneChild && !theOnlyOneChild.children">
      <sidebar-item-link :to="resolvePath(theOnlyOneChild.path)">
        <el-menu-item
          :index="resolvePath(theOnlyOneChild.path)"
          :class="{'submenu-title-noDropdown': isFirstLevel}"
        >
          <svg-icon
            v-if="theOnlyOneChild.icon"
            :name="theOnlyOneChild.icon"
          />
          <span
            v-if="theOnlyOneChild.title"
            slot="title"
          >{{ theOnlyOneChild.title }}</span>
        </el-menu-item>
      </sidebar-item-link>
    </template>
    <el-submenu
      v-else
      :index="resolvePath(item.path)"
      popper-append-to-body
    >
      <template slot="title">
        <svg-icon
          :name="item.icon"
        />
        <span
          slot="title"
        >{{ item.title }}</span>
      </template>
      <template v-if="item.children">
        <sidebar-item
          v-for="child in item.children"
          :key="child.path"
          :item="child"
          :is-collapse="isCollapse"
          :is-first-level="false"
          :base-path="resolvePath(child.path)"
          class="nest-menu"
        />
      </template>
    </el-submenu>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import { IMenu } from '@/utils/menus';
import { isExternal } from '@/utils/validate';
import SidebarItemLink from './SidebarItemLink.vue';
import path from 'path';

@Component({
  // Set 'name' here to prevent uglifyjs from causing recursive component not work
  // See https://medium.com/haiiro-io/element-component-name-with-vue-class-component-f3b435656561 for detail
  name: 'SidebarItem',
  components: {
    SidebarItemLink
  }
})
export default class extends Vue {
  @Prop({ required: true }) private item!: IMenu;
  @Prop({ default: false }) private isCollapse!: boolean;
  @Prop({ default: true }) private isFirstLevel!: boolean;
  @Prop({ default: '' }) private basePath!: string;

  get showingChildNumber() {
    if (this.item.children) {
      const showingChildren = this.item.children.filter(item => {
        if (item.hidden) {
          return false;
        } else {
          return true;
        }
      });
      return showingChildren.length;
    }
    return 0;
  }

  get theOnlyOneChild() {
    if (this.showingChildNumber > 1) {
      return null;
    }
    if (this.item.children) {
      for (let child of this.item.children) {
        if (!child || !child.hidden) {
          return child;
        }
      }
    }
    // If there is no children, return itself with path removed,
    // because this.basePath already conatins item's path information
    return { ...this.item, path: '' };
  }

  private resolvePath(item: IMenu, isRouterLink = false) {
    if (item.href && isExternal(item.href)) {
      return item.href;
    }

    if (isExternal(this.basePath)) {
      return this.basePath;
    }
    const __path = path.resolve(this.basePath, item.path || '');
    // console.log(this.$router.resolve({ path: __path, query: item.query }));
    return isRouterLink ? this.$router.resolve({ path: __path, query: item.query }).href : __path;
  }
}
</script>

<style lang="scss">
.el-submenu.is-active > .el-submenu__title {
  color: $subMenuActiveText !important;
}

.full-mode {
  .nest-menu .el-submenu > .el-submenu__title,
  .el-submenu .el-menu-item {
    min-width: $sideBarWidth !important;
    background-color: $subMenuBg !important;

    &:hover {
      background-color: $subMenuHover !important;
    }
  }
}

.simple-mode {
  &.first-level {
    .submenu-title-noDropdown {
      padding: 0 !important;
      position: relative;

      .el-tooltip {
        padding: 0 !important;
      }
    }

    .el-submenu {
      overflow: hidden;

      & > .el-submenu__title {
        padding: 0px !important;

        .el-submenu__icon-arrow {
          display: none;
        }

        & > span {
          visibility: hidden;
        }
      }
    }
  }
}
</style>

<style lang="scss" scoped>
.svg-icon {
  margin-right: 16px;
}

.simple-mode {
  .svg-icon {
    margin-left: 20px;
  }
}
</style>
