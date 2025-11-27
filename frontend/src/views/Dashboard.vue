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
                        <span>{{ elec_consumption.usage_mom_rate }}% 环比</span>
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
                        <span>{{ gas_consumption.usage_mom_rate }}% 环比</span>
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
                        <span>{{ water_consumption.usage_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
    </el-row>
    <div class="line-chart-container">
        <el-card>
        <h2>能耗趋势图</h2>
        <TrendChart
            type="line"
            :data="chartData"
            :options="chartOptions"
        />
        </el-card>
    </div>
    <el-row :gutter="20">
        <el-col :span="8">
            <el-card>
                <h2>能源费用分布</h2>
                <DistributionChart/>
                <div class="cost-detail" v-for="item in costsDistribution">
                    <div class="icon-text">
                        <span :class="getIconClass(item.bill_type)"></span>
                        <span>{{ getBillTypeText(item.bill_type) }}</span>
                    </div>
                    <div class="cost-amount">
                        <span>￥{{ item.amount }} ({{ item.percentage }}%)</span>
                        <span></span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="16">
            <el-card>
                <EnergySuggestions />
            </el-card>
        </el-col>
    </el-row>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import TrendChart from '@/components/charts/TrendChart.vue';
import DistributionChart from '@/components/charts/DistributionChart.vue';
import EnergySuggestions from '@/components/EnergySuggestions.vue';
import { CaretTop, CaretBottom, Minus, SemiSelect, Top, Bottom } from '@element-plus/icons-vue'
import { getEnergyComparison, getEnergyTrend, getEnergyCostsDistribution } from '@/api/analysis';

const costsDistribution = ref({})

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

const getBillTypeText = (billType) => {
    switch(billType) {
        case 'electricity':
            return '电费'
        case 'gas':
            return '燃气费'
        case 'water':
            return '水费'
        default:
            return '未知费用'
    }
}

const getIconClass = (billType) => {
    switch (billType) {
        case 'electricity':
            return 'radius-electricity'
        case 'gas':
            return 'radius-gas'
        case 'water':
            return 'radius-water'
    }
}

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

const fetchEnergyCostsDistribution = async () => {
    try {
        const res = await getEnergyCostsDistribution()
        console.log(res)
        costsDistribution.value = res.items
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
    fetchEnergyCostsDistribution()
})

</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

.electricity-card {
    height: 160px;
    background-color: rgba(75, 192, 192, 1);
    border-radius: 15px;
}

.gas-card {
    height: 160px;
    background-color: #F36812;
    border-radius: 15px;
}

.water-card {
    height: 160px;
    background: rgb(30, 144, 255);
    border-radius: 15px;
}

.value-type {
    font-size: 16px;
    color: #f0f1f4;
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

.line-chart-container {
    margin: 20px 0;
}

.cost-detail {
    display: flex;
    justify-content: space-between;
}

.icon-text {
    display: flex;
    align-items: center;
    margin: 3px 0;
}

.radius-electricity {
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 8px;
    background-color: rgb(75, 192, 192);
    margin-right: 5px;
}

.radius-gas {
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 8px;
    background-color: rgb(243, 104, 18);
    margin-right: 5px;
}

.radius-water {
    display: inline-block;
    width: 16px;
    height: 16px;
    border-radius: 8px;
    background-color: rgb(30, 144, 255);
    margin-right: 5px;
}
</style>