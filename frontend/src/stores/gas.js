import { defineStore } from "pinia";
import { ref } from "vue";

// 燃气分析模块
export const useGasStore = defineStore('gas', () => {
    const gasSuggestionData = ref({})
    const gasAnomalyMonthsData = ref([])
    const userId = ref(0)

    const setGasSuggestionData = (newData) => {
        gasSuggestionData.value = newData
    }

    const setGasAnomalyMonthsData = (newData) => {
        gasAnomalyMonthsData.value = newData
    }

    const setUserId = (newId) => {
        userId.value = newId
    }

    return {
        gasSuggestionData,
        gasAnomalyMonthsData,
        userId,
        setGasSuggestionData,
        setGasAnomalyMonthsData,
        setUserId
    }
}, {
    persist: true
})