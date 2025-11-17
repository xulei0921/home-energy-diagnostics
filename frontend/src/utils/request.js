import axios from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";
import { useUserStore } from "@/stores";

const baseURL = import.meta.env.VITE_APP_API_BASE_URL

const instance = axios.create({
    // 基础地址，超时时间
    baseURL,
    timeout: 15000
})

// 请求拦截器
instance.interceptors.request.use(
    (config) => {
        // 携带token
        const userStore = useUserStore()
        if (userStore.token) {
            config.headers.Authorization = `Bearer ${userStore.token}`
        }
        return config
    },
    (err) => Promise.reject(err)
)

// 响应拦截器
instance.interceptors.response.use(
    (res) => {
        return res.data
    },
    (err) => {
        // 处理401错误
        // 错误的特殊情况 => 401 权限不足 或 token 过期 => 拦截到登录
        if (err.response?.status === 401) {
            const userStore = useUserStore()
            if (userStore.token) {
                userStore.removeToken()
            }
            router.push('/login')
            ElMessage.error({ message: err.response?.data?.detail } || '请求失败，请稍后重试')
            return Promise.reject(err.response?.data?.detail || '请求失败')
        }

        // 错误的默认情况 => 只要给提示
        const errorMsg = err.response?.data?.detail || '请求失败，请稍后重试'
        ElMessage.error(errorMsg)
        return Promise.reject(errorMsg)
    }
)

export default instance
export { baseURL }