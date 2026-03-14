// 本地开发: NEXT_PUBLIC_API_URL 未设置 → 用 localhost:8000
// Docker部署: NEXT_PUBLIC_API_URL='' → 用相对路径 (Nginx 代理)
const envUrl = process.env.NEXT_PUBLIC_API_URL;
export const API_BASE_URL = envUrl !== undefined ? envUrl : 'http://localhost:8000';
