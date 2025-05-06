<template>
  <div class="ddi-container">
    <h1>DDI 检测</h1>
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>药物选择</span>
        </div>
      </template>
      <el-form :inline="true" :model="formState" class="drug-selection-form">
        <el-form-item label="药物一">
          <el-select
            v-model="formState.drug1"
            placeholder="请选择药物一"
            filterable
            clearable
            :loading="loadingDrugs"
            style="width: 240px"
          >
            <el-option
              v-for="item in drugList"
              :key="item.drug_id"
              :label="item.name"
              :value="item.drug_id">
              <!-- 假设药物对象有 name 属性用于显示 -->
              <span style="float: left">{{ item.name }}</span>
              <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px;">
                ID: {{ item.drug_id }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="药物二">
          <el-select
            v-model="formState.drug2"
            placeholder="请选择药物二"
            filterable
            clearable
            :loading="loadingDrugs"
            style="width: 240px"
          >
            <el-option
               v-for="item in drugList"
              :key="item.drug_id"
              :label="item.name"
              :value="item.drug_id">
               <!-- 假设药物对象有 name 属性用于显示 -->
              <span style="float: left">{{ item.name }}</span>
              <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px;">
                ID: {{ item.drug_id }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQueryDDI" :loading="loadingDDI">
            查询互作用
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="box-card result-card" v-if="ddiResult !== null && ddiResult.length > 0">
       <template #header>
        <div class="card-header">
          <span>预测结果</span>
        </div>
      </template>
      <div>
        <!-- 使用无序列表展示 DDI 结果 -->
        <ul>
          <li v-for="(interaction, index) in ddiResult" :key="index">
            {{ interaction }}
          </li>
        </ul>
      </div>
    </el-card>
    <!-- 添加一个卡片用于显示没有检测到互作用的情况 -->
    <el-card class="box-card result-card" v-else-if="ddiResult !== null && ddiResult.length === 0">
       <template #header>
        <div class="card-header">
          <span>预测结果</span>
        </div>
      </template>
      <div>
        <p>未检测到这两个药物之间已知的相互作用。</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { fetchDrugList, fetchDDI } from '@/api/api';
import { notify } from '@/composables/utils';

const drugList = ref([]); // 药物列表
const loadingDrugs = ref(false); // 加载药物列表状态
const loadingDDI = ref(false); // 查询 DDI 状态
const formState = reactive({ // 表单状态
  drug1: '',
  drug2: ''
});
const ddiResult = ref(null); // DDI 结果，预期是一个字符串数组

// 获取药物列表的函数
const getDrugList = async () => {
  loadingDrugs.value = true;
  ddiResult.value = null; // 开始获取新列表时清空上次结果
  try {
    const res = await fetchDrugList();
    console.log(res);
     // 假设后端返回的数据结构是 { code: 200, data: [...] }
    if (res && res.code === 200) {
       // 注意：请根据你后端实际返回的药物列表字段调整这里的赋值
       // 假设后端返回的药物对象数组在 res.data 中，且每个对象有 drug_id 和 name 字段
      drugList.value = res.data || [];
      if (drugList.value.length === 0) {
         notify('warning', '获取到的药物列表为空');
      }
    } else {
      // 如果 axios 拦截器没有处理，这里可以处理 API 返回的业务错误
      notify('error', res.message || '获取药物列表失败');
      drugList.value = []; // 清空列表防止使用旧数据
    }
  } catch (error) {
    // 如果 axios 拦截器处理了错误，这里可能不会执行
    // 如果需要，可以在这里添加额外的错误处理
    console.error("获取药物列表失败:", error);
     drugList.value = []; // 清空列表
    // notify 已在 axios 拦截器中调用
  } finally {
    loadingDrugs.value = false;
  }
};

// 处理查询 DDI 的函数
const handleQueryDDI = async () => {
  if (!formState.drug1 || !formState.drug2) {
    notify('warning', '请选择两种药物');
    return;
  }
  if (formState.drug1 === formState.drug2) {
     notify('warning', '请选择两种不同的药物');
    return;
  }

  loadingDDI.value = true;
  ddiResult.value = null; // 清空上一次结果
  try {
    const res = await fetchDDI(formState.drug1, formState.drug2);
     // 假设后端成功返回的数据结构是 { code: 200, data: [...] }，其中 data 是字符串列表
     if (res && res.code === 200) {
        // 确保 res.data 是一个数组
        ddiResult.value = Array.isArray(res.data) ? res.data : [];
        notify('success', '查询成功');
        if (ddiResult.value.length === 0) {
           console.log("查询成功，但未发现相互作用记录。");
           // 可选：如果需要，可以为"未发现记录"添加特定的 notify
           // notify('info', '未检测到相互作用');
        }
     } else {
       ddiResult.value = null; // 查询失败时清空结果
       notify('error', res.message || '查询 DDI 失败');
     }
  } catch (error) {
    ddiResult.value = null; // 异常时清空结果
    console.error("查询 DDI 失败:", error);
     // notify 已在 axios 拦截器中调用
  } finally {
    loadingDDI.value = false;
  }
};

// 组件挂载后获取药物列表
onMounted(() => {
  getDrugList();
});
</script>

<style scoped>
.ddi-container {
  padding: 20px;
}

.box-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drug-selection-form .el-form-item {
  margin-bottom: 0; /* 让表单项更紧凑 */
}

.result-card {
  margin-top: 20px;
}

/* 如果需要让 pre 标签换行 */
pre {
  white-space: pre-wrap;       /* CSS 3 */
  white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 */
  white-space: -o-pre-wrap;    /* Opera 7 */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */
}

/* 为列表项添加一些样式 */
.result-card ul {
  padding-left: 20px; /* 添加内边距 */
  margin: 0; /* 移除默认外边距 */
}

.result-card li {
  margin-bottom: 10px; /* 增加列表项之间的间距 */
  line-height: 1.6; /* 增加行高，提高可读性 */
  text-align: left; /* 确保文本靠左对齐 */
}
</style>
