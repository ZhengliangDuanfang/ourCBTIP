<template>
    <div>
        <el-result icon="error" title="Error Tip" sub-title="Please follow the instructions">
            <template #extra>
                <el-button type="primary" @click="$router.push('/login')">Back</el-button>
            </template>
        </el-result>
    </div>
</template>