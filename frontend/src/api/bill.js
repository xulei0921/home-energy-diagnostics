import request from '@/utils/request'

// 创建账单数据
export const createBill = (data) => {
    return request.post('/bills/', data)
}

// 获取账单数据
export const getBills = (filterData) => {
    return request.get('/bills/', {
        params: filterData
    })
}

// 获取账单数据 by ID
export const getBillById = (bill_id) => {
    return request.get(`/bills/${bill_id}`)
}

// 编辑账单
export const updateBill = (bill_id, updateData) => {
    return request.put(`/bills/${bill_id}`, updateData)
}

// 删除账单
export const deleteBill = (bill_id) => {
    return request.delete(`/bills/${bill_id}`)
}