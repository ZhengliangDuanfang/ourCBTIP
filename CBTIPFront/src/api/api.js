import axios from "@/axios"


export function fetchDrugList() {
    // 注意：根据你的后端定义，这里使用了 POST 方法，
    // 通常获取列表会用 GET，如果后端是 GET，请修改此处。
    // 同时，假设后端 POST /drugs 不需要特定的请求体内容。
    return axios.post('/drugs', {})
  }
  
/**
 * 查询两种药物的相互作用
 * @param {string} drugId1 第一个药物的ID
 * @param {string} drugId2 第二个药物的ID
 * @returns Promise
 */
export function fetchDDI(drugId1, drugId2) {
return axios.post('/ddi', {
    drug_id_1: drugId1,
    drug_id_2: drugId2
})
}