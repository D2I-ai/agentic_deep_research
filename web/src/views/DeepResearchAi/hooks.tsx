import { useEffect, useState } from "react";
import botImg from "@/assets/img/bot.jpg";
import { UserOutlined } from "@ant-design/icons";
interface ChatMessage {
  from: "user" | "bot";
  text: string;
  sql?: any;
  subTable?: any;
}
type TransformedMessage = {
  user: string;
  bot: string;
  role: "user" | "bot";
  message: any;
};
export const useIndex = () => {
  const BotAvatar = (name?: string) => {
    return (
      <div className="bot-avatar">
        <img src={botImg} alt="Bot" />
        {name}
      </div>
    );
  };

  const UserAvatar = () => {
    return (
      <div className="user-avatar">
        <UserOutlined
          style={{ fontSize: "22px", marginTop: "3px", color: "#624aff" }}
        />
      </div>
    );
  };
  const transformMessages = (messagesArray: any[]): TransformedMessage[] => {
    const transformed: any[] = [];

    // 通过索引来迭代，可以检查连续的消息
    for (let i = 0; i < messagesArray.length - 1; i++) {
      const currentMessage = messagesArray[i];
      const nextMessage = messagesArray[i + 1];

      if (currentMessage.type == "error" || nextMessage.type == "error") {
        continue;
      }
      // 确保当前消息来自 "user"，下一条消息来自 "bot"
      if (
        currentMessage.from === "user" &&
        nextMessage &&
        nextMessage.from === "bot"
      ) {
        transformed.push({
          user: currentMessage.text,
          bot: nextMessage.text,
        });
        i++; // 跳过下一条消息
      }
    }

    return transformed;
  };
  const splitJson = (text: string) => {
    // 使用 '\0' 分割新数据片段

    // const jsonStrings = text.split(/\0+/).filter(Boolean);
    const jsonStrings = text.split("\\**").filter(Boolean);
    let newText = "";
    let subTable: any;
    let end: any;
    let sql: any;
    let queryResult: any;
    let img: any;
    let lins: any = { end: "", sql: "", img: "" };
    // 解析每个 JSON 字符串并提取 "output" 字段

    jsonStrings.map((jsonStr) => {
      try {
        const trimmedJsonStr = jsonStr.trim();

        if (trimmedJsonStr) {
          const jsonObj = JSON.parse(trimmedJsonStr);
          if (jsonObj.output != undefined) {
            newText += jsonObj.output;
          }
        }
      } catch (error) {
        // console.error("解析 JSON 字符串时发生错误:", error);
        // return '';
      }
    });

    return { text: newText, subTable, sql, queryResult, img };
  };

  return {
    BotAvatar,
    UserAvatar,
    transformMessages,
    splitJson,
  };
};
