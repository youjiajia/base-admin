<template>
  <div class="detail-table__container">
    <div>
      <el-input
        v-model="bookname"
        placeholder="书名"
      ></el-input>
    </div>
    <el-table
      :data="pagedTableData"
      style="width: 100%"
      class="roboto-font"
    >
      <el-table-column
        prop="name"
        label="书名"
      ></el-table-column>
      <el-table-column
        prop="pv"
        label="PV"
        align="right"
        width="180"
      ></el-table-column>
      <el-table-column
        prop="earn"
        label="分成"
        align="right"
        width="180"
      >
        <template #default="{row}">
          <span>{{ row.earn.toFixed(2) }}</span>
        </template>
      </el-table-column>
    </el-table>
    <div style="text-align:right;">
      <el-pagination
        layout="prev, pager, next"
        :total="filtedTableData.length"
        :page-size="pagenation.pageSize"
        :current-page.sync="pagenation.currentPage"
        :pager-count="pagenation.pagerCount"
      ></el-pagination>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import { IBillItem } from '@/api/types';
@Component({
  name: 'CompDetailTable'
})
export default class extends Vue {
  @Prop({ default: () => [] }) private tableData!: Array<IBillItem>;
  private bookname: string = '';
  private pagenation = {
    pageSize: 10,
    currentPage: 1,
    pagerCount: 9
  };

  get filtedTableData() {
    const name = this.bookname.trim().toLowerCase();
    if (!name) {
      return this.tableData;
    }
    return this.tableData.filter(book => book.name.toLowerCase().includes(name));
  }

  get pagedTableData() {
    const totalPage = Math.ceil(this.filtedTableData.length / this.pagenation.pageSize);
    const currentPage = this.pagenation.currentPage <= totalPage ? this.pagenation.currentPage : totalPage;
    const skip = this.pagenation.pageSize * (currentPage - 1);
    return this.filtedTableData.slice(skip, skip + this.pagenation.pageSize);
  }
}
</script>
<style lang="scss" scoped>
.detail-table__ {
  &container {
  }
}
</style>
