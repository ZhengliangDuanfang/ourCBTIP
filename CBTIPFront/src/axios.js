import axios from 'axios'
import { notify } from '@/composables/utils'
// import { useCookies } from '@vueuse/integrations/useCookies';

const service = axios.create({
  baseURL: 'http://127.0.0.1:5000'
})

// 添加响应拦截器
service.interceptors.response.use(function (response) {
  return response.data;
}, function (error) {
  notify('error', error.response.data.message)
  return Promise.reject(error);
});

export default service