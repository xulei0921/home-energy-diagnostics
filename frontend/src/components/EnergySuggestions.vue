<template>
    <div class="energy-suggestions-container">
        <div class="suggestions-header">
            <h2 style="margin: 0; padding: 0;">智能节能建议</h2>
            <div class="header-controls">
                <el-select v-model="selectedBillType" placeholder="选择能源类型" style="width: 150px; margin-right: 10px;">
                    <el-option label="全部" value=""></el-option>
                    <el-option label="电力" value="electricity"></el-option>
                    <el-option label="燃气" value="gas"></el-option>
                    <el-option label="水" value="water"></el-option>
                </el-select>
                <el-select v-model="selectedPeriod" placeholder="分析周期" style="width: 120px; margin-right: 10px;">
                    <el-option label="月度" value="monthly"></el-option>
                    <el-option label="季度" value="quarter"></el-option>
                    <el-option label="年度" value="annual"></el-option>
                </el-select>
                <el-button type="primary" @click="fetchSuggestions" :loading="isLoading">
                    生成建议
                </el-button>
            </div>
        </div>

        <div
            v-loading="isLoading"
            element-loading-text="分析数据量较大，请耐心等待..."
            class="suggestions-content"
        >
            <!-- 无数据状态 -->
            <div v-if="!isLoading && (!suggestionsData || !suggestionsData.energy_analyses || suggestionsData.energy_analyses.length === 0)" 
                 class="no-data-container">
                <el-empty description="暂无节能建议" />
            </div>

            <!-- 有数据状态 -->
            <div v-else-if="suggestionsData" class="suggestions-data">
                <!-- 整体评估 -->
                <div class="overall-assessment" v-if="suggestionsData.overall_summary">
                    <h3>整体评估</h3>
                    <div class="assessment-content">
                        <p>{{ suggestionsData.overall_summary }}</p>
                        <!-- <div class="risk-indicator">
                            <span>风险等级：</span>
                            <el-tag :type="getRiskTagType(suggestionsData.risk_level)">
                                {{ getRiskLevelText(suggestionsData.risk_level) }}
                            </el-tag>
                        </div>
                        <div class="optimization-indicator">
                            <span>优化潜力：</span>
                            <el-tag :type="getOptimizationTagType(suggestionsData.optimization_potential)">
                                {{ getOptimizationPotentialText(suggestionsData.optimization_potential) }}
                            </el-tag>
                        </div> -->
                    </div>
                </div>

                <!-- 能源类型分析 -->
                <div class="energy-analyses" v-if="suggestionsData.energy_analyses && suggestionsData.energy_analyses.length > 0">
                    <h3>能源类型分析</h3>
                    <el-tabs v-model="activeEnergyTab" type="card">
                        <el-tab-pane 
                            v-for="analysis in suggestionsData.energy_analyses" 
                            :key="analysis.bill_type"
                            :label="getEnergyTypeText(analysis.bill_type)" 
                            :name="analysis.bill_type"
                        >
                            <div class="energy-analysis-content">
                                <!-- AI分析 -->
                                <div class="ai-analysis" v-if="analysis.ai_analysis">
                                    <span style="font-weight: 600;">智能分析</span>
                                    <div class="ai-analysis-item">
                                        <p>{{ analysis.ai_analysis.overall_assessment }}</p>
                                        
                                        <div v-if="analysis.ai_analysis.key_insights && analysis.ai_analysis.key_insights.length > 0" class="key-insights">
                                            <h3>关键洞察</h3>
                                            <ul>
                                                <li v-for="(insight, index) in analysis.ai_analysis.key_insights" :key="index">
                                                    {{ insight }}
                                                </li>
                                            </ul>
                                        </div>

                                        <div v-if="analysis.ai_analysis.seasonal_analysis" class="seasonal-analysis">
                                            <h3>季节性分析</h3>
                                            <p style="font-size: 16px;">{{ analysis.ai_analysis.seasonal_analysis }}</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- 具体建议 -->
                                <div class="suggestions-list" v-if="analysis.suggestions && analysis.suggestions.length > 0">
                                    <h3>节能建议</h3>
                                    <div class="suggestion-cards">
                                        <el-card 
                                            v-for="(suggestion, index) in analysis.ai_analysis.suggestions" 
                                            :key="index"
                                            :class="getSuggestionStyle(suggestion.impact_rating)"
                                            shadow="hover"
                                        >
                                            <div class="suggestion-header">
                                                <div class="suggestion-title">
                                                    <div style="font-weight: 500;">{{ suggestion.suggestion_title }}</div>
                                                </div>
                                                <div class="rate-and-date">
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
                                                <p>{{ suggestion.suggestion_text }}</p>
                                            </div>
                                        </el-card>
                                    </div>
                                </div>
                            </div>
                        </el-tab-pane>
                    </el-tabs>
                </div>

                <!-- 综合建议 -->
                <div class="general-suggestions" v-if="suggestionsData.comprehensive_suggestions && suggestionsData.comprehensive_suggestions.length > 0">
                    <h3>综合建议</h3>
                    <div class="suggestion-cards">
                        <el-card 
                            v-for="(suggestion, index) in suggestionsData.comprehensive_suggestions" 
                            :key="index"
                            :class="getSuggestionStyle(suggestion.impact_rating)"
                            shadow="hover"
                        >
                            <div class="suggestion-header">
                                <div class="suggestion-title">
                                    <div style="font-weight: 500;">{{ suggestion.suggestion_title }}</div>
                                </div>
                                <div class="rate-and-date">
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
                                <p>{{ suggestion.suggestion_text }}</p>
                                <div v-if="suggestion.potential_savings" class="potential-savings">
                                    预计节省: {{ suggestion.potential_savings }}
                                </div>
                            </div>
                        </el-card>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getComprehensiveAnalysis } from '@/api/analysis'
