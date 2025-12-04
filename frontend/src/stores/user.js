import { defineStore } from "pinia";
import { ref } from "vue";
import { isTokenExpired } from "@/utils/jwt";

// 用户模块 token setToken removeToken
export const useUserStore = defineStore('big-user', () => {
    const token = ref('')
    const currentUserId = ref(0)

    const setCurrentUserId = (newId) => {
        currentUserId.value = newId
    }

    const setToken = (newToken) => {
        token.value = newToken
    }

    const removeToken = () => {
        token.value = ''
    }

    const isLogin = () => {
        if (isTokenExpired(token.value)) {
            token.value = ''
            return false
        }
        return true
    }

    // const isFamilyInfoExist = () => {

    // }

    return {
        token,
        currentUserId,
        setToken,
        setCurrentUserId,
        removeToken,
        isLogin
    }
}, {
    persist: true
})