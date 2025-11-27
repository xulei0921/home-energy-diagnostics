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

const fetchEnergyCostsDistribution = async () => {
    try {
        const res = await getEnergyCostsDistribution()
        // console.log(res)
        billData.value = res
    } catch (error) {
        console.error(error)
    }
}

const formatChartData = (data) => {
    // console.log(billData.value)
    if (!data || !data.items || data.items.length === 0) {
        return { labels: [], datasets: [{ data: [] }] }
    }

    const labels = data.items.map(item => {
        // 将英文类型转换为中文
        const typeMap = {
            'electricity': '电费',
            'gas': '燃气费',
            'water': '水费'
        }
        return typeMap[item.bill_type] || item.bill_type
    })

    const values = data.items.map(item => item.amount)

    return {
        labels: labels,
        datasets: [{
            label: '账单金额(元)',
            data: values,
            backgroundColor: [
                'rgba(75, 192, 192, 0.7)',
                'rgba(243, 104, 18, 0.7)',
                'rgba(30, 144, 255, 0.7)'
            ],
            borderColor: [
                'rgba(255, 255, 255, 1)',
                'rgba(255, 255, 255, 1)',
                'rgba(255, 255, 255, 1)'
            ],
            borderWidth: 1
        }]
    }
}

// 3. 封装一个初始化图表的函数
const initChart = () => {
    // 如果已有实例，先销毁
    if (chartInstance.value) {
        chartInstance.value.destroy()
    }

    // 获取 canvas 上下文
    const ctx = chartRef.value.getContext('2d')

    const formattedDate = formatChartData(billData.value)

    // 创建新实例
    chartInstance.value = new Chart(ctx, {
        type: 'doughnut',
        data: formattedDate,
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
            initChart()
        }
    },
    { deep: true }
)

// 4. 在组件挂载后初始化图表
onMounted(async () => {
    await fetchEnergyCostsDistribution()
    initChart()
})

// 6. 在组件卸载前销毁图表实例，防止内存泄露
onUnmounted(() => {
    if (chartInstance.value) {
        chartInstance.value.destroy()
    }
})
</script>

<style scoped>
.chart-container {
    
}
</style>