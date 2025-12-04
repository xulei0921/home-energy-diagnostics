import { defineStore } from "pinia";
import { ref } from "vue";

// 仪表盘模块
export const useDashboardStore = defineStore('dashboard', () => {
    const userId = ref(0)
    const dashboardSuggestionsData = ref(null)

    const setUserId = (newId) => {
        userId.value = newId
    }

    const setDashboardSuggestionsData = (newData) => {
        dashboardSuggestionsData.value = newData
    }

    return {
        userId,
        dashboardSuggestionsData,
        setUserId,
        setDashboardSuggestionsData
    }
},{
    persist: true
})