import { getCurrentUser } from '@/api/user'
import { Warning, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useUserStore } from '@/stores'
import { storeToRefs } from 'pinia'

const icons = [Warning, Warning, Warning]
const dashboardStore = useDashboardStore()
const userStore = useUserStore()

const {
    userId,
    dashboardSuggestionsData
} = storeToRefs(dashboardStore)

const {
    setUserId,
    setDashboardSuggestionsData
} = dashboardStore

const {
    currentUserId
} = storeToRefs(userStore)

const isLoading = ref(false)
const suggestionsData = ref(null)
const selectedBillType = ref('')
const selectedPeriod = ref('monthly')
const activeEnergyTab = ref('')

// 获取节能建议
const fetchSuggestions = async () => {
    try {
        isLoading.value = true
        const params = {
            period: selectedPeriod.value
        }
        
        if (selectedBillType.value) {
            params.bill_type = selectedBillType.value
        }
        
        const response = await getComprehensiveAnalysis(params)
        const userData = await getCurrentUser()
        suggestionsData.value = response
        setUserId(userData.id)
        setDashboardSuggestionsData(response)
        
        // 设置默认激活的标签页
        if (response.energy_analyses && response.energy_analyses.length > 0) {
            activeEnergyTab.value = response.energy_analyses[0].bill_type
        }
    } catch (error) {
        console.error('获取节能建议失败:', error)
        // 显示错误提示但保持界面可用
        suggestionsData.value = {
            energy_analyses: [],
            overall_assessment: '暂时无法获取智能分析，请稍后重试',
            general_suggestions: [
                {
                    title: '基础节能建议',
                    description: '请确保及时关闭不使用的电器设备，合理设置空调温度，定期检查设备能效状态。',
                    priority: 'medium',
                    potential_savings: '预计可节省5-10%能源消耗'
                }
            ]
        }
    } finally {
        isLoading.value = false
    }
}

// 获取能源类型文本
const getEnergyTypeText = (billType) => {
    switch(billType) {
        case 'electricity': return '电力'
        case 'gas': return '燃气'
        case 'water': return '水'
        default: return '未知'
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

// 组件挂载时获取默认建议
onMounted(() => {
    // fetchSuggestions()
    if (currentUserId.value === userId.value) {
        suggestionsData.value = dashboardSuggestionsData.value
        if (suggestionsData.value.energy_analyses && suggestionsData.value.energy_analyses.length > 0) {
            activeEnergyTab.value = suggestionsData.value.energy_analyses[0].bill_type
        }
    }
})
</script>

<style scoped>
/* * {
    margin: 0;
    padding: 0;
} */

.energy-suggestions-container {
    overflow-y: auto;
    height: 422px;
    width: 100%;
}

.suggestions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.suggestions-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}

.header-controls {
    display: flex;
    align-items: center;
}

.suggestions-content {
    min-height: 300px;
}

.no-data-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
}

.suggestions-data {
    width: 100%;
}

.overall-assessment,
.energy-analyses,
.general-suggestions {
    margin-bottom: 20px;
    font-size: 18px;
}

:deep(.el-tabs__item) {
    font-size: 17px;
}

.overall-assessment h3,
.energy-analyses h3,
.general-suggestions h3 {
    margin-bottom: 10px;
    font-size: 19px;
    font-weight: 600;
}

.assessment-content {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 18px;
}

.risk-indicator,
.optimization-indicator {
    margin-top: 10px;
    display: flex;
    align-items: center;
}

.risk-indicator span,
.optimization-indicator span {
    margin-right: 10px;
    font-weight: 500;
}

.energy-analysis-content {
    padding: 10px 0;
}

.ai-analysis,
.suggestions-list {
    margin-bottom: 20px;
    font-size: 18px;
}

.ai-analysis h3,
.suggestions-list h3 {
    margin-bottom: 10px;
    font-size: 19px;
    font-weight: 600;
}

.key-insights,
.seasonal-analysis {
    margin-top: 10px;
}

.key-insights h3,
.seasonal-analysis h3 {
    margin-bottom: 5px;
    font-size: 19px;
    font-weight: 600;
}

.key-insights ul {
    padding-left: 20px;
    margin: 5px 0;
}

.key-insights li {
    margin-bottom: 10px;
    font-size: 16px;
}

.seasonal-analysis p {
    font-size: 13px;
    margin: 5px 0;
}

.suggestion-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill);
    gap: 15px;
}

.suggestion-card {
    height: 100%;
}

.suggestion-header {
    /* display: flex; */
    align-items: center;
    margin-bottom: 10px;
    /* justify-content: space-between; */
}

.suggestion-icon {
    margin-right: 8px;
    color: #409EFF;
}

.suggestion-priority {
    font-size: 12px;
    font-weight: 600;
}

.suggestion-content p {
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 10px;
}

.potential-savings {
    font-size: 12px;
    color: #67C23A;
    font-weight: 600;
}

.suggestion-item-high {
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 5px;
    padding: 5px;
}

.suggestion-item-medium {
    background-color: #FEFCE8;
    border: 1px solid #FEF08A;
    border-radius: 5px;
    padding: 5px;
}

.suggestion-item-low {
    background-color: #C8E6C9;
    border: 1px solid #a8c7a9;
    border-radius: 5px;
    padding: 5px;
}

.rate-and-date {
    font-size: 17px;
}

.suggestion-date {
    margin-left: 10px;
}
</style>