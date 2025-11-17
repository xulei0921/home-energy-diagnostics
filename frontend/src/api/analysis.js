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