<template>
    <el-row :gutter="20">
        <el-col :span="8">
            <el-card class="gas-usage">
                <div>
                    <div class="value-type">本月用气量</div>
                    <h3 class="value-consumption">{{ gasData.current_usage }} m³</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(gasData.usage_mom_rate)" />
                        </el-icon>
                        <span>{{ gasData.usage_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="gas-amount">
                <div>
                    <div class="value-type">本月燃气费</div>
                    <h3 class="value-consumption">￥{{ gasData.current_amount }}</h3>
                    <div class="value-trend">
                        <el-icon>
                            <component :is="trendIcon(gasData.amount_mom_rate)" />
                        </el-icon>
                        <span>{{ gasData.amount_mom_rate }}% 环比</span>
                    </div>
                </div>
            </el-card>
        </el-col>
        <el-col :span="8">
            <el-card class="gas-unit-price">
                <div>
                    <div class="value-type">平均气价</div>
                    <h3 class="value-consumption">￥{{ gasData.current_unit_price }} /m³</h3>
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
            <h2>燃气消耗趋势图</h2>
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
                <GasConsumptionChart/>
            </el-card>
        </el-col>
        <el-col :span="12">
            <el-card style="height: 475px; overflow-y: auto;">
                <div class="detect-header">
                    <h2>异常用气月份检测</h2>
                    <el-button :loading="isLoadingAnomaly" @click="fetchAnomalyMonths()" style="padding: 0 10px;" type="primary">分析</el-button>
                </div>
                <div
                    class="detect-container"
                    v-loading="isLoadingAnomaly"
                    element-loading-text="分析数据量较大，请耐心等待..."
                >
                    <div v-if="anomalyMonthsData.length === 0 && !isLoadingAnomaly" class="no-data-container">
                        <el-empty description="暂无异常用气数据"></el-empty>
                    </div>
                    <el-card v-else v-for="item in anomalyMonthsData" shadow="never" :class="getDetectCardStyle(item.severity)">
                        <div class="detect-title">
                            <h4>{{ item.month }}月用气异常</h4>
                            <el-tag style="padding: 10px;" round effect="dark" :type="getDetectTagType(item.severity)">{{ getDetectTagText(item.severity) }}</el-tag>
                        </div>
                        <span>用气量达到{{ item.usage }}m³</span>
                        <span v-for= "recommendation in item.recommendations">,{{ recommendation }}</span>
                    </el-card>
                </div>
            </el-card>
        </el-col>
    </el-row>

    <div class="gas-suggestion">
        <el-card style="height: 500px; overflow-y: auto;">
            <el-tabs>
                <el-tab-pane label="分析与生成最新建议">
                    <div class="suggestion-header">
                        <h2>用气分析与节能建议</h2>
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
                                <h3>整体用气分析</h3>
                                <div class="overview-grid">
                                    <!-- 整体评估 -->
                                    <div class="overview-item">
                                        <el-tag type="primary" size="large" class="item-label">整体评估</el-tag>
                                        <p v-if="suggestionData?.overall_assessment" class="item-content">{{ suggestionData.overall_assessment }}</p>
                                        <p v-else class="item-content">暂无整体评估</p>
                                    </div>

                                    <!-- 风险等级 -->
                                    <div class="overview-item">
                                        <el-tag type="warning" size="large" class="item-label">风险等级</el-tag>
                                        <el-badge
                                            v-if="suggestionData?.risk_level"
                                            :type="riskLevelType(suggestionData.risk_level)"
                                            :value="riskLevelText(suggestionData.risk_level)"
                                            class="risk-badge"
                                        ></el-badge>
                                        <p v-else class="item-content">暂无风险等级</p>
                                    </div>

                                    <!-- 优化潜力 -->
                                    <div class="overview-item">
                                        <el-tag
                                            type="success"
                                            size="large"
                                            class="item-label"
                                        >优化潜力</el-tag>
                                        <el-progress
                                            v-if="suggestionData?.optimization_potential"
                                            :percentage="optimizationPotentialPercent(suggestionData.optimization_potential)"
                                            :status="optimizationStatus(suggestionData.optimization_potential)"
                                            text-inside
                                            stroke-width="20"
                                        ></el-progress>
                                        <p v-else class="item-content">暂无优化潜力</p>
                                    </div>

                                    <!-- 季节分析 -->
                                    <div class="overview-item">
                                        <el-tag
                                            type="info"
                                            size="large"
                                            class="item-label"
                                        >季节因素分析</el-tag>
                                        <p v-if="suggestionData?.seasonal_analysis" class="item-content">{{ suggestionData.seasonal_analysis }}</p>
                                        <p v-else class="item-content">暂无季节因素分析</p>
                                    </div>

                                    <!-- 关键洞察 -->
                                    <div class="key-insights">
                                        <el-collapse>
                                            <el-collapse-item title="关键洞察">
                                                <div v-if="suggestionData?.key_insights && suggestionData?.key_insights.length !== 0" v-for="insight in suggestionData.key_insights" class="insight-item">
                                                    <el-icon class="insight-icon"><Warning /></el-icon>
                                                    <span>{{ insight }}</span>
                                                </div>
                                                <div v-else>
                                                    <el-icon class="insight-icon"><Hide /></el-icon>
                                                    <span>暂无关键洞察</span>
                                                </div>
                                            </el-collapse-item>
                                        </el-collapse>
                                    </div>
                                </div>
                            </el-card>
                            <el-card class="suggestion-card">
                                <h3>最新节能建议</h3>
                                <div :class="getSuggestionStyle(suggestion.impact_rating)" v-if="suggestionData?.suggestions && suggestionData?.suggestions.length !== 0" v-for="suggestion in suggestionData.suggestions">
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
                                <div v-else class="no-data-container">
                                    <el-empty description="暂无最新节能建议"></el-empty>
                                </div>
                            </el-card>
                        </div>
                    </div>
                </el-tab-pane>
                <el-tab-pane label="所有历史建议">
                    <el-form
                        ref="form"
                        :model="filterForm"
                    >
                        <el-row :gutter="25">
                            <el-col :span="7">
                                <el-form-item label="目标账单日期">
                                    <el-date-picker
                                        type="month"
                                        v-model="filterForm.suggestion_date"
                                        value-format="YYYY-MM-DD"
                                        placeholder="请选择日期"
                                    ></el-date-picker>
                                </el-form-item>
                            </el-col>
                            <el-col :span="7">
                                <el-form-item label="影响程度">
                                    <el-select
                                        v-model="filterForm.impact_rating"
                                        clearable
                                    >   
                                        <el-option label="低" :value="1"></el-option>
                                        <el-option label="中" :value="3"></el-option>
                                        <el-option label="高" :value="5"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-col>
                            <el-col :span="7">
                                <el-form-item label="是否实施">
                                    <el-select
                                        v-model="filterForm.is_implemented"
                                        clearable
                                    >
                                        <el-option label="是" :value="1"></el-option>
                                        <el-option label="否" :value="0"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-col>
                            <el-col :span="3">
                                <el-form-item>
                                    <el-button
                                        style="padding: 10px 13px;"
                                        type="info"
                                        plain
                                        @click="handleReset"
                                        v-loading="isLoadingSuggestionList"
                                    >重置</el-button>
                                    <el-button
                                        style="padding: 10px 13px;"
                                        type="primary"
                                        @click="handleSearch"
                                        v-loading="isLoadingSuggestionList"
                                    >搜索</el-button>
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </el-form>

                    <el-table
                        style="margin-top: 20px;"
                        v-loading="isLoadingSuggestionList"
                        :data="tableData"
                    >
                        <el-table-column label="目标账单日期">
                            <template #default="scope">
                                <span>{{ formatMonth(scope.row.suggestion_date) }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="suggestion_title" label="建议标题"></el-table-column>
                        <el-table-column prop="suggestion_text" label="建议内容" header-align="center"></el-table-column>
                        <el-table-column label="影响程度" align="center">
                            <template #default="scope">
                                <!-- 动态渲染影响程度 -->
                                <span>
                                    {{ getImpactRatingText(scope.row.impact_rating) }}
                                </span>
                            </template>
                        </el-table-column>
                        <el-table-column label="是否实施" align="center">
                            <template #default="scope">
                                <span>{{ getImplementedText(scope.row.is_implemented) }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" align="center">
                            <template #default="scope">
                                <el-switch
                                    style="margin-right: 20px;"
                                    v-model="scope.row.is_implemented"
                                    inline-prompt
                                    active-text="已实施"
                                    inactive-text="未实施"
                                    @change="handleChange(scope.row)"
                                ></el-switch>
                                <el-button
                                    type="danger"
                                    text
                                    :icon="Delete"
                                    @click="handleDelete(scope.row.id)"
                                >删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <div class="table-pagination">
                        <el-pagination
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="totalCount"
                            v-model:current-page="filterForm.page"
                            v-model:page-size="filterForm.page_size"
                            :page-sizes="[5, 10, 20, 30]"
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                        ></el-pagination>
                    </div>
                </el-tab-pane>
            </el-tabs>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Top, Bottom, SemiSelect, Warning, Hide } from '@element-plus/icons-vue'
import { getEnergyComparison, getEnergyTrend, getAnomalyMonths, getEnhancedEnergyAnalysis } from '@/api/analysis';
import { getCurrentUser } from '@/api/user';
import { getSuggestion, updateSuggestion, deleteSuggestion } from '@/api/suggestion';
import TrendChart from '@/components/charts/TrendChart.vue';
import GasConsumptionChart from '@/components/charts/GasConsumptionChart.vue';
import { useGasStore } from '@/stores/gas';
import { useUserStore } from '@/stores';
import { storeToRefs } from 'pinia';

const gasStore = useGasStore()

const {
    gasSuggestionData,
    gasAnomalyMonthsData,
    userId
} = storeToRefs(gasStore)

const {
    setGasSuggestionData,
    setGasAnomalyMonthsData,
    setUserId
} = gasStore

const userStore = useUserStore()

const {
    currentUserId
} = storeToRefs(userStore)

const gasData = ref({})
const isLoadingAnomaly = ref(false)
const isLoadingSuggestion = ref(false)
const isLoadingSuggestionList = ref(false)
const anomalyMonthsData = ref([])
const suggestionData = ref({})
const tableData = ref([])
const totalCount = ref(0)

const filterForm = ref({
    bill_type: 'gas',
    suggestion_date: null,
    impact_rating: null,
    is_implemented: null,
    page: 1,
    page_size: 5
})

const updateForm = ref({
    bill_type: 'gas',
    suggestion_title: null,
    suggestion_text: null,
    suggestion_date: null,
    impact_rating: null,
    is_implemented: null
})

const chartData = ref({
    labels: [],
    datasets: [
        {
            label: '用气量 (m³)',
            data: [],
            borderColor: 'rgb(243,104,18)',
            backgroundColor: 'rgba(243,104,18, 0.4)',
            yAxisID: 'y',
            tension: 0.3
        },
        {
            label: '燃气费 (元)',
            data: [],
            borderColor: 'rgb(255,99,71)',
            backgroundColor: 'rgba(255,99,71, 0.4)',
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
            text: '燃气消耗趋势'
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
                text: '用气量'
            }
        },
        y1: {
            type: 'linear',
            display: true,
            position: 'right',
            beginAtZero: true,
            title: {
                display: true,
                text: '燃气费'
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

const getImpactRatingText = (impact_rating) => {
    const impact_map = {
        5: '高',
        3: '中',
        1: '低' 
    }
    return impact_map[impact_rating]
}

const getImplementedText = (is_implemented) => {
    const implemented_map = {
        false: '否',
        true: '是'
    }
    return implemented_map[is_implemented]
}

const formatMonth = (dateString) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    return `${year}-${month}`
}

const isEmptyObject = (obj) => {
    if (typeof obj !== 'object' || obj === null || Array.isArray(obj)) {
        return true
    }
    return Object.keys(obj).length === 0
}

// 当分页器页面大小发生改变时
const handleSizeChange = () => {
    filterForm.value.page = 1
    fetchSuggestion(filterForm.value)
}

// 当分页器页码发生改变时
const handleCurrentChange = () => {
    fetchSuggestion(filterForm.value)
}

const handleSearch = () => {
    fetchSuggestion(filterForm.value)
}

const handleReset = () => {
    filterForm.value = {
        bill_type: 'gas',
        suggestion_date: null,
        impact_rating: null,
        is_implemented: null,
        page: 1,
        page_size: 5
    }
    fetchSuggestion(filterForm.value)
}

const handleChange = async (row) => {
    try {
        // console.log(row)
        updateForm.value = {
            bill_type: row.bill_type,
            suggestion_title: row.suggestion_title,
            suggestion_text: row.suggestion_text,
            suggestion_date: row.suggestion_date,
            impact_rating: row.impact_rating,
            is_implemented: row.is_implemented
        }
        // 弹出确认对话框
        await ElMessageBox.confirm(
            `确定要将「${row.suggestion_title}」的状态修改为「${row.is_implemented ? '已实施' : '未实施'}」吗?`,
            '状态修改确认',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )
        await updateSuggestion(row.id, updateForm.value)
        ElMessage.success(`状态已成功修改为:${row.is_implemented ? '已实施' : '未实施'}`)

        fetchSuggestion(filterForm.value)
    } catch (error) {
        // 如果用户点击了“取消”，则会进入这里
        // ElMessageBox.confirm 会在用户取消时抛出一个错误，错误信息为 'cancel'
        if (error === 'cancel') {
            row.is_implemented = !row.is_implemented
            ElMessage.info('已取消修改')
        } else {
            ElMessage.error('修改失败', error)
            console.error('建议状态修改失败，请稍后重试')
        }
    }
}

const handleDelete = async (suggestion_id) => {
    try {
        await ElMessageBox.confirm(
            `此操作将永久删除该节能建议，删除后无法恢复`,
            '确认删除',
            {
                confirmButtonText: '确认',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )
        await deleteSuggestion(suggestion_id)
        ElMessage.success('删除节能建议成功')
        fetchSuggestion(filterForm.value)
    } catch (error) {
        if (error === 'cancel') {
            ElMessage.info('已取消删除')
        } else {
            console.error('删除失败', error)
            ElMessage.error('删除节能建议失败，请稍后重试')
        }
    }
}

const fetchEnergyComparison = async (trend_data) => {
    try {
        const res = await getEnergyComparison(trend_data)
        gasData.value = res
        // console.log(gasData.value)
    } catch (error) {
        console.error(error)
    }
}

const fetchEnergyTrendData = async () => {
    const trendData = await getEnergyTrend({
        period: 'monthly',
        bill_type: 'gas'
    })

    const labels = []
    const gasUsageData = []
    const gasAmountData = []

    trendData.forEach(item => {
        const formattedDate = `${item.year}-${item.month.padStart(2, '0')}`
        labels.push(formattedDate)

        gasUsageData.push(item.usage)
        gasAmountData.push(item.amount)
    })

    chartData.value.labels = labels
    chartData.value.datasets[0].data = gasUsageData
    chartData.value.datasets[1].data = gasAmountData
}

const fetchAnomalyMonths = async () => {
    try {
        isLoadingAnomaly.value = true
        const res = await getAnomalyMonths('gas')
        const userData = await getCurrentUser()
        console.log(res)
        // console.log(userData)
        anomalyMonthsData.value = res
        setGasAnomalyMonthsData(res)
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
        const res = await getEnhancedEnergyAnalysis('gas', 'monthly')
        const userData = await getCurrentUser()
        console.log(res)
        suggestionData.value = res.ai_analysis
        setGasSuggestionData(res.ai_analysis)
        setUserId(userData.id)
    } catch (error) {
        console.error(error)
    } finally {
        isLoadingSuggestion.value = false
    }
}

const fetchSuggestion = async () => {
    try {
        isLoadingSuggestionList.value = true
        const res = await getSuggestion(filterForm.value)
        // console.log(res)
        tableData.value = res.items
        totalCount.value = res.total
    } catch (error) {
        console.error(error)
    } finally {
        isLoadingSuggestionList.value = false
    }
}

onMounted(() => {
    fetchEnergyComparison({
        period: 'monthly',
        bill_type: 'gas'
    })

    fetchEnergyTrendData()
    // fetchAnomalyMonths()
    if (currentUserId.value === userId.value) {
        // console.log('测试用户缓存')
        anomalyMonthsData.value = gasAnomalyMonthsData.value
        suggestionData.value = gasSuggestionData.value
    }

    fetchSuggestion(filterForm.value)
})
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

.gas-usage {
    height: 160px;
    background-color: rgb(243,104,18);
    border-radius: 15px;
}

.gas-amount {
    height: 160px;
    background-color: rgb(255,99,71);
    border-radius: 15px;
}

.gas-unit-price {
    height: 160px;
    background-color: rgb(255,69,0);
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

.gas-suggestion {
    margin-top: 20px;
}

.suggestion-header {
    display: flex;
    justify-content: space-between;
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
    transition: box-shadow 0.3s ease;
}

.suggestion-item-high:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-item-medium {
    margin-top: 10px;
    margin-bottom: 20px;
    background-color: #FEFCE8;
    border: 1px solid #FEF08A;
    border-radius: 5px;
    padding: 10px;
    transition: box-shadow 0.3s ease;
}

.suggestion-item-medium:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-item-low {
    margin-top: 10px;
    margin-bottom: 20px;
    background-color: #C8E6C9;
    border: 1px solid #a8c7a9;
    border-radius: 5px;
    padding: 10px;
    transition: box-shadow 0.3s ease;
}

.suggestion-item-low:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

.table-pagination {
    margin-top: 10px;
}
</style>

<style>
.el-select-dropdown__item {
    margin: initial !important;
    padding: 0 20px !important;
    line-height: 34px !important;
}
</style>