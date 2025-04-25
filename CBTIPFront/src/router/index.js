import {
    createRouter,
    createWebHistory
} from 'vue-router'


import DDI from "@/views/DDI.vue"
import NotFount from "@/views/404.vue"


const routes = [
    {
        path: '/',
        redirect: '/ddi'  // 重定向到 /ddi
    },
    {
        path: '/ddi',
        component: DDI,
        meta: {
            title: 'DDI检测'
        }
    },
    {
        path: '/:pathMatch(.*)',
        name: 'NotFound',
        component: NotFount
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router