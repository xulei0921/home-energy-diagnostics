<template>
    <el-header class="fixed-header">
        <div class="header-container">
            <div class="header-title">{{ currentTitle }}</div>
            <el-dropdown>
                <div class="el-dropdown-link">
                    <el-avatar :src="currentUser.avatar" class="avatar" :icon="UserFilled"></el-avatar>
                    <span class="username">{{ currentUser.username }}</span>
                    <el-icon class="el-dropdown-icon">
                        <ArrowDown />
                    </el-icon>
                </div>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item @click="$router.push('/index/settings')">个人中心</el-dropdown-item>
                        <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
    </el-header>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getCurrentUser } from '@/api/user'
import { useUserStore } from '@/stores'
import { User, UserFilled } from '@element-plus/icons-vue'

const userStore = useUserStore()
const currentUser = ref({})

const {
    removeToken
} = userStore

const router = useRouter()
const route = useRoute()
const currentTitle = ref('仪表盘')

const titleMap = {
    '/index/dashboard': '仪表盘',
    '/index/electricity': '电力分析',
    '/index/gas': '燃气分析',
    '/index/water': '水资源分析',
    '/index/devices': '设备管理',
    '/index/bills': '账单管理',
    '/index/settings': '个人设置'
}

const logout = async () => {
    try {
        removeToken()
        ElMessage.success('退出登录成功')
        
        await nextTick()
        router.push('/login')
    } catch (error) {
        ElMessage.error('退出登录失败，请稍后重试'),
        console.error('Logout error:', error)
    }
}

const fetchCurrentUser = async () => {
    try {
        const res = await getCurrentUser()
        // console.log(res)
        currentUser.value = res
    } catch (error) {
        console.error(error)
    }
}

watch(() => route.path, (newPath) => {
    currentTitle.value = titleMap[newPath] || '首页'
}, {
    immediate: true
})

onMounted(() => {
    fetchCurrentUser()
})
</script>

<style scoped>
.fixed-header {
    background-color: #fff;
    position: fixed;
    top: 0;
    right: 8px;
    left: 270px;
    z-index: 100;
    height: 60px;
    border-bottom: #F0F1F2 solid 1px;
}

.header-container {
    display: flex;
    justify-content: space-between;
    /* margin: 5px; */
    /* padding: 10px; */
    align-items: center;
    /* padding: 0 10px; */
    /* margin-left: 250px; */
    width: 100%;
    height: 100%;
}

.header-title {
    font-size: 17px;
}

.el-dropdown-link {
    cursor: pointer;
    display: flex;
    align-items: center;
}

.el-dropdown-icon {
    transition: transform 0.3s ease;
}

.el-dropdown-link:hover {
    color: #409EFF;
    .el-dropdown-icon {
        transform: rotate(180deg);
    }
}

.username {
    margin: 5px;
}
</style>