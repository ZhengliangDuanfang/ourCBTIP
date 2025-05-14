import { ElNotification } from 'element-plus'


export function notify(type, message) {
  ElNotification({
    message: message,
    type: type,
    duration: 1200
  })
}