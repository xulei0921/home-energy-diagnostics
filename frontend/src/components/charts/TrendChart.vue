<template>
  <div class="chart-wrapper">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import Chart from 'chart.js/auto'

// 1. 定义 props，让父组件可以传递数据和配置
const props = defineProps({
  type: {
    type: String,
    required: true,
  },
  data: {
    type: Object,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({}),
  },
})

// 2. 定义一个 ref 来获取 canvas 元素
const chartRef = ref(null)
// 定义一个 ref 来存储 Chart 实例，方便后续销毁和更新
const chartInstance = ref(null)

// 3. 封装一个初始化图表的函数
const initChart = () => {
  // 如果已有实例，先销毁
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }

  // 获取 canvas 上下文
  const ctx = chartRef.value.getContext('2d')

  // 创建新实例
  chartInstance.value = new Chart(ctx, {
    type: props.type,
    data: props.data,
    options: {
      // 合并默认选项和父组件传入的选项
      responsive: true,
      maintainAspectRatio: false,
      ...props.options,
    },
  })
}

// 4. 在组件挂载后初始化图表
onMounted(() => {
  initChart()
})

// 5. 监听 props 变化，如果数据或类型变了，就更新图表
watch(
  () => [props.type, props.data],
  () => {
    if (chartRef.value) {
      initChart()
    }
  },
  { deep: true }  // 深度监听，确保对象内部属性变化也能被检测到
)

// 6. 在组件卸载前销毁图表实例，防止内存泄漏
onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 400px;

}
</style>