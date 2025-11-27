<template>
    <el-row :gutter="20">
        <el-col :span="8">
            <el-card class="electricity-usage">
                <div>
                    <div class="value-type">本月用电量</div>
                    <h3 class="value-consumption">{{ electricityData.current_usage }} Kwh</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(electricityData.usage_mom_rate)" />
                        </el-icon>
                        <span>{{ electricityData.usage_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="electricity-amount">
                <div>
                    <div class="value-type">本月电费</div>
                    <h3 class="value-consumption">￥{{ electricityData.current_amount }}</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(electricityData.amount_mom_rate)" />
                        </el-icon>
                        <span>{{ electricityData.amount_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="electricity-unit-price">
                <div>
                    <div class="value-type">平均电费</div>
                    <h3 class="value-consumption">￥{{ electricityData.current_unit_price }} /Kwh</h3>
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
            <h2>电力消耗趋势图</h2>
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
                <ElectricityConsumptionChart/>
            </el-card>
        </el-col>
        <el-col :span="12"></el-col>
    </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Top, Bottom, SemiSelect } from '@element-plus/icons-vue'
import { getEnergyComparison, getEnergyTrend } from '@/api/analysis';
import TrendChart from '@/components/charts/TrendChart.vue';
import ElectricityConsumptionChart from '@/components/charts/ElectricityConsumptionChart.vue';

const electricityData = ref({})

const chartData = ref({
    labels: [],
    datasets: [
        {
            label: '用电量 (Kwh)',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.4)',
            yAxisID: 'y',
            tension: 0.3
        },
        {
            label: '电费 (元)',
            data: [],
            borderColor: 'rgb(135,206,250)',
            backgroundColor: 'rgba(135,206,250, 0.4)',
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
            text: '电力消耗趋势'
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
                text: '电费'
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

const fetchEnergyComparison = async (trend_data) => {
    try {
        const res = await getEnergyComparison(trend_data)
        electricityData.value = res
        // console.log(electricityData.value)
    } catch (error) {
        console.error(error)
    }
}

const fetchEnergyTrendData = async () => {
    const trendData = await getEnergyTrend({
        period: 'monthly',
        bill_type: 'electricity'
    })

    // 处理数据，将其转换为 Chart.js 所需格式
    const labels = []
    const elecUsageData = []
    const elecAmountData = []

    trendData.forEach(item => {
        // 格式化 X 轴标签
        const formattedDate = `${item.year}-${item.month.padStart(2, '0')}`
        labels.push(formattedDate)

        elecUsageData.push(item.usage)
        elecAmountData.push(item.amount)
    })

    chartData.value.labels = labels
    chartData.value.datasets[0].data = elecUsageData
    chartData.value.datasets[1].data = elecAmountData
}

onMounted(() => {
    fetchEnergyComparison({
        period: 'monthly',
        bill_type: 'electricity'
    })

    fetchEnergyTrendData()
})
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

.electricity-usage {
    height: 160px;
    background-color: rgba(75, 192, 192, 1);
    border-radius: 15px;
}

.electricity-amount {
    height: 160px;
    background-color: rgba(135,206,250, 1);
    border-radius: 15px;
}

.electricity-unit-price {
    height: 160px;
    background-color: rgba(64,224,208, 1);
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

</style>