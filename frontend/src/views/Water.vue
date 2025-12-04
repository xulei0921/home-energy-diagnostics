<template>
    <el-row :gutter="20">
        <el-col :span="8">
            <el-card class="water-usage">
                <div>
                    <div class="value-type">本月用水量</div>
                    <h3 class="value-consumption">{{ waterData.current_usage }} m³</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(waterData.usage_mom_rate)" />
                        </el-icon>
                        <span>{{ waterData.usage_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="water-amount">
                <div>
                    <div class="value-type">本月水费</div>
                    <h3 class="value-consumption">￥{{ waterData.current_amount }}</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(waterData.amount_mom_rate)" />
                        </el-icon>
                        <span>{{ waterData.amount_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="water-unit-price">
                <div>
                    <div class="value-type">平均水价</div>
                    <h3 class="value-consumption">￥{{ waterData.current_unit_price }} /m³</h3>
                    <!-- <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(electricityData.amount_mom_rate)" />
                        </el-icon>
                        <span>{{ electricityData.unit_price_mom_rate }}% 环比</span>
                    </div> -->
                </div>
            </el-card>
        </el-col>
    </el-row>
    <div class="line-chart-container">
        <el-card>
            <h2>水资源消耗趋势图</h2>
            <TrendChart
                type="line"
                :data="chartData"
                :options="chartOptions"
            />
        </el-card>
    </div>
    <el-row :gutter="20">
        <el-col :span="12">
            <el-card>
                <h2>设备能耗占比</h2>
                <WaterConsumptionChart/>
            </el-card>
        </el-col>
        <el-col :span="12">
            <el-card style="height: 475px; overflow-y: auto;">
                <div class="detect-header">
                    <h2>异常用水月份检测</h2>
                    <el-button :loading="isLoadingAnomaly" @click="fetchAnomalyMonths()" style="padding: 0 10px;" type="primary">分析</el-button>
                </div>
                <div
                    class="detect-container"
                    v-loading="isLoadingAnomaly"
                    element-loading-text="分析数据量较大，请耐心等待..."
                >
                    <div v-if="anomalyMonthsData.length === 0 && !isLoadingAnomaly" class="no-data-container">
                        <el-empty description="暂无异常用水数据"></el-empty>
                    </div>
                    <el-card v-else v-for="item in anomalyMonthsData" shadow="never" :class="getDetectCardStyle(item.severity)">
                        <div class="detect-title">
                            <h4>{{ item.month }}月用水异常</h4>
                            <el-tag style="padding: 10px;" round effect="dark" :type="getDetectTagType(item.severity)">{{ getDetectTagText(item.severity) }}</el-tag>
                        </div>
                        <span>用水量达到{{ item.usage }}m³</span>
                        <span v-for="recommendation in item.recommendations">,{{ recommendation }}</span>
                    </el-card>
                </div>
            </el-card>
        </el-col>
    </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Top, Bottom, SemiSelect } from '@element-plus/icons-vue'
import { getEnergyComparison, getEnergyTrend, getAnomalyMonths } from '@/api/analysis';
import TrendChart from '@/components/charts/TrendChart.vue';
import WaterConsumptionChart from '@/components/charts/WaterConsumptionChart.vue';

const waterData = ref({})
const isLoadingAnomaly = ref(false)
const anomalyMonthsData = ref([])

const chartData = ref({
    labels: [],
    datasets: [
        {
            label: '用水量 (m³)',
            data: [],
            borderColor: 'rgb(30, 144, 255)',
            backgroundColor: 'rgba(30, 144, 255, 0.4)',
            yAxisID: 'y',
            tension: 0.3
        },
        {
            label: '水费 (元)',
            data: [],
            borderColor: 'rgb(100,149,237)',
            backgroundColor: 'rgba(100,149,237, 0.4)',
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
            text: '水资源消耗趋势'
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
                            label += context.parsed.y + ' m³'
                        } else {
                            label += context.parsed.y + ' 元'
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
                text: '用水量'
            }
        },
        y1: {
            type: 'linear',
            display: true,
            position: 'right',
            beginAtZero: true,
            title: {
                display: true,
                text: '水费'
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

const getDetectCardStyle = (severity) => {
    switch (severity) {
        case 'high':
            return 'severity-high'
        case 'medium':
            return 'severity-medium'
        case 'low':
            return 'severity-low'
    }
}

const getDetectTagType = (severity) => {
    switch (severity) {
        case 'high':
            return 'danger'
        case 'medium':
            return 'warning'
        case 'low':
            return 'primary'
    }
}

const getDetectTagText = (severity) => {
    const text_map = {
        'high': '高',
        'medium': '中',
        'low': '低'
    }
    return text_map[severity]
}

const fetchEnergyComparison = async (trend_data) => {
    try {
        const res = await getEnergyComparison(trend_data)
        waterData.value = res
        console.log(waterData.value)
    } catch (error) {
        console.error(error)
    }
}

const fetchEnergyTrendData = async () => {
    const trendData = await getEnergyTrend({
        period: 'monthly',
        bill_type: 'water'
    })

    const labels = []
    const waterUsageData = []
    const waterAmountData = []

    trendData.forEach(item => {
        const formattedDate = `${item.year}-${item.month}`
        labels.push(formattedDate)

        waterUsageData.push(item.usage)
        waterAmountData.push(item.amount)
    })

    chartData.value.labels = labels
    chartData.value.datasets[0].data = waterUsageData
    chartData.value.datasets[1].data = waterAmountData
}

const fetchAnomalyMonths = async () => {
    try {
        isLoadingAnomaly.value = true
        const res = await getAnomalyMonths('water')
        console.log(res)
        anomalyMonthsData.value = res
    } catch (error) {
        console.error(error)
    } finally {
        isLoadingAnomaly.value = false
    }
}

onMounted(() => {
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

.water-usage {
    height: 160px;
    background-color: rgb(30, 144, 255);
    border-radius: 15px;
}

.water-amount {
    height: 160px;
    background-color: rgb(100,149,237);
    border-radius: 15px;
}

.water-unit-price {
    height: 160px;
    background-color: rgb(135,206,250);
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

.detect-header {
    display: flex;
    justify-content: space-between;
}

.detect-container {
    margin-top: 20px;
    min-height: 350px;
}

.detect-title {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.no-data-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 363px;
}

.severity-high {

    background-color: #FEF2F2;
    border: 1px solid #FECACA;
}

.severity-medium {
    background-color: #FEFCE8;
    border: 1px solid #FEF08A;
}

.severity-low {
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
}
</style>