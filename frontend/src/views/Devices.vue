<template>
    <div class="header">
        <h1 class="title">设备列表</h1>
        <div class="device-action">
            <el-select
                style="margin-right: 20px;"
                placeholder="设备类型"
                clearable
                v-model="filterForm.device_type"
                @change="handleSelect"
            >
                <el-option label="电力" value="electricity"></el-option>
                <el-option label="燃气" value="gas"></el-option>
                <el-option label="水资源" value="water"></el-option>
            </el-select>
            <el-button :icon="Plus" type="primary" @click="showCreateForm = true">新增</el-button>
        </div>
        <el-dialog
            title="新增设备"
            v-model="showCreateForm"
            width="600px"
        >
            <el-form
                ref="form"
                :rules="rules"
                :model="createForm"
                label-width="120px"
            >
                <el-form-item label="设备类型:" prop="device_type">
                    <el-select
                        v-model="createForm.device_type"
                    >
                        <el-option label="电力" value="electricity"></el-option>
                        <el-option label="燃气" value="gas"></el-option>
                        <el-option label="水资源" value="water"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="设备名称:" prop="name">
                    <el-input v-model="createForm.name"></el-input>
                </el-form-item>
                <el-form-item label="额定功率/流量:" prop="power_rating">
                    <el-input v-model.number="createForm.power_rating"></el-input>
                </el-form-item>
                <el-form-item label="日均使用(小时):" prop="usage_hours_per_day">
                    <el-input v-model.number="createForm.usage_hours_per_day"></el-input>
                </el-form-item>
                <el-form-item label="能耗等级:">
                    <el-input v-model="createForm.efficiency_rating"></el-input>
                </el-form-item>
                <el-form-item label="购买年份:" prop="purchase_year">
                    <el-input v-model.number="createForm.purchase_year"></el-input>
                </el-form-item>
                <el-form-item label="备注:">
                    <el-input v-model="createForm.notes" type="textarea"></el-input>
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="showCreateForm = false">取消</el-button>
                <el-button type="primary" @click="submitCreateForm">新增</el-button>
            </template>
        </el-dialog>
    </div>

    <div class="table-container">
        <el-table
            :data="tableData"
        >
            <el-table-column prop="name" label="设备名称"></el-table-column>
            <el-table-column label="设备类型" align="center">
                <template #default="scope">
                    <el-tag
                        v-if="scope.row.device_type === 'electricity'"
                        type="primary"
                        round
                    >电力</el-tag>

                    <el-tag
                        v-else-if="scope.row.device_type === 'gas'"
                        type="warning"
                        round
                    >燃气</el-tag>

                    <el-tag
                        v-else-if="scope.row.device_type === 'water'"
                        type="success"
                        round
                    >水资源</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="power_rating" label="功率/流量" align="center">
                <template #default="scope">
                    {{ scope.row.power_rating }}
                    <span v-if="scope.row.device_type === 'electricity'">W/h</span>
                    <span v-else-if="scope.row.device_type === 'gas'">m³/h</span>
                    <span v-else-if="scope.row.device_type === 'water'">L/h</span>
                </template>
            </el-table-column>
            <el-table-column prop="usage_hours_per_day" label="日均使用(小时)" align="center"></el-table-column>
            <el-table-column prop="efficiency_rating" label="能耗等级" align="center"></el-table-column>
            <el-table-column prop="purchase_year" label="购买年份" align="center"></el-table-column>
            <el-table-column prop="notes" label="备注" header-align="center" show-overflow-tooltip></el-table-column>
            <el-table-column label="操作" align="center">
                <template #default="scope">
                    <el-button
                        type="text"
                        :icon="Edit"
                        @click="handleEdit(scope.row)"
                    >编辑</el-button>
                    <el-button
                        type="text"
                        :icon="Delete"
                        @click="handleDelete(scope.row.id)"
                    >删除</el-button>
                    <el-button
                        type="text"
                        :icon="DocumentCopy"
                    >查看记录</el-button>
                </template>
            </el-table-column>
        </el-table>

        <div class="table-pagination">
            <el-pagination
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalCount"
                v-model:current-page="filterForm.page"
                v-model:page-size="filterForm.page_size"
                :page-sizes="[5, 10, 20, 30]"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            ></el-pagination>
        </div>

        <el-dialog
            title="编辑设备"
            v-model="showEditForm"
            width="600px"
        >
            <el-form
                ref="form"
                :rules="rules"
                :model="editForm"
                label-width="120px"
            >
                <el-form-item label="设备类型:" prop="device_type">
                    <el-select
                        v-model="editForm.device_type"
                    >
                        <el-option label="电力" value="electricity" />
                        <el-option label="燃气" value="gas" />
                        <el-option label="水资源" value="water" />
                    </el-select>
                </el-form-item>
                <el-form-item label="设备名称:" prop="name">
                    <el-input v-model="editForm.name"></el-input>
                </el-form-item>
                <el-form-item label="额定功率/流量:" prop="power_rating">
                    <el-input v-model.number="editForm.power_rating"></el-input>
                </el-form-item>
                <el-form-item label="日均使用(小时):" prop="usage_hours_per_day">
                    <el-input v-model.number="editForm.usage_hours_per_day"></el-input>
                </el-form-item>
                <el-form-item label="能耗等级:">
                    <el-input v-model="editForm.efficiency_rating"></el-input>
                </el-form-item>
                <el-form-item label="购买年份:" prop="purchase_year">
                    <el-input v-model.number="editForm.purchase_year"></el-input>
                </el-form-item>
                <el-form-item label="备注:">
                    <el-input v-model="editForm.notes" type="textarea"></el-input>
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="showEditForm = false">取消</el-button>
                <el-button type="primary" @click="submitEditForm">保存</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Plus, Edit, Delete, DocumentCopy } from '@element-plus/icons-vue'
