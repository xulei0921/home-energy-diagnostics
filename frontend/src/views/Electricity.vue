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
        <el-col :span="12">
            <el-card style="height: 475px; overflow-y: auto;" >
                <div class="detect-header">
                    <h2>异常用电月份检测</h2>
                    <el-button :loading="isLoadingAnomaly" @click="fetchAnomalyMonths()" style="padding: 0 10px;" type="primary">分析</el-button>
                </div>
                <div
                    class="detect-container"
                    v-loading="isLoadingAnomaly"
                    element-loading-text="分析数据量较大，请耐心等待..."
                >
                    <div v-if="anomalyMonthsData.length === 0 && !isLoadingAnomaly" class="no-data-container">
                        <el-empty description="暂无异常用电数据"></el-empty>
                    </div>
                    <el-card v-else v-for="item in anomalyMonthsData" shadow="never" :class="getDetectCardStyle(item.severity)">
                        <div class="detect-title">
                            <h4>{{ item.year }}年{{ item.month }}月用电异常</h4>
                            <el-tag style="padding: 10px;" round effect="dark" :type="getDetectTagType(item.severity)">{{ getDetectTagText(item.severity) }}</el-tag>
                        </div>
                        <span>用电量达到{{ item.usage }}kWh</span>
                        <span v-for= "recommendation in item.recommendations">,{{ recommendation }}</span>
                    </el-card>
                </div>
            </el-card>
        </el-col>
    </el-row>
    <div class="electricity-suggestion">
        <el-card style="height: 500px; overflow-y: auto;">
            <el-tabs>
                <el-tab-pane label="分析与生成最新建议">
                    <div class="suggestion-header">
                        <h2>用电分析与节能建议</h2>
                        <el-button
                            type="primary"
                            :icon="Refresh"
                            style="padding: 0 15px;"
                            v-loading="isLoadingSuggestion"
                            @click="fetchEnhancedEnergyAnalysis"
                        >
                            更新建议
                        </el-button>
                    </div>
                    <div
                        class="suggestion-container"
                        v-loading="isLoadingSuggestion"
                        element-loading-text="分析数据量较大，请耐心等待..."
                    >
                        <div v-if="isEmptyObject(suggestionData)" class="no-data-container">
                            <el-empty description="暂无节能建议"></el-empty>
                        </div>
                        <div v-else>
                            <el-card style="margin-top: 10px;">
                                <h3>整体用电分析</h3>
                                <div class="overview-grid">
                                    <!-- 整体评估 -->
                                    <div class="overview-item">
                                        <el-tag type="primary" size="large" class="item-label">整体评估</el-tag>
                                        <p class="item-content">{{ suggestionData.overall_assessment }}</p>
                                    </div>

                                    <!-- 风险等级 -->
                                    <div class="overview-item">
                                        <el-tag type="warning" size="large" class="item-label">风险等级</el-tag>
                                        <el-badge
                                            :type="riskLevelType(suggestionData.risk_level)"
                                            :value="riskLevelText(suggestionData.risk_level)"
                                            class="risk-badge"
                                        ></el-badge>
                                    </div>

                                    <!-- 优化潜力 -->
                                    <div class="overview-item">
                                        <el-tag
                                            type="success"
                                            size="large"
                                            class="item-label"
                                        >优化潜力</el-tag>
                                        <el-progress
                                            :percentage="optimizationPotentialPercent(suggestionData.optimization_potential)"
                                            :status="optimizationStatus(suggestionData.optimization_potential)"
                                            text-inside
                                            stroke-width="20"
                                        ></el-progress>
                                    </div>

                                    <!-- 季节分析 -->
                                    <div class="overview-item">
                                        <el-tag
                                            type="info"
                                            size="large"
                                            class="item-label"
                                        >季节因素分析</el-tag>
                                        <p class="item-content">{{ suggestionData.seasonal_analysis }}</p>
                                    </div>

                                    <!-- 关键洞察 -->
                                    <div class="key-insights">
                                        <el-collapse>
                                            <el-collapse-item title="关键洞察">
                                                <div v-for="insight in suggestionData.key_insights" class="insight-item">
                                                     <el-icon class="insight-icon"><Search /></el-icon>
                                                    <span>{{ insight }}</span>
                                                </div>
                                            </el-collapse-item>
                                        </el-collapse>
                                    </div>
                                </div>
                            </el-card>
                            <el-card class="suggestion-card">
                                <h3>最新节能建议</h3>
                                <div :class="getSuggestionStyle(suggestion.impact_rating)" v-for="suggestion in suggestionData.suggestions">
                                    <div class="suggestion-header">
                                        <div class="suggestion-title">
                                            {{ suggestion.suggestion_title }}
                                        </div>
                                        <div class="rating-and-date">
                                            <span class="suggestion-rating">
                                                影响等级: 
                                                <el-rate
                                                    v-model="suggestion.impact_rating"
                                                    disabled
                                                    :icons="icons"
                                                    :void-icon="Warning"
                                                    :colors="['#67c23a', '#FF9900', '#FF0000']"
                                                ></el-rate>
                                            </span>
                                            <span class="suggestion-date">目标账单日期:{{ suggestion.suggestion_date.slice(0, 7) }}</span>
                                        </div>
                                    </div>
                                    <div class="suggestion-content">
                                        {{ suggestion.suggestion_text }}
                                    </div>
                                </div>
                            </el-card>
                        </div>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="所有历史建议"></el-tab-pane>
            </el-tabs>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useElectricityStore } from '@/stores/electricity';
