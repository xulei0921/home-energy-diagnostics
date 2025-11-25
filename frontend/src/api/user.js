import request from '@/utils/request'

// 用户注册
export const registerUser = (registerData) => {
    return request.post('/users/register', registerData)
}

// 用户登录
export const loginUser = ({ username, password }) => {
    const formData = `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    return request.post('/users/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

// 获取当前用户信息
export const getCurrentUser = () => {
    return request.get('/users/me')
}

// 更新当前用户信息
export const updateCurrentUser = (userUpdate) => {
    return request.put('/users/me', userUpdate)
}