import { getDevices, createDevice, getDeviceById, updateDevice, deleteDevice } from '@/api/device';

const form = ref(null)
const tableData = ref([])
const item = ref([])
const totalCount = ref(0)
const showCreateForm = ref(false)
const showEditForm = ref(false)
const filterForm = ref({
    device_type: null,
    page: 1,
    page_size: 5
})

const createForm = ref({
    device_type: '',
    name: '',
    power_rating: null,
    usage_hours_per_day: null,
    efficiency_rating: '',
    purchase_year: null,
    notes: ''
})

const editForm = ref({
    device_type: '',
    name: '',
    power_rating: null,
    usage_hours_per_day: null,
    efficiency_rating: '',
    purchase_year: null,
    notes: ''
})

const rules = {
    device_type: [
        { required: true, message: '请选择设备类型', trigger: 'blur' }
    ],
    name: [
        { required: true, message: '请输入设备名称', trigger: 'blur' }
    ],
    power_rating: [
        { required: true, message: '请输入额定功率/流量', trigger: 'blur' },
        { type: 'number', message: '额定功率/流量必须是数字' }
    ],
    usage_hours_per_day: [
        { required: true, message: '请输入日均使用时间(小时)', trigger: 'blur' },
        { type: 'number', message: '日均使用时间必须是数字' }
    ],
    purchase_year: [
        { type: 'number', message: '购买年份必须是数字' }
    ]
}

const handleSelect = () => {
    fetchDevices(filterForm.value)
}

const handleSizeChange = () => {
    filterForm.value.page = 1
    fetchDevices(filterForm.value)
}

const handleCurrentChange = () => {
    fetchDevices(filterForm.value)
}

const handleEdit = async (row) => {
    try {
        showEditForm.value = true
        // 根据设备ID查询设备详情
        const res = await getDeviceById(row.id)
        // console.log(res)
        item.value = res
        // console.log(item.value)
        editForm.value = {
            device_type: res.device_type,
            name: res.name,
            power_rating: res.power_rating,
            usage_hours_per_day: res.usage_hours_per_day,
            efficiency_rating: res.efficiency_rating,
            purchase_year: res.purchase_year,
            notes: res.notes
        }
        // console.log(editForm.value)
    } catch (error) {
        console.error(error)
    }
}

const handleDelete = async (bill_id) => {
    try {
        // 弹出确认对话框
        await ElMessageBox.confirm(
            '此操作将永久删除该设备，删除后无法恢复',
            '确认删除',
            {
                confirmButtonText: '确认删除',
                cancelButtonText: '取消',
                type: 'warning'
            }
        )
        await deleteDevice(bill_id)
        ElMessage.success('设备删除成功')

        fetchDevices(filterForm.value)
    } catch (error) {
        if (error === 'cancel') {
            ElMessage.info('已取消删除')
        } else {
            console.error('删除失败:', error)
            ElMessage.error('设备删除失败，请稍后重试')
        }
    }
}

const submitCreateForm = async () => {
    try {
        await form.value.validate()
        const res = await createDevice(createForm.value)
        console.log(res)
        ElMessage.success('新增设备成功')
        showCreateForm.value = false
        await fetchDevices(filterForm.value)
    } catch (error) {
        console.error(error)
    }
}

const submitEditForm = async () => {
    try {
        await form.value.validate()
        // console.log(item.value)
        await updateDevice(item.value.id, editForm.value)
        ElMessage.success('编辑设备信息成功')
        showEditForm.value = false
        await fetchDevices(filterForm.value)
    } catch (error) {
        console.error(error)
    }
}

const fetchDevices = async (filterData) => {
    try {
        const res = await getDevices(filterData)
        // console.log(res)
        tableData.value = res.items
        totalCount.value = res.total
    } catch (error) {
        console.error(error)
    }
}

onMounted(() => {
    fetchDevices(filterForm.value)
})
</script>

<style scoped>
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 10px 0;
}

.title {
    font-size: clamp(16px, 2vw, 24px)
}

@media (max-width: 768px) {
    .title {
        font-size: 18px;
    }
}

@media (min-width: 769px) and (max-width: 1200px) {
    .title {
        font-size: 20px;
    }
}

@media (min-width: 1201px) {
    .title {
        font-size: 24px;
    }
}

.device-action {
    display: flex;
    width: 240px;
}

.table-container {
    margin-top: 25px;
}

.table-pagination {
    margin-top: 10px;
}
</style>