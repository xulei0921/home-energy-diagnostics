import { defineStore } from "pinia";
import { ref } from "vue";

// 电力分析模块
export const useElectricityStore = defineStore('electricity', ()=> {
    const elecSuggestionData = ref({})
    const elecAnomalyMonthsData = ref([])
    const userId = ref(0)

    const setElecSuggestionData = (newData) => {
        elecSuggestionData.value = newData
    }

    const setElecAnomalyMonthsData = (newData) => {
        elecAnomalyMonthsData.value = newData
    }

    const setUserId = (newId) => {
        userId.value = newId
    }

    return {
        elecSuggestionData,
        elecAnomalyMonthsData,
        userId,
        setElecSuggestionData,
        setElecAnomalyMonthsData,
        setUserId
    }
}, {
    persist: true
})