<template>
    <el-aside class="aside-menu">
        <h3 class="title">能耗分析平台</h3>
        <el-menu 
            class="side-menu"
            router
            :default-active="route.path"
        >
            <el-menu-item index="/index/dashboard">
                <el-icon><Odometer /></el-icon>
                <!-- <i class="iconfont icon-yibiaopan"></i> -->
                <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/index/electricity">
                <i class="iconfont icon-dian" style="font-size: 20px;"></i>
                <span>电力分析</span>
            </el-menu-item>
            <el-menu-item index="/index/gas">
                <i class="iconfont icon-ranqi"></i>
                <span>燃气分析</span>
            </el-menu-item>
            <el-menu-item index="/index/water">
                <i class="iconfont icon-water"></i>
                <span>水资源分析</span>
            </el-menu-item>
            <el-menu-item index="/index/devices">
                <i class="iconfont icon-chatou1"></i>
                <span>设备管理 </span>
            </el-menu-item>
            <el-menu-item index="/index/bills">
                <i class="iconfont icon-zhangdan"></i>
                <span>账单管理</span>
            </el-menu-item>
            <el-menu-item index="/index/settings">
                <i class="iconfont icon-shezhi"></i>
                <span>个人设置</span>
            </el-menu-item>
        </el-menu>
    </el-aside>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { Odometer } from '@element-plus/icons-vue'

const route = useRoute()
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

.aside-menu {
    position: fixed;
    height: 100vh;
    width: 250px;
    background-color: #fff;
}

.title {
    color: #409EFF;
    font-size: 25px;
    border-bottom: #F0F1F2 solid 2px;
    padding: 10px;
}

.side-menu {
    border: none;
}

.iconfont {
    margin-right: 5px;
}

.el-menu-item {
    font-size: 17px;
}

:deep(.el-menu-item.is-active) {
  background-color: #5096F9 !important;  /* 高亮背景色 */
  color: white !important;  /* 高亮文字色 */
}

:deep(.el-menu-item) {
  border-radius: 10px !important;  /* 圆角大小，可调整 */
  margin: 6px 4px !important;  /* 增加间距，让圆角更明显 */
  padding: 0 16px !important;  /* 调整内边距 */
}
</style>