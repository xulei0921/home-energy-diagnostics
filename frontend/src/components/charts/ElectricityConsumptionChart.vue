<template>
    <div class="chart-wrapper">
        <div
            class="chart-container"
            v-loading="isLoading"
            element-loading-text="正在加载中..."
        >
            <!-- 无数据时显示提示 -->
            <div v-if="!isLoading && (!deviceData || deviceData.length === 0)" class="no-data-container">
                <el-empty description="暂无数据" />
            </div>
            <!-- 有数据时显示图表 -->
            <canvas v-else ref="chartRef"></canvas>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { getDeviceConsumption } from '@/api/analysis';
import { generateRandomColorPairs } from '@/utils/colorUtils';
import Chart from 'chart.js/auto'

const deviceData = ref(null)
const chartRef = ref(null)
const chartInstance = ref(null)
const isLoading = ref(false)

// 获取设备能耗数据
const fetchDeviceConsumption = async () => {
    try {
        isLoading.value = true
        const res = await getDeviceConsumption('electricity')
        console.log(res)
        deviceData.value = res
    } catch (error) {
        console.error('获取设备能耗数据失败:', error)
    } finally {
        isLoading.value = false
    }
}

// 格式化图表数据（环形图适配）
const formatChartData = (data) => {
    if (!data || data.length === 0) {
        return { labels: [], datasets: [{ data: [] }] }
    }

    const dataLength = data.length
    // console.log(dataLength)
    const randomColors = generateRandomColorPairs(dataLength)
    const backgroundColor = randomColors.map(item => item.backgroundColor)
    const borderColor = randomColors.map(item => item.borderColor)

    // 计算总能耗（用于百分比计算）
    const totalConsumption = data.reduce((sum, item) => sum + item.consumption, 0)
    
    return {
        labels: data.map(item => item.device_name),
        datasets: [{
            label: '设备能耗 (kWh)',
            data: data.map(item => item.consumption),
            backgroundColor: backgroundColor,
            borderColor: borderColor,
            borderWidth: 1,
            // 存储原始数据用于tooltip
            deviceData: data.map(item => ({
                name: item.device_name,
                consumption: item.consumption,
                monthlyUsage: item.monthly_usage,
                percentage: ((item.consumption / totalConsumption) * 100).toFixed(2)
            }))
        }]
    }
}

// 初始化环形图
const initChart = () => {
    if (chartInstance.value) {
        chartInstance.value.destroy()
    }

    // 如果没有数据，不初始化图表
    if (!deviceData.value || deviceData.value.length === 0) {
        return
    }

    const ctx = chartRef.value.getContext('2d')
    const formattedData = formatChartData(deviceData.value)

    chartInstance.value = new Chart(ctx, {
        type: 'doughnut',  // 保持环形图类型
        data: formattedData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'  // 图例在右侧
                },
                title: {
                    display: false,
                    text: '设备能耗分布',
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    callbacks: {
                        // 自定义提示框，展示详细信息
                        label: function(context) {
                            const device = formattedData.datasets[0].deviceData[context.dataIndex]
                            return [
                                // `${device.name}`,
                                `月使用能耗: ${device.monthlyUsage}kWh (${device.consumption}%)`,
                                // `月使用时长: ${device.monthlyUsage}小时`
                            ]
                        }
                    }
                }
            },
            cutout: '60%'  // 环形比例
        }
    })
}

// 数据变化时更新图表
watch(
    () => deviceData.value,
    () => {
        if (chartRef.value && deviceData.value && deviceData.value.length > 0) {
            initChart()
        }
    },
    { deep: true }
)

// 组件挂载时加载数据
onMounted(async () => {
    await fetchDeviceConsumption()
    initChart()
})

// 组件卸载时销毁图表
onUnmounted(() => {
    if (chartInstance.value) {
        chartInstance.value.destroy()
    }
})
</script>

<style scoped>
.chart-container {
    height: 400px;
    width: 100%;
    position: relative;
}

.no-data-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
}
</style>