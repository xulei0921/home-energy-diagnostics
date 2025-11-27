import axios from "axios";
import { ElMessage } from "element-plus";
import router from "@/router";
import { useUserStore } from "@/stores";

const baseURL = import.meta.env.VITE_APP_API_BASE_URL

const instance = axios.create({
    // 基础地址，超时时间
    baseURL,
    timeout: 300000  // 增加到3分钟，以适应AI服务的响应时间
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

        // 检查是否为静默请求（通过config中的silent标识）
        const isSilent = err.config?.silent === true

        // 处理404错误且为静默请求的情况（如获取家庭信息时没有数据）
        if (err.response?.status === 404 && isSilent) {
            return Promise.reject(err)
        }

        // 错误的默认情况 => 只要给提示（非静默请求）
        if (!isSilent) {
            const errorMsg = err.response?.data?.detail || '请求失败，请稍后重试'
            ElMessage.error(errorMsg)
            return Promise.reject(errorMsg)
        }

        return Promise.reject(err)
    }
)

export default instance
export { baseURL }
