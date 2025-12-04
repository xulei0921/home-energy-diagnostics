<template>
    <div class="chart-container">
        <canvas ref="chartRef"></canvas>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { getEnergyCostsDistribution } from '@/api/analysis';
import Chart from 'chart.js/auto'

const billData = ref(null)
// 2. 定义一个 ref 来获取 canvas 元素
const chartRef = ref(null)
// 定义一个 ref 来存储 Chart 实例，方便后续销毁和更新
const chartInstance = ref(null)

const BILL_TYPE_COLOR_MAP = {
    'electricity': {
        bg: 'rgba(75, 192, 192, 0.7)',
        border: 'rgba(255, 255, 255, 1)'
    },
    'gas': {
        bg: 'rgba(243, 104, 18, 0.7)',
        border: 'rgba(255, 255, 255, 1)'
    },
    'water': {
        bg: 'rgba(30, 144, 255, 0.7)',
        border: 'rgba(255, 255, 255, 1)'
    }
}

// 默认颜色
const DEFAULT_COLOR = {
    bg: 'rgba(153, 102, 255, 0.7)',
    border: 'rgba(255, 255, 255, 1)'
}

const fetchEnergyCostsDistribution = async () => {
    try {
        const res = await getEnergyCostsDistribution()
        // console.log(res)
        billData.value = res
    } catch (error) {
        console.error(error)
        billData.value = { items: [], total_amount: 0, month: '' }
    }
}

const formatChartData = (data) => {
    // console.log(billData.value)
    if (!data || !data.items || data.items.length === 0) {
        return { labels: [], datasets: [{ data: [] }] }
    }

    // const labels = data.items.map(item => {
    //     // 将英文类型转换为中文
    //     const typeMap = {
    //         'electricity': '电费',
    //         'gas': '燃气费',
    //         'water': '水费'
    //     }
    //     return typeMap[item.bill_type] || item.bill_type
    // })

    // const values = data.items.map(item => item.amount)

    const labels = []
    const values = []
    const bgColors = []
    const borderColors = []

    data.items.forEach(item => {
        // 1. 处理标签 (英文转中文)
        const typeMap = {
            'electricity': '电费',
            'gas': '燃气费',
            'water': '水费'
        }
        labels.push(typeMap[item.bill_type] || item.bill_type)

        // 2. 处理数值
        values.push(item.amount || 0)

        // 3. 按 bill_type 匹配颜色
        const colorConfig = BILL_TYPE_COLOR_MAP[item.bill_type] || DEFAULT_COLOR
        bgColors.push(colorConfig.bg)
        borderColors.push(colorConfig.border)
    })

    return {
        labels: labels,
        datasets: [{
            label: '账单金额(元)',
            data: values,
            backgroundColor: bgColors,
            borderColor: borderColors,
            borderWidth: 1
        }]
    }
}

// 3. 封装一个初始化图表的函数
const initChart = () => {
    // 如果已有实例，先销毁
    if (chartInstance.value) {
        chartInstance.value.destroy()
        chartInstance.value = null
    }

    // 避免 chartRef 未渲染导致的 null 错误
    if (!chartRef.value) return

    // 获取 canvas 上下文
    const ctx = chartRef.value.getContext('2d')
    if (!ctx) return

    const formattedDate = formatChartData(billData.value)

    // 创建新实例
    chartInstance.value = new Chart(ctx, {
        type: 'doughnut',
        data: formattedDate,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // 添加事件处理以防止销毁后的事件触发
            onHover: (event, activeElements) => {
                if (!chartInstance.value) {
                    return
                }
            },
            onClick: (event, activeElements) => {
                if (!chartInstance.value) {
                    return
                }
            },
            plugins: {
                legend: {
                    position: 'right'  // 图例位置
                },
                title: {
                    display: true,
                    align: 'start',
                    text: `${billData.value.month}账单分布 (总计: ${billData.value.total_amount}元)`,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        // 自定义提示框内容，显示金额和百分比
                        label: function(context) {
                            const label = context.label || ''
                            const value = context.raw || 0
                            const percentage = ((value / billData.value.total_amount) * 100).toFixed(2)
                            return `${label}: ${value}元 (${percentage}%)`
                        }
                    }
                }
            },
            cutout: '60%'  // 控制环形的粗细，'60%' 表示中间空白部分占 60%'
        }
    })
}

// 5. 监听 props 变化， 如果数据或类型变了，就更新图表
watch(
    () => billData.value,
    () => {
        if (chartRef.value) {
            try {
                initChart()
            } catch (error) {
                console.error('图表初始化失败:', error)
            }
        }
    },
    { deep: true }
)

// 4. 在组件挂载后初始化图表
onMounted(async () => {
    try {
        await fetchEnergyCostsDistribution()
        initChart()
    } catch (error) {
        console.error('组件挂载时初始化失败:', error)
    }
})

// 6. 在组件卸载前销毁图表实例，防止内存泄露
onUnmounted(() => {
    if (chartInstance.value) {
        try {
            chartInstance.value.destroy()
        } catch (error) {
            console.warn('图表销毁时发生错误:', error)
        } finally {
            chartInstance.value = null
        }
    }
})
</script>

<style scoped>
.chart-container {
    
}
</style>