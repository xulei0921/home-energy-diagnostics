<template>
    <div class="header">
        <h1 class="title">账单列表</h1>
        <div class="bill-action">
            <el-date-picker
                style="flex: 1;"
                v-model="filterForm.bill_date"
                type="month"
                placeholder="账单日期"
                clearable
                value-format="YYYY-MM-DD"
                @change="handleDateChange"
            ></el-date-picker>
            <el-select
                v-model="filterForm.bill_type"
                placeholder="账单类型"
                clearable
                style="margin: 0 20px; flex: 1;"
                @change="handleSelect"
            >
                <el-option label="电力" value="electricity"></el-option>
                <el-option label="燃气" value="gas"></el-option>
                <el-option label="水资源" value="water"></el-option>
            </el-select>
            <el-button :icon="Plus" type="primary" @click="showCreateForm = true">添加</el-button>
        </div>
        <el-dialog
            title="添加账单"
            v-model="showCreateForm"
            width="600px"
        >
            <el-form
                ref="form"
                :rules="rules"
                :model="createForm"
                label-width="85px"
            >
                <el-form-item label="账单日期:" prop="bill_date">
                    <el-date-picker
                        style="width: 150px;"
                        v-model="createForm.bill_date"
                        type="month"
                        placeholder="请选择账单日期"
                        value-format="YYYY-MM-DD"
                    ></el-date-picker>
                </el-form-item>
                <el-form-item label="账单类型:" prop="bill_type">
                    <el-select
                        v-model="createForm.bill_type"
                        style="width: 150px;"
                    >
                        <el-option label="电力" value="electricity"></el-option>
                        <el-option label="燃气" value="gas"></el-option>
                        <el-option label="水资源" value="water"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="总金额:" prop="amount">
                    <el-input v-model.number="createForm.amount"></el-input>
                </el-form-item>
                <el-form-item label="用量:" prop="usage">
                    <el-input v-model.number="createForm.usage"></el-input>
                </el-form-item>
                <el-form-item label="单价:" prop="unit_price">
                    <el-input v-model.number="createForm.unit_price"></el-input>
                </el-form-item>
                <el-form-item label="备注:">
                    <el-input type="textarea" v-model="createForm.notes"></el-input>
                </el-form-item>
            </el-form>

            <template #footer>
                <el-button @click="showCreateForm = false">取消</el-button>
                <el-button type="primary" @click="submitCreateForm">添加</el-button>
            </template>
        </el-dialog>
    </div>

    <div class="table-container">
        <el-table :data="tableData">
            <el-table-column prop="bill_date" label="账单日期"></el-table-column>
            <el-table-column label="账单类型">
                <template #default="scope">
                    <div class="bill-type-container">
                        <!-- 动态渲染图标 -->
                        <i :class="getIconClass(scope.row.bill_type)"></i>
                        <!-- 动态渲染文字 -->
                        <span class="bill-type-text">
                            {{ getBillTypeText(scope.row.bill_type) }}
                        </span>
                    </div>
                </template>
            </el-table-column>
            <el-table-column prop="usage" label="用量" align="center">
                <template #default="scope">
                    {{ scope.row.usage }}
                    <span v-if="scope.row.bill_type === 'electricity'">Kwh</span>
                    <span v-else-if="scope.row.bill_type === 'gas'">m³</span>
                    <span v-else-if="scope.row.bill_type === 'water'">m³</span>
                </template>
            </el-table-column>
            <el-table-column prop="unit_price" label="单价" align="center">
                <template #default="scope">
                    ￥{{ scope.row.unit_price }}
                    <span v-if="scope.row.bill_type === 'electricity'">/Kwh</span>
                    <span v-else-if="scope.row.bill_type === 'gas'">/m³</span>
                    <span v-else-if="scope.row.bill_type === 'water'">/m³</span>
                </template>
            </el-table-column>
            <el-table-column prop="amount" label="总金额" align="center">
                <template #default="scope">
                    <span class="bold-text">￥{{ scope.row.amount }}</span>
                </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" header-align="center"></el-table-column>
            <el-table-column label="操作" header-align="center" align="center">
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
            title="编辑账单"
            v-model="showEditForm"
            width="600px"
        >
            <el-form
                ref="form"
                :rules="rules"
                :model="formModel"
                label-width="85px"
            >
                <el-form-item label="账单日期:" prop="bill_date">
                    <el-date-picker
                        style="width: 150px;"
                        v-model="formModel.bill_date"
                        type="month"
                        placeholder="请选择账单日期"
                        value-format="YYYY-MM-DD"
                    ></el-date-picker>
                </el-form-item>
                <el-form-item label="账单类型:" prop="bill_type">
                    <el-select
                    style="width: 150px;"
                        v-model="formModel.bill_type"
                    >
                        <el-option label="电力" value="electricity"></el-option>
                        <el-option label="燃气" value="gas"></el-option>
                        <el-option label="水资源" value="water"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="用量:" prop="usage">
                    <el-input
                        v-model.number="formModel.usage"
                    ></el-input>
                </el-form-item>
                <el-form-item label="单价:" prop="unit_price">
                    <el-input
                        v-model.number="formModel.unit_price"
                    ></el-input>
                </el-form-item>
                <el-form-item label="总金额:" prop="amount">
                    <el-input
                        v-model.number="formModel.amount"
                    ></el-input>
                </el-form-item>
                <el-form-item label="备注:">
                    <el-input
                        v-model="formModel.notes"
                        type="textarea"
                    ></el-input>
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
import { ref, onMounted, nextTick, watch } from 'vue';
import { getBills, getBillById, updateBill, deleteBill, createBill } from '@/api/bill';
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const filterForm = ref({
    bill_type: null,
    bill_date: null,
    page: 1,
    page_size: 5
})

