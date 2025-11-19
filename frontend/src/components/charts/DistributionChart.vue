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
    
})
</script>

<style scoped>

</style>