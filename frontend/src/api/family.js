import request from '@/utils/request'

// 当前用户家庭信息是否存在
export const isFamilyInfoExist = () => {
    return request.get('/family/is-exist')
}

// 获取当前用户家庭信息
export const getFamilyInfo = () => {
    return request.get('/family/')
}

// 为当前用户新增家庭信息
export const createFamilyInfo = (familyData) => {
    return request.post('/family/', familyData)
}

// 编辑家庭信息
export const updateFamilyInfo = (familyUpdate) => {
    return request.put('/family/', familyUpdate)
}