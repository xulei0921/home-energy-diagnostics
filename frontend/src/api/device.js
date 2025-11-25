import request from '@/utils/request'

// 根据 device_type 获取设备列表
export const getDevices = (filterData) => {
    return request.get('/devices/', {
        params: filterData
    })
}

// 根据 ID 获取设备
export const getDeviceById = (device_id) => {
    return request.get(`/devices/${device_id}`)
} 

// 新增设备信息
export const createDevice = (data) => {
    return request.post('/devices/', data)
}

// 编辑设备信息
export const updateDevice = (device_id, update_data) => {
    return request.put(`/devices/${device_id}`, update_data)
}

// 删除设备信息
export const deleteDevice = (device_id) => {
    return request.delete(`/devices/${device_id}`)
}

// 获取设备使用记录
export const getDeviceUsage = (data) => {
    return request.get(`/devices/usage/${data.device_id}`, {
        params: data
    })
}

// 新增设备使用记录
export const createDeviceUsage = (createData) => {
    return request.post('/devices/usage', createData)
}

// 编辑设备使用记录
export const updateDeviceUsage = (device_id, usage_id, updateData) => {
    return request.put(`/devices/usage/${device_id}/${usage_id}`, updateData)
}

// 删除设备使用记录
export const deleteDeviceUsage = (device_id, usage_id) => {
    return request.delete(`/devices/usage/${device_id}/${usage_id}`)
}