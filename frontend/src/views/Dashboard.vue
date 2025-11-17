<template>
    <el-row :gutter="20">
        <el-col :span="8">
            <el-card class="electricity-card">
                <div>
                    <div class="value-type">电力消耗</div>
                    <h3 class="value-consumption">{{ elec_consumption.current_usage }}Kwh</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(elec_consumption.usage_mom_rate)" />
                        </el-icon>
                        <span>{{ elec_consumption.usage_mom_rate }}% 同比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="gas-card">
                <div>
                    <div class="value-type">燃气消耗</div>
                    <h3 class="value-consumption">{{ gas_consumption.current_usage }}m³</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(gas_consumption.usage_mom_rate)" />
                        </el-icon>
                        <span>{{ gas_consumption.usage_mom_rate }}% 同比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="water-card">
                <div>
                    <div class="value-type">水资源消耗</div>
                    <h3 class="value-consumption">{{ water_consumption.current_usage }}m³</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(water_consumption.usage_mom_rate)" />
                        </el-icon>
                        <span>{{ water_consumption.usage_mom_rate }}% 同比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
    </el-row>
    <div class="chart-container">
        <el-card>
        <h2>能耗趋势图</h2>
        <TrendChart
            type="line"
            :data="chartData"
            :options="chartOptions"
        />
        </el-card>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import TrendChart from '@/components/charts/TrendChart.vue';
import { CaretTop, CaretBottom, Minus, SemiSelect, Top, Bottom } from '@element-plus/icons-vue'
import { getEnergyComparison, getEnergyTrend } from '@/api/analysis';

// 定义响应式数据，用于存储图表配置
const chartData = ref({
    labels: [],  // X 轴标签
    datasets: [
        {
            label: '用电量 (Kwh)',
            data: [],  // 用电量数据
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.4)',
            yAxisID: 'y',  // 关联到'y'轴
            tension: 0.3
        },
        {
            label: '用气量 (m³)',
            data: [],  // 用气量数据
            borderColor: 'rgb(255, 127, 80)',
            backgroundColor: 'rgba(255, 127, 80, 0.4)',
            yAxisID: 'y1',
            tension: 0.3
        },
        {
            label: '用水量 (m³)',
            data: [],  // 用水量数据
            borderColor: 'rgb(30, 144, 255)',
            backgroundColor: 'rgba(30, 144, 255, 0.4)',
            yAxisID: 'y1',
            tension: 0.3
        }
    ]
})

// 定义图表选项
const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        mode: 'index',  // 鼠标悬浮时，同时显示多个数据集的数据
        intersect: false
    },
    plugins: {
        title: {
            display: false,
            text: '能源消耗趋势'
        },
        tooltip: {
            callbacks: {
                // 自定义提示框内容
                label: function(context) {
                    let label = context.dataset.label || ''
                    if (label) {
                        label += ': '
                    }
                    if (context.parsed.y !== null) {
                        // 根据数据集格式化数据
                        if (context.datasetIndex === 0) {
                            label += context.parsed.y + ' Kwh'
                        } else {
                            label += context.parsed.y + ' m³'
                        }
                    }
                    return label
                }
            }
        }
    },
    scales: {
        y: {
            type: 'linear',
            display: true,
            position: 'left',
            beginAtZero: true,
            title: {
                display: true,
                text: '用电量'
            }
        },
        y1: {
            type: 'linear',
            display: true,
            position: 'right',
            beginAtZero: true,
            title: {
                display: true,
                text: '燃气/水用量'
            },
            grid: {
                drawOnChartArea: false
            }
        },
        x: {
            title: {
                display: true,
                text: '日期'
            },
            grid: {
                display: true
            }
        }
    }
})

const fetchEnergyTrendData = async () => {
    const electricityData = await getEnergyTrend({
        period: 'monthly',
        bill_type: 'electricity'
    })

    const gasData = await getEnergyTrend({
        period: 'monthly',
        bill_type: 'gas'
    })

    const waterData = await getEnergyTrend({
        period: 'monthly',
        bill_type: 'water'
    })

    // 处理数据，将其转换为 Chart.js 所需格式
    const labels = []
    const elecUsageData = []
    const gasUsageData = []
    const waterUsageData = []

    electricityData.forEach(item => {
        // 格式化 X 轴标签，例如 "2025-01"
        const formattedDate = `${item.year}-${item.month.padStart(2, '0')}`
        labels.push(formattedDate)

        elecUsageData.push(item.usage)
    })

    gasData.forEach(item => {
        gasUsageData.push(item.usage)
    })

    waterData.forEach(item => {
        waterUsageData.push(item.usage)
    })

    // 更新响应式的 chartData
    chartData.value.labels = labels
    chartData.value.datasets[0].data = elecUsageData
    chartData.value.datasets[1].data = gasUsageData
    chartData.value.datasets[2].data = waterUsageData
}

const elec_consumption = ref({
    current_usage: 0,
    usage_mom_rate: 0
})

const gas_consumption = ref({
    current_usage: 0,
    usage_mom_rate: 0
})

const water_consumption = ref({
    current_usage: 0,
    usage_mom_rate: 0
})

// 计算趋势图标
const trendIcon = (rate) => {
    if (rate > 0) {
        return Top
    } else if (rate < 0){
        return Bottom
    } else if (rate === 0) {
        return SemiSelect
    }
}

const fetchEnergyComparison = async (trend_data) => {
    try {
        const res = await getEnergyComparison(trend_data)
        // console.log(res)
        if (trend_data.bill_type === 'electricity') {
            elec_consumption.value.current_usage = res.current_usage
            elec_consumption.value.usage_mom_rate = res.usage_mom_rate || 0
        } else if (trend_data.bill_type === 'gas') {
            gas_consumption.value.current_usage = res.current_usage
            gas_consumption.value.usage_mom_rate = res.usage_mom_rate || 0
        } else if (trend_data.bill_type === 'water') {
            water_consumption.value.current_usage = res.current_usage
            water_consumption.value.usage_mom_rate = res.usage_mom_rate || 0
        }
    } catch (error) {
        console.error(error)
    }
}

onMounted(() => {
    fetchEnergyComparison({
        period: 'monthly',
        bill_type: 'electricity'
    })

    fetchEnergyComparison({
        period: 'monthly',
        bill_type: 'gas'
    })

    fetchEnergyComparison({
        period: 'monthly',
        bill_type: 'water'
    })

    fetchEnergyTrendData()
})

</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

.electricity-card {
    height: 160px;
    background-color: rgba(59, 130, 246, 1);
    border-radius: 15px;
}

.gas-card {
    height: 160px;
    background-color: #F36812;
    border-radius: 15px;
}

.water-card {
    height: 160px;
    background: #5096F9;
    border-radius: 15px;
}

.value-type {
    font-size: 16px;
    color: #d7e3f5;
}

.value-consumption {
    font-size: 25px;
    color: #fff;
    margin: 5px 0;
}

.value-trend {
    font-size: 16px;
    color: #fff;
}

.chart-container {
    margin-top: 20px;
}
</style>