import request from "@/api";
// chat通用
export function GenerateStream(formData: any, userId: any) {
  return fetch(`api/deepresearch/agent/chat`, {
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
    url: `/deepresearch/agent/chat`,
    method: "post",
    data: query,
  });
}

export function getStatus(query?: any) {
  return request({
    url: `/deepresearch/thinking/status`,
    method: "post",
    data: query,
  });
}
