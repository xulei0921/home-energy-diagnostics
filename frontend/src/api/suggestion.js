import request from '@/utils/request'

// 获取建议列表
export const getSuggestion = (filterData) => {
    return request.get('/suggestion/', {
        params: filterData
    })
}

// 编辑节能建议
export const updateSuggestion = (suggestion_id, updateData) => {
    return request.put(`/suggestion/${suggestion_id}`, updateData)
}

// 删除节能建议
export const deleteSuggestion = (suggestion_id) => {
    return request.delete(`/suggestion/${suggestion_id}`)
}