const createForm = ref({
    bill_type: '',
    bill_date: '',
    amount: null,
    usage: null,
    unit_price: null,
    notes: ''
})

const formModel = ref({
    bill_type: '',
    bill_date: '',
    amount: 0,
    usage: 0,
    unit_price: 0,
    notes: ''
})

const form = ref(null)
const item = ref([])
const totalCount = ref(0)
const tableData = ref([])
const showEditForm = ref(false)
const showCreateForm = ref(false)

const rules = {
    bill_date: [
        { required: true, message: '请选择账单日期', trigger: 'blur' }
    ],
    bill_type: [
        { required: true, message: '请选择账单类型', trigger: 'blur' }
    ],
    usage: [
        { required: true, message: '请输入能耗用量', trigger: 'blur' },
        { type: 'number', message: '能耗用量必须是数字' }
    ],
    unit_price: [
        { required: true, message: '请输入能耗单价', trigger: 'blur' },
        { type: 'number', message: '能耗单价必须是数字' }
    ],
    amount: [
        { required: true, message: '请输入账单总金额', trigger: 'blur' },
        { type: 'number', message: '账单总金额必须是数字' }
    ]
}

const getIconClass = (billType) => {
    switch(billType) {
        case 'electricity':
            return 'iconfont icon-dian';
        case 'gas':
            return 'iconfont icon-ranqi';
        case 'water':
            return 'iconfont icon-water'
        default:
            return '';
    } 
}

const getBillTypeText = (billType) => {
    switch(billType) {
        case 'electricity':
            return '电费';
        case 'gas':
            return '燃气费';
        case 'water':
            return '水费';
        default:
            return '未知类型';
    }
}

// 当分页器页面大小改变时
const handleSizeChange = () => {
    filterForm.value.page = 1
    fetchBills(filterForm.value)
}

// 当分页器页码改变时
const handleCurrentChange = () => {
    fetchBills(filterForm.value)
}

const handleSelect = () => {
    fetchBills(filterForm.value)
}

const handleDateChange = () => {
    // console.log('测试筛选日期触发效果')
    fetchBills(filterForm.value)
}

// 打开编辑弹窗，并获取点击的账单信息
const handleEdit = async (row) => {
    try {
        showEditForm.value = true
        // 根据账单ID查询账单详情
        const res = await getBillById(row.id)
        item.value = res
        // console.log(res)
        formModel.value = {
            bill_date: res.bill_date,
            bill_type: res.bill_type,
            usage: res.usage,
            unit_price: res.unit_price,
            amount: res.amount,
            notes: res.notes
        }
        // console.log(formModel.value)
        // console.log(typeof(formModel.value.amount))
    } catch (error) {
        ElMessage.error('获取账单详情失败')
        console.error(error)
    }
}

