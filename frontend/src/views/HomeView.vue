<template>
    <el-container>
        <SideBar />
        <el-container class="content-container">
            <Header />
            <el-main class="main-content">
                <RouterView />
            </el-main>
        </el-container>
    </el-container>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import SideBar from '@/components/layout/SideBar.vue';
import Header from '@/components/layout/Header.vue';

</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

.content-container {
    /* margin: 0 15px; */
    margin-left: 15px;
}

.main-content {
    background-color: #F9FAFB;
    margin-left: 250px;
    margin-top: 60px;
    padding: 10px;
    height: calc(100vh - 60px);
}
</style>