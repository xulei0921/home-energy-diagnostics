import request from '@/utils/request'

// 获取能耗趋势数据
export const getEnergyTrend = (query_data) => {
    return request.get('/analysis/energy-trend', {
        params: query_data
    })
}

// 获取最新月份能耗数据的同比，环比数据
export const getEnergyComparison = (trend_data) => {
    return request.get('/analysis/energy-comparison', {
        params: trend_data
    })
}

// 获取最新月份的各类能源花费数据
export const getEnergyCostsDistribution = () => {
    return request.get('/analysis/energy-costs-distribution')
}

// 获取设备能耗占比数据
export const getDeviceConsumption = (bill_type) => {
    return request.get(`/analysis/device-consumption/${bill_type}`)
}

// 获取综合能耗分析结果
export const getComprehensiveAnalysis = (query_data) => {
    return request.get('/analysis/comprehensive-analysis', {
        params: query_data
    })
}