// 提交添加账单请求
const submitCreateForm = async () => {
    try {
        // console.log(createForm.value)
        await form.value.validate()
        const res = await createBill(createForm.value)
        ElMessage.success('添加账单成功')
        showCreateForm.value = false
        await fetchBills()
    } catch (error) {
        // ElMessage.error('添加账单失败，请稍后重试')
        console.log(error)
    }
}

// 提交编辑账单请求
const submitEditForm = async () => {
    try {
        // console.log(formModel.value)
        await form.value.validate()
        await updateBill(item.value.id, formModel.value)
        ElMessage.success('编辑账单信息成功')
        showEditForm.value = false
        await nextTick()
        await fetchBills()
    } catch (error) {
        // ElMessage.error('编辑账单信息失败，请稍后重试')
        console.error(error)
    }
}

// 提交删除账单请求
const handleDelete = async (bill_id) => {
    try {
        // 弹出确认对话框
        await ElMessageBox.confirm(
            '此操作将永久删除该账单，删除后无法恢复',  // 提示信息
            '确认删除',  // 对话框标题
            {
                confirmButtonText: '确认删除', // 确认按钮文本
                cancelButtonText: '取消',  // 取消按钮文本
                type: 'warning'  // 对话框类型，用于显示不同的图标
            }
        )
        // 如果用户点击了“确认删除”，则执行删除操作
        await deleteBill(bill_id)
        ElMessage.success('账单删除成功')

        // 更新表格数据
        fetchBills()
    } catch (error) {
        // 如果用户点击了“取消”，则会进入这里
        // ElMessageBox.confirm 会在用户取消时抛出一个错误，错误信息为 'cancel'
        if (error === 'cancel') {
            ElMessage.info('已取消删除')
        } else {
            console.error('删除失败:', error)
            ElMessage.error('账单删除失败，请稍后重试')
        }
    }
}

// 获取账单列表
const fetchBills = async () => {
    try {
        const res = await getBills(filterForm.value)
        // console.log(res)
        tableData.value = res.items
        totalCount.value = res.total
    } catch (error) {
        console.error(error)
    }
}

watch(showCreateForm, () => {
    // console.log('监听成功')
    createForm.value = {
        bill_type: '',
        bill_date: '',
        amount: null,
        usage: null,
        unit_price: null,
        notes: ''
    }
})

onMounted(() => {
    fetchBills()
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
    font-size: clamp(16px, 2vw, 24px);
}

/* 在小屏幕上保持适中大小 */
@media (max-width: 768px) {
    .title {
        font-size: 18px;
    }
}

/* 在中等屏幕上稍微增大 */
@media (min-width: 769px) and (max-width: 1200px) {
    .title {
        font-size: 20px;
    }
}

/* 在大屏幕上使用更大字体 */
@media (min-width: 1201px) {
    .title {
        font-size: 24px;
    }
}

.bill-action {
    display: flex;
    width: 400px;
}

.table-container {
    margin-top: 25px;
}

.table-pagination {
    margin-top: 10px;
}

.icon-dian {
    display: inline-block;
    width: 32px;
    height: 32px;
    background-color: #DBEAFE;
    border-radius: 16px;
    color: #409EFF;
    font-size: 20px;
    text-align: center;
    line-height: 32px;
}

.icon-ranqi {
    display: inline-block;
    width: 32px;
    height: 32px;
    background-color: #FFEDD5;
    border-radius: 16px;
    color: #E6A23C;
    font-size: 17px;
    text-align: center;
    line-height: 32px;
}

.icon-water {
    display: inline-block;
    width: 32px;
    height: 32px;
    /* background-color: #DBEAFE; */
    background-color: #8FDAEB;
    border-radius: 16px;
    /* color: #409EFF; */
    color: #F0F9EB;
    font-size: 18px;
    text-align: center;
    line-height: 32px;
}

.bill-type-text {
    display: inline-block;
    margin-left: 7px;
    align-items: center;
    /* font-weight: 500; */
    color: black;
}

/* :deep(.el-table th.el-table__cell) {
  text-align: center;
} */

 .bold-text {
    /* font-weight: bold; */
    color: black;
 }
</style>