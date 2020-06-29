<template>
  <div
    v-loading="loading"
    class="dashboard__container"
  >
    <el-row>
      <el-col :span="24">
        <el-form
          ref="queryForm"
          :inline="true"
          :model="query"
          :rules="formRules"
          class="demo-form-inline"
        >
          <el-form-item
            label="年"
            prop="year"
          >
            <el-input
              v-model="query.year"
              placeholder="年"
              :disabled="!isAdmin"
            ></el-input>
          </el-form-item>
          <el-form-item label="月">
            <el-select
              v-model="query.month"
              placeholder="月"
              :disabled="!isAdmin"
            >
              <el-option
                v-for="option in MonthOptions"
                :key="option"
                :label="option"
                :value="option"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              @click="handleExport(true,undefined)"
            >导出</el-button>
            <el-button
              type="primary"
              @click="handleExport(undefined,undefined)"
            >导出(无PV)</el-button>
            <el-button
              type="primary"
              @click="handleShowConfig"
            >配置</el-button>
          </el-form-item>
        </el-form>
      </el-col>
      <el-col :span="24">
        <el-table
          :data="billDetail"
          style="width: 100%"
          class="roboto-font"
          show-summary
        >
          <el-table-column type="expand">
            <template #default="{row}">
              <DetailTable :table-data="row.items"></DetailTable>
            </template>
          </el-table-column>
          <el-table-column
            prop="cp_name"
            label="CP Name"
            width="180"
          ></el-table-column>
          <el-table-column
            prop="pv"
            label="PV"
            width="180"
            align="right"
          ></el-table-column>
          <el-table-column
            prop="gain"
            label="收入"
            width="180"
            align="right"
          >
            <template #default="{row}">
              <span>{{ row.gain.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="earn"
            label="分成"
            width="180"
            align="right"
          >
            <template #default="{row}">
              <span>{{ row.earn.toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="base_revision"
            label="保底修正"
            width="180"
            align="right"
          >
            <template #default="{row}">
              <span>{{ row.base_revision .toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            align="center"
          >
            <template #default="{row}">
              <el-button
                size="small"
                type="primary"
                @click="handleExport(true,true,row.cp_code)"
              >导出</el-button>
              <el-button
                size="small"
                type="primary"
                @click="handleExport(undefined,true,row.cp_code)"
              >导出(无PV)</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>
    <el-drawer
      title="编辑配置"
      size="640"
      :visible.sync="showConfig"
      direction="rtl"
      class="scroll-drawer"
      :show-close="false"
    >
      <template #title>
        <el-button
          type="primary"
          :disabled="!configChanged"
          @click="doQuery"
        >保存配置并查询</el-button>
      </template>
      <el-form
        ref="configForm"
        :model="billConfig"
        label-width="80px"
        :disabled="!isAdmin"
      >
        <el-form-item label="总计">
          <el-input-number
            v-model="billConfig.total"
            style="width:454px;"
            :precision="2"
            :step="1000"
            :min="0"
          ></el-input-number>
        </el-form-item>
      </el-form>
      <el-form
        v-for="line in billConfig.items"
        ref="configItemsForm"
        :key="line.cp_name"
        :model="billConfig"
        :inline="true"
        label-width="80px"
        :disabled="!isAdmin"
      >
        <el-form-item :label="line.cp_name || '匿名'">
          <el-input-number
            v-model="line.percentage"
            :min="0"
            :max="1"
            :step="0.01"
          ></el-input-number>
        </el-form-item>
        <el-form-item label="保底">
          <el-input-number
            v-model="line.base"
            :precision="2"
            :step="1000"
            :min="0"
          ></el-input-number>
        </el-form-item>
      </el-form>
    </el-drawer>
  </div>
</template>

<script lang="ts">
import { BillExportBaseURL, exportBill, getBillConfig, getBillDetail, updateBillConfig } from '@/api/bill';
import { Component, Ref, Vue, Watch } from 'vue-property-decorator';
import { Form as ElForm, Table as ElTable } from 'element-ui';
import { IBill, IBillConfig } from '@/api/types';
import { UserModule } from '@/store/modules/user';
import DetailTable from './CompDetailTable.vue';
import cloneDeep from 'lodash/cloneDeep';
// 初始化月份选项
const MonthOptions = Array.from({ length: 12 }).map((item, index) => `${index + 1}`.padStart(2, '0'));
// 初始化月份,默认看上个月的数据
const [Year, Month] = (() => {
  let month: number | string = new Date().getMonth();
  let year: number | string = new Date().getFullYear();
  month = `${month === 0 ? 12 : month}`.padStart(2, '0');
  year = `${month === '12' ? year - 1 : year}`;
  return [year, month];
})();

@Component({
  name: 'Bill',
  components: { DetailTable }
})
export default class extends Vue {
  private loading = false;
  private configChanged = false;
  private dataInited = false;
  private showConfig = false;
  private billDetail: IBill[] = [];
  private billConfig: IBillConfig = {
    total: 0,
    items: []
  };
  private billConfigBak: IBillConfig = {
    total: 0,
    items: []
  };
  private query = {
    year: Year,
    month: Month
  };
  private MonthOptions = MonthOptions;
  // 检查年份 2020~2039
  private validateYear(rule: any, value: string, callback: Function) {
    if (!/^(202|203)[0-9]$/.test(value)) {
      callback(new Error('请填写正确的年份,2020~2039'));
    } else {
      callback();
    }
  }
  private formRules = {
    year: [{ validator: this.validateYear, trigger: 'blur' }]
  };

  get billDate() {
    return `${this.query.year}${this.query.month}`;
  }
  get isAdmin() {
    return UserModule.isAdmin;
  }
  @Ref('queryForm') readonly queryForm!: ElForm;
  @Ref('configForm') readonly configForm!: ElForm;

  private async created() {
    try {
      this.loading = true;
      await Promise.all([this.fetchBillDetail(), this.fetchBillConfig()]);
      this.dataInited = true;
    } catch (e) {
      console.error(e);
    } finally {
      this.loading = false;
    }
  }

  @Watch('billConfig', { deep: true })
  private handleBillConifgChange() {
    if (this.dataInited) {
      this.configChanged = true;
    }
  }
  @Watch('query', { deep: true })
  private async handleQueryChange() {
    this.billConfig = cloneDeep(this.billConfigBak);
    await this.$nextTick();
    this.configChanged = false;
    await this.$nextTick();
    this.doQuery();
  }
  private handleShowConfig() {
    this.showConfig = true;
  }
  private async fetchBillDetail() {
    try {
      this.billDetail = await getBillDetail({
        bill_date: this.billDate,
        novel: true
      });
    } catch (e) {
      console.error(e);
    }
  }
  private async fetchBillConfig() {
    try {
      this.billConfigBak = await getBillConfig({ bill_date: this.billDate });
      this.billConfigBak = this.billConfigBak || { total: 0, items: [] };
      this.billConfig = cloneDeep(this.billConfigBak);
    } catch (e) {
      console.error(e);
    }
  }
  private async updateBillConfig() {
    try {
      await updateBillConfig(this.billConfig);
      this.configChanged = false;
    } catch (e) {
      console.error(e);
    }
  }
  private async doQuery() {
    try {
      this.showConfig = false;
      this.loading = true;
      await this.queryForm.validate();
      if (this.configChanged) {
        await this.updateBillConfig();
      } else {
        await this.fetchBillConfig();
      }
      await this.fetchBillDetail();
    } catch (e) {
      console.error(e);
    } finally {
      this.loading = false;
    }
  }
  private handleExport(pv?: string, isNovel?: string, provider?: string) {
    const url = this.$router.resolve({
      path: BillExportBaseURL,
      query: {
        bill_date: this.billDate,
        pv,
        is_novel: isNovel,
        provider
      }
    }).href;
    exportBill(url);
  }
}
</script>

<style lang="scss" scoped>
.dashboard__ {
  &container {
    padding: 16px;
    height: 100%;
  }
}
</style>
