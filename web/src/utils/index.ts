
// 获取指定名称的 Cookie 值
export const getCookie = (name: string): string | undefined => {
  const cookieArray = document.cookie.split(';'); // 将 Cookie 字符串拆分为数组
  for (let cookie of cookieArray) {
    const [cookieName, cookieValue] = cookie.trim().split('='); // 拆分 Cookie 的名称和值
    
    if (cookieName === name) {
      return decodeURIComponent(cookieValue); // 如果找到匹配的 Cookie，返回其值
    }
  }
  return ''; // 如果没有找到，返回 undefined
};