import { useUserStore } from '@/stores';
import { Top, Bottom, SemiSelect, Refresh, Search, Warning, ChatDotRound, ChatLineRound, ChatRound } from '@element-plus/icons-vue'
import { getEnergyComparison, getEnergyTrend, getAnomalyMonths, getEnhancedEnergyAnalysis } from '@/api/analysis';
import { getCurrentUser } from '@/api/user'; 
import TrendChart from '@/components/charts/TrendChart.vue';
import ElectricityConsumptionChart from '@/components/charts/ElectricityConsumptionChart.vue';
import { storeToRefs } from 'pinia';

const icons = [Warning, Warning, Warning]

const electricityStore = useElectricityStore()

const {
    elecSuggestionData,
    elecAnomalyMonthsData,
    userId
} = storeToRefs(electricityStore)

const {
    setElecSuggestionData,
    setElecAnomalyMonthsData,
    setUserId
} = electricityStore

const userStore = useUserStore()

const {
    currentUserId
} = storeToRefs(userStore)

const electricityData = ref({})
const anomalyMonthsData = ref([])
const suggestionData = ref({})
const isLoadingAnomaly = ref(false)
const isLoadingSuggestion = ref(false)

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

const getSuggestionStyle = (impact_rating) => {
    switch (impact_rating) {
        case 5:
            return 'suggestion-item-high'
        case 3:
            return 'suggestion-item-medium'
        case 1:
            return 'suggestion-item-low'
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

const riskLevelType = (risk_level) => {
    const risk_type_map = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'success'
    }
    return risk_type_map[risk_level]
}

const riskLevelText = (risk_level) => {
    const risk_text_map = {
        'high': '高',
        'medium': '中',
        'low': '低'
    }
    return risk_text_map[risk_level]
}

const optimizationPotentialPercent = (optimization_potential) => {
    const potential_map = {
        'high': 90,
        'medium': 60,
        'low': 30
    }
    return potential_map[optimization_potential]
}

const optimizationStatus = (optimization_potential) => {
    return optimization_potential === 'high' ? 'success' : 'processing'
}

const isEmptyObject = (obj) => {
    if (typeof obj !== 'object' || obj === null || Array.isArray(obj)) {
        return true
    }
    return Object.keys(obj).length === 0
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

const fetchAnomalyMonths = async () => {
    try {
        isLoadingAnomaly.value = true
        const res = await getAnomalyMonths('electricity')
        const userData = await getCurrentUser()
        console.log(res)
        anomalyMonthsData.value = res
        setElecAnomalyMonthsData(res)
        setUserId(userData.id)
    } catch (error) {
        console.error(error)
    } finally {
        isLoadingAnomaly.value = false
    }
}

const fetchEnhancedEnergyAnalysis = async () => {
    try {
        isLoadingSuggestion.value = true
        const res = await getEnhancedEnergyAnalysis('electricity', 'monthly')
        const userData = await getCurrentUser()
        console.log(res)
        suggestionData.value = res.ai_analysis
        setElecSuggestionData(res.ai_analysis)
        setUserId(userData.id)
    } catch (error) {
        console.error(error)
    } finally {
        isLoadingSuggestion.value = false
    }
}

onMounted(() => {
    fetchEnergyComparison({
        period: 'monthly',
        bill_type: 'electricity'
    })

    fetchEnergyTrendData()
    // fetchAnomalyMonths()
    if (currentUserId.value === userId.value){
        anomalyMonthsData.value = elecAnomalyMonthsData.value
        suggestionData.value = elecSuggestionData.value
    }
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

.detect-container {
    margin-top: 20px;
    min-height: 350px;
}

.no-data-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 363px;
}

.detect-title {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}

.detect-header {
    display: flex;
    justify-content: space-between;
}

.severity-high {
    margin-bottom: 20px;
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
}

.severity-medium {
    margin-bottom: 20px;
    background-color: #FEFCE8;
    border: 1px solid #FEF08A;
}

.severity-low {
    margin-bottom: 20px;
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
}

.electricity-suggestion {
    margin-top: 20px;
}

.suggestion-header {
    display: flex;
    justify-content: space-between;
    /* align-items: center; */
}

.overview-item {
    padding: 16px;
    border-bottom: 1px solid #EBEEF5;
}

.item-label {
    margin-bottom: 8px;
    margin-right: 8px;
    font-size: 17px;
}

:deep(.el-tag) {
    padding: 10px;
}

.risk-badge {
    padding: 4px;
    font-size: 16px;
}

.key-insights {
    padding-left: 16px;
}

:deep(.el-collapse-item__header) {
    font-size: 17px;
}

.insight-item {
    margin-bottom: 10px;
    font-size: 16px;
    border-bottom: 1px solid #ced1d9;
}

.insight-icon {
    color: #409eff;
    margin-right: 8px;
}

.suggestion-card {
    margin-top: 20px;
}

.suggestion-item {
    margin-top: 10px;
    margin-bottom: 20px;
    border: 1px solid #c4c7cd;
    border-radius: 5px;
    padding: 10px;
}

.suggestion-item-high {
    margin-top: 10px;
    margin-bottom: 20px;
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 5px;
    padding: 10px;
}

.suggestion-item-medium {
    margin-top: 10px;
    margin-bottom: 20px;
    background-color: #FEFCE8;
    border: 1px solid #FEF08A;
    border-radius: 5px;
    padding: 10px;
}

.suggestion-item-low {
    margin-top: 10px;
    margin-bottom: 20px;
    background-color: #C8E6C9;
    border: 1px solid #a8c7a9;
    border-radius: 5px;
    padding: 10px;
}

.suggestion-content {
    margin-top: 8px;
}

.suggestion-title {
    font-style: 18px;
    font-weight: bold;
}

.suggestion-rating {
    margin-right: 20px;
}
</style>