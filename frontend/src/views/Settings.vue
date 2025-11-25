<template>
    <el-tabs v-model="activeName" class="info-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="个人信息" name="first">
            <el-form
                label-position="top"
                size="large"
                ref="form"
                :rules="rules"
                :model="currentUser"
            >
                <el-form-item label="用户名">
                    <el-input :prefix-icon="User" disabled v-model="currentUser.username"></el-input>
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input :prefix-icon="Message" :disabled="!isEdit" v-model="currentUser.email"></el-input>
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                    <el-input :prefix-icon="Iphone" :disabled="!isEdit" v-model="currentUser.phone"></el-input>
                </el-form-item>
                <el-form-item label="头像">
                    <el-upload
                        :disabled="!isEdit"
                        class="avatar-uploader"
                        :action="`${baseURL}/users/upload-image`"
                        :on-success="handleImageSuccess"
                        list-type="picture-card"
                        :limit="1"
                    >
                        <el-icon class="avatar-uploader-icon">
                            <Plus />
                        </el-icon>
                    </el-upload>
                </el-form-item>
                <el-form-item class="button-right">
                    <div class="edit" v-if="!isEdit">
                        <el-button type="primary" @click="isEdit = true">编辑</el-button>
                    </div>
                    <div class="submit-edit" v-else>
                        <el-button @click="handleCancel">取消</el-button>
                        <el-button type="primary" @click="submitEditForm">保存</el-button>
                    </div>
                </el-form-item>
            </el-form>
        </el-tab-pane>
        <el-tab-pane label="家庭信息" name="second">
            <el-form
                v-if="hasFamilyInfo || isAddingFamily"
                label-position="top"
                size="large"
                :model="currentUserFamilyInfo"
            >
                <el-alert
                    title="提示"
                    type="info"
                    description="家庭人数、房屋面积、居住地点会影响能耗分析的推荐建议"
                    show-icon
                    style="margin: 16px 0;"
                ></el-alert>
                <el-form-item label="家庭人数">
                    <el-input-number
                        :disabled="!isEditFamily && !isAddingFamily"
                        v-model="currentUserFamilyInfo.family_size"
                        :min="1"
                    >
                        <template #suffix>人</template>
                    </el-input-number>
                </el-form-item>
                <el-form-item label="房屋面积">
                    <el-input-number
                        :disabled="!isEditFamily && !isAddingFamily"
                        v-model="currentUserFamilyInfo.house_area"
                        :min="0"
                    >
                        <template #suffix>
                            <span>㎡</span>
                        </template>
                    </el-input-number>
                </el-form-item>
                <el-form-item label="居住地点">
                    <el-input
                        :prefix-icon="MapLocation"
                        :disabled="!isEditFamily && !isAddingFamily"
                        v-model="currentUserFamilyInfo.location"
                    ></el-input>
                </el-form-item>
                <el-form-item label="房屋年龄">
                    <el-input-number
                        :disabled="!isEditFamily && !isAddingFamily"
                        v-model="currentUserFamilyInfo.building_age"
                        :min="0"
                    >
                        <template #suffix>
                            <span>年</span>
                        </template>
                    </el-input-number>
                </el-form-item>
                <el-form-item class="button-right">
                    <div class="submit-add" v-if="isAddingFamily">
                        <el-button @click="isAddingFamily = false">取消</el-button>
                        <el-button @click="submitAddFamilyForm" type="primary">添加</el-button>
                    </div>
                    <div class="submit-edit" v-else-if="isEditFamily">
                        <el-button @click="isEditFamily = false">取消</el-button>
                        <el-button @click="submitEditFamilyForm" type="primary">保存</el-button>
                    </div>
                    <div class="edit" v-else-if="!isAddingFamily && !isEditFamily">
                        <el-button type="primary" @click="isEditFamily = true">编辑</el-button>
                    </div>
                </el-form-item>
            </el-form>

            <div v-else class="no-family-info">
                <el-empty
                    description="暂无家庭信息"
                    :image-size="120"
                >
                    <template #description>
                        <p class="empty-description">您还没有添加家庭信息</p>
                        <p class="empty-sub-description">添加家庭信息可以帮助我们为您提供更精准的能耗分析</p>
                    </template>
                    <el-button type="primary" size="large" @click="isAddingFamily = true">
                        <el-icon><Plus /></el-icon>
                        添加家庭信息
                    </el-button>
                </el-empty>
            </div>
        </el-tab-pane>
    </el-tabs>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getCurrentUser, updateCurrentUser } from '@/api/user';
