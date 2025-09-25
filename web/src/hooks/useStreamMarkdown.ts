import { useEffect, useState } from "react";
import { marked } from "marked";

export const useStreamMarkdown = (stream: any) => {
  const [markdown, setMarkdown] = useState("");

  useEffect(() => {
    if(stream || stream === "") {
      setMarkdown(stream); // 这里假设数据是字符串，可以直接拼接
    }
  }, [stream]);

  // 将 Markdown 转换为 HTML
  const htmlContent = marked(markdown);
  return { markdown, htmlContent };
};
