/**
 * API 配置 - 自动检测后端地址
 */

const getBaseURL = () => {
  // 开发环境使用代理
  if (import.meta.env.DEV) {
    return ''
  }
  // 生产环境：动态获取当前主机
  const protocol = window.location.protocol
  const host = window.location.host
  return `${protocol}//${host}`
}

export const apiConfig = {
  baseURL: getBaseURL(),
  timeout: 30000
}

export default apiConfig
