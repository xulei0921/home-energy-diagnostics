<template>
    <el-page-header :icon="ArrowLeft" title="返回" @back="goBack"></el-page-header>

    <el-row class="login-page">
        <el-col :span="6" :offset="9" class="form">
            <!-- 注册表单 -->
            <el-form
                v-if="isRegister"
                autocomplete="off"
                size="large"
                ref="form"
                :model="formData"
                :rules="rules"
            >
                <el-form-item>
                    <h1>注册</h1>
                </el-form-item>
                <el-form-item prop="username">
                    <el-input :prefix-icon="User" v-model="formData.username" placeholder="请输入用户名"></el-input>
                </el-form-item>
                <el-form-item prop="email">
                    <el-input :prefix-icon="Message" v-model="formData.email" placeholder="请输入邮箱"></el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input
                        :prefix-icon="Lock"
                        placeholder="请输入密码"
                        v-model="formData.password"
                        type="password"
                    ></el-input>
                </el-form-item>
                <el-form-item prop="repassword">
                    <el-input
                        :prefix-icon="Lock"
                        placeholder="请再次输入密码"
                        v-model="formData.repassword"
                        type="password"
                        @keyup.enter="handleRegister"
                    ></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" class="button" @click="handleRegister">
                        注册
                    </el-button>
                </el-form-item>
                <el-form-item>
                    <el-link type="info" :underline="false" @click="isRegister = false">
                        ← 返回
                    </el-link>
                </el-form-item>
            </el-form>
            <el-form
                ref="form"
                v-else
                autocomplete="off"
                size="large"
                :model="formData"
                :rules="rules"
            >
                <el-form-item>
                    <h1>登录</h1>
                </el-form-item>
                <el-form-item prop="username">
                    <el-input v-model="formData.username" :prefix-icon="User" placeholder="请输入用户名"></el-input>
                </el-form-item>
                <el-form-item prop="password">
                    <el-input
                        :prefix-icon="Lock"
                        placeholder="请输入密码"
                        v-model="formData.password"
                        type="password"
                        @keyup.enter="handleLogin"
                    ></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" class="button" @click="handleLogin">
                        登录
                    </el-button>
                </el-form-item>
                <el-form-item>
                    <el-link type="info" :underline="false" @click="isRegister=true">
                        注册
                    </el-link>
                </el-form-item>
            </el-form>
        </el-col>
    </el-row>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft, User, Lock, Message } from '@element-plus/icons-vue'
import { registerUser, loginUser } from '@/api/user';
import { useUserStore } from '@/stores';

const userStore = useUserStore()

const {
    setToken
} = userStore

const form = ref('')
const isRegister = ref(true)
const router = useRouter()
const formData = ref({
    username: '',
    email: '',
    password: '',
    repassword: ''
})

const rules = {
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
    ],
    repassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        {
            validator: (rule, value, callback) => {
                if (value !== formData.value.password) {
                    callback(new Error('两次输入密码不一致!'))
                } else {
                    callback()
                }
            },
            trigger: 'blur'
        }
    ]
}

const handleRegister = async () => {
    try {
        await form.value.validate()
        await registerUser(formData.value)
        ElMessage.success('注册成功')
        // 切换到登录页面
        isRegister.value = false
    } catch (error) {
        console.error(error)
    }
}

const handleLogin = async () => {
    try {
        await form.value.validate()
        const res = await loginUser(formData.value)
        console.log(res)
        setToken(res.access_token)
        ElMessage.success('登陆成功')
        // 跳转到首页
        router.push('/')
    } catch (error) {
        console.error(error)
    }
}

const goBack = () => {
    router.go(-1)
}

watch(isRegister, () => {
    formData.value = {
        username: '',
        email: '',
        password: '',
        repassword: ''
    }
})
</script>

<style scoped>
.login-page {
    height: 100vh;
    background-color: #fff;
}
.form {
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.button {
    width: 100%;
}
</style>