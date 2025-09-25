import request from "@/api";
const prefix = "/tqtableqa/sysconfig";
// chat通用
export function GenerateStream(formData: any, userId: any) {
  return fetch(`api/nba/tableqa/chat`, {
    method: "POST",
    body: formData,
    headers: {
      "Content-Type": "application/json",
      userId,
    },
  });
}
export function Generate(query: any) {
  return request({
    url: `/nba/tableqa/chat`,
    method: "post",
    data: query,
  });
}