import { getFamilyInfo, createFamilyInfo, isFamilyInfoExist, updateFamilyInfo } from '@/api/family';
import { Plus, User, Message, Iphone, MapLocation } from '@element-plus/icons-vue'

const activeName = ref('first')
const form = ref(null)
const isEdit = ref(false)
const hasFamilyInfo = ref(false)
const isAddingFamily = ref(false)
const isEditFamily = ref(false)
const currentUser = ref({
    username: '',
    email: '',
    phone: '',
    avatar: ''
})

const currentUserFamilyInfo = ref({
    family_size: 1,
    house_area: null,
    location: '',
    building_age: null
})
const baseURL = import.meta.env.VITE_APP_API_BASE_URL

const rules = {
    email: [
        { required: true, message: '邮箱不能为空', trigger: 'change' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'change' }
    ],
    phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'change' }
    ]
}

const handleCancel = async () => {
    fetchCurrentUser()
    isEdit.value = false
}

const handleImageSuccess = (response) => {
    // console.log(response)
    currentUser.value.avatar = `${import.meta.env.VITE_APP_IMAGE_BASE_URL}/${response.file_name}`
}

const handleTabChange = () => {
    isAddingFamily.value = false
    isEditFamily.value = false
    isEdit.value = false
    fetchCurrentUser()
    if (hasFamilyInfo.value) {
        fetchFamilyInfo()
    } else {
        currentUserFamilyInfo.value = {
            family_size: 1,
            house_area: null,
            location: '',
            building_age: null
        }
    }
}

const submitEditForm = async () => {
    try {
        // console.log(currentUser.value)
        await form.value.validate()
        await updateCurrentUser(currentUser.value)
        isEdit.value = false
        fetchCurrentUser()
    } catch (error) {
        console.error(error)
    }
}

const submitAddFamilyForm = async () => {
    try {
        // console.log(currentUserFamilyInfo.value)
        await createFamilyInfo(currentUserFamilyInfo.value)
        ElMessage.success('添加家庭信息成功')
        hasFamilyInfo.value = true
        isAddingFamily.value = false
        fetchFamilyInfo()
    } catch (error) {
        console.error(error)
    }
} 

const submitEditFamilyForm = async () => {
    try {
        await updateFamilyInfo(currentUserFamilyInfo.value)
        ElMessage.success('编辑家庭信息成功')
        isEditFamily.value = false
        await fetchFamilyInfo()
    } catch (error) {
        console.error(error)
    }
}

const fetchCurrentUser = async () => {
    try {
        const res = await getCurrentUser()
        // console.log(res)
        currentUser.value = {
            username: res.username,
            email: res.email,
            phone: res.phone,
            avatar: res.avatar
        }
    } catch (error) {
        console.error(error)
    }
}

const fetchFamilyInfoExist = async () => {
    try {
        const res = await isFamilyInfoExist()
        // console.log(res)
        hasFamilyInfo.value = res
    } catch (error) {
        console.error(error)
    }
}

const fetchFamilyInfo = async () => {
    try {
        const res = await getFamilyInfo()
        // console.log(res)
        currentUserFamilyInfo.value = {
            family_size: res.family_size,
            house_area: res.house_area,
            location: res.location,
            building_age: res.building_age
        }
        hasFamilyInfo.value = true
    } catch (error) {
        console.error(error)
        hasFamilyInfo.value = false
    }
}

onMounted(async () => {
    await fetchFamilyInfoExist()
    await fetchCurrentUser()
    if (hasFamilyInfo.value === true) {
        await fetchFamilyInfo()
    }
    console.log('是否存在家庭信息:', hasFamilyInfo.value)
})
</script>

<style scoped>
.info-tabs {
    background-color: #fff;
    height: 100%;
    padding: 20px;
}

/* .info-tabs :deep() */

:deep(.el-tabs__item) {
  font-size: 18px !important;
  height: 50px;
  line-height: 50px;
  padding: 0 25px;
}

:deep(.el-tabs__header) {
    /* padding-left: 20px; */
}

:deep(.el-tabs__active-bar) {
    height: 2px;
}

.button-right :deep(.el-form-item__content) {
  display: flex;
  justify-content: flex-end;
  gap: 12px; /* 按钮之间的间距 */
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

:deep(.el-form-item__label) {
    font-weight: 500;
    font-size: large;
}
</style>