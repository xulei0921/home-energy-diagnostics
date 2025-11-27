<template>
    <div class="energy-suggestions-container">
        <div class="suggestions-header">
            <h3>智能节能建议</h3>
            <div class="header-controls">
                <el-select v-model="selectedBillType" placeholder="选择能源类型" style="width: 120px; margin-right: 10px;">
                    <el-option label="全部" value=""></el-option>
                    <el-option label="电力" value="electricity"></el-option>
                    <el-option label="燃气" value="gas"></el-option>
                    <el-option label="水" value="water"></el-option>
                </el-select>
                <el-select v-model="selectedPeriod" placeholder="分析周期" style="width: 120px; margin-right: 10px;">
                    <el-option label="月度" value="monthly"></el-option>
                    <el-option label="季度" value="quarterly"></el-option>
                    <el-option label="年度" value="yearly"></el-option>
                </el-select>
                <el-button type="primary" @click="fetchSuggestions" :loading="isLoading">
                    生成建议
                </el-button>
            </div>
        </div>

        <div v-loading="isLoading" class="suggestions-content">
            <!-- 无数据状态 -->
            <div v-if="!isLoading && (!suggestionsData || !suggestionsData.energy_analyses || suggestionsData.energy_analyses.length === 0)" 
                 class="no-data-container">
                <el-empty description="暂无节能建议" />
            </div>

            <!-- 有数据状态 -->
            <div v-else-if="suggestionsData" class="suggestions-data">
                <!-- 整体评估 -->
                <div class="overall-assessment" v-if="suggestionsData.overall_assessment">
                    <h4>整体评估</h4>
                    <div class="assessment-content">
                        <p>{{ suggestionsData.overall_assessment }}</p>
                        <div class="risk-indicator">
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
                        </div>
                    </div>
                </div>

                <!-- 能源类型分析 -->
                <div class="energy-analyses" v-if="suggestionsData.energy_analyses && suggestionsData.energy_analyses.length > 0">
                    <h4>能源类型分析</h4>
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
                                    <h5>智能分析</h5>
                                    <div class="ai-analysis-item">
                                        <p>{{ analysis.ai_analysis.overall_assessment }}</p>
                                        
                                        <div v-if="analysis.ai_analysis.key_insights && analysis.ai_analysis.key_insights.length > 0" class="key-insights">
                                            <h6>关键洞察</h6>
                                            <ul>
                                                <li v-for="(insight, index) in analysis.ai_analysis.key_insights" :key="index">
                                                    {{ insight }}
                                                </li>
                                            </ul>
                                        </div>

                                        <div v-if="analysis.ai_analysis.seasonal_analysis" class="seasonal-analysis">
                                            <h6>季节性分析</h6>
                                            <p>{{ analysis.ai_analysis.seasonal_analysis }}</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- 具体建议 -->
                                <div class="suggestions-list" v-if="analysis.suggestions && analysis.suggestions.length > 0">
                                    <h5>节能建议</h5>
                                    <div class="suggestion-cards">
                                        <el-card 
                                            v-for="(suggestion, index) in analysis.ai_analysis.suggestions" 
                                            :key="index"
                                            class="suggestion-card"
                                            shadow="hover"
                                        >
                                            <div class="suggestion-header">
                                                <el-icon class="suggestion-icon">
                                                    <!-- <component :is="getSuggestionIcon(suggestion.priority)" /> -->
                                                    <span>{{ suggestion.impact_rating }}</span>
                                                </el-icon>
                                                <!-- <span class="suggestion-priority">{{ getPriorityText(suggestion.priority) }}</span> -->
                                            </div>
                                            <div class="suggestion-content">
                                                <!-- <p>{{ suggestion.description }}</p> -->
                                                <p>{{ suggestion.suggestion_text }}</p>
                                                <!-- <div v-if="suggestion.potential_savings" class="potential-savings">
                                                    预计节省: {{ suggestion.potential_savings }}
                                                </div> -->
                                            </div>
                                        </el-card>
                                    </div>
                                </div>
                            </div>
                        </el-tab-pane>
                    </el-tabs>
                </div>

                <!-- 综合建议 -->
                <div class="general-suggestions" v-if="suggestionsData.general_suggestions && suggestionsData.general_suggestions.length > 0">
                    <h4>综合建议</h4>
                    <div class="suggestion-cards">
                        <el-card 
                            v-for="(suggestion, index) in suggestionsData.general_suggestions" 
                            :key="index"
                            class="suggestion-card"
                            shadow="hover"
                        >
                            <div class="suggestion-header">
                                <el-icon class="suggestion-icon">
                                    <component :is="getSuggestionIcon(suggestion.priority)" />
                                </el-icon>
                                <span class="suggestion-priority">{{ getPriorityText(suggestion.priority) }}</span>
                            </div>
                            <div class="suggestion-content">
                                <p>{{ suggestion.description }}</p>
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
import { Warning, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'

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
        suggestionsData.value = response
        
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

// 获取风险等级标签类型
const getRiskTagType = (riskLevel) => {
    switch(riskLevel) {
        case 'high': return 'danger'
        case 'medium': return 'warning'
        case 'low': return 'SuccessFilled'
        default: return 'info'
    }
}

// 获取风险等级文本
const getRiskLevelText = (riskLevel) => {
    switch(riskLevel) {
        case 'high': return '高'
        case 'medium': return '中'
        case 'low': return '低'
        default: return '未知'
    }
}

// 获取优化潜力标签类型
const getOptimizationTagType = (potential) => {
    switch(potential) {
        case 'high': return 'SuccessFilled'
        case 'medium': return 'warning'
        case 'low': return 'info'
        default: return 'info'
    }
}

// 获取优化潜力文本
const getOptimizationPotentialText = (potential) => {
    switch(potential) {
        case 'high': return '高'
        case 'medium': return '中'
        case 'low': return '低'
        default: return '未知'
    }
}

// 获取优先级图标
const getSuggestionIcon = (priority) => {
    switch(priority) {
        case 'high': return Warning
        case 'medium': return InfoFilled
        case 'low': return SuccessFilled
        default: return InfoFilled
    }
}

// 获取优先级文本
const getPriorityText = (priority) => {
    switch(priority) {
        case 'high': return '高优先级'
        case 'medium': return '中优先级'
        case 'low': return '低优先级'
        default: return '未知'
    }
}

// 组件挂载时获取默认建议
onMounted(() => {
    fetchSuggestions()
})
</script>

<style scoped>
.energy-suggestions-container {
    height: 100%;
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
}

.overall-assessment h4,
.energy-analyses h4,
.general-suggestions h4 {
    margin-bottom: 10px;
    font-size: 16px;
    font-weight: 600;
}

.assessment-content {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
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
}

.ai-analysis h5,
.suggestions-list h5 {
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: 600;
}

.key-insights,
.seasonal-analysis {
    margin-top: 10px;
}

.key-insights h6,
.seasonal-analysis h6 {
    margin-bottom: 5px;
    font-size: 13px;
    font-weight: 600;
}

.key-insights ul {
    padding-left: 20px;
    margin: 5px 0;
}

.key-insights li {
    margin-bottom: 5px;
    font-size: 13px;
}

.seasonal-analysis p {
    font-size: 13px;
    margin: 5px 0;
}

.suggestion-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
}

.suggestion-card {
    height: 100%;
}

.suggestion-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
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
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 10px;
}

.potential-savings {
    font-size: 12px;
    color: #67C23A;
    font-weight: 600;
}
</style>