import axios from "axios";
import { store } from "../redux";
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 3000000,
  headers: {
    "Content-Type": "application/json",
  },
});
request.interceptors.request.use(
  (config) => {
    const user = store.getState().user;
    if (user.userId) {
      // config.headers.Authorization = "Bearer " + user.token;
      config.headers.userId = user.userId;
    }

    // 追加时间戳，防止GET请求缓存
    if (config.method?.toUpperCase() === "GET") {
      config.params = { ...config.params, t: new Date().getTime() };
    }

    config.data = { ...config.data};

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      // 请求已发出，但服务器响应的状态码不在 2xx 范围内
      console.error("The request was made 2xx", error.response.data);
    } else if (error.request) {
      // 请求已经发出，但没有收到响应
      console.error(
        "The request was made but no response was received",
        error.request
      );
    } else {
      // 发送请求时出了点问题
      // console.error("Error", error.message);
    }
    return Promise.reject(error);
  }
);

export default request;
