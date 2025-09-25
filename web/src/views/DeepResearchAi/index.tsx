import React, { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Input, message, Typography, Switch, Button, List, Select } from "antd";
import {
  ArrowDownOutlined,
  RetweetOutlined,
  SendOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { GenerateStream, Generate, getStatus } from "@/api/deepAgent.ts";
import { setDbId, setDbTabs } from "@/redux/modules/common/action";
import Loading from "@/components/Loading";
import ItemModel from "./ItemModel/index.tsx";
import { useSelector, useDispatch } from "react-redux";
import { useTranslation } from "react-i18next";
import "@/styles/chat.scss";
import StepContent from "./StepContent.tsx";
import { useIndex } from "./hooks.tsx";
import InferenceSidebar from "./InferenceSidebar";
import ExportButton from "./ExportButton";
export interface ChatMessage {
  from: "user" | "bot" | "deep";
  text?: any;
  info?: any;
  subTable?: any;
  stepCurrent?: number;
  stepItems?: any[];
  content?: any;
}
interface FetchBotResponseParams {
  userInput: string;
}
type TransformedMessage = {
  user: string;
  bot: string;
};
const { TextArea } = Input;

const helps = "Hey 😊, I'm your DeepResearch assistant.";

const Dash: React.FC = () => {
  const { t } = useTranslation();
  const [items, setItems] = useState<any>([]);
  const errorText = t("index.errorText");
  const common = useSelector((state: any) => state.common);
  const [model, setModel] = useState<string>("qwen-max-2025-01-25");
  const [sessionId, setSessionId] = useState<string>(
    "userid_" + new Date().getTime()
  );
  const user = useSelector((state: any) => state.user);
  const dispatch = useDispatch();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const isMounted = useRef(true);
  const navigate = useNavigate();
  const [userInput, setUserInput] = useState<any>("");
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const containerRef = useRef<any>(null);
  const headerRef = useRef<any>(null);
  const textAreaRef = useRef<any>(null);
  const [isEnd, setIsEnd] = useState<boolean>(false);
  const [isStep, setIsStep] = useState<boolean>(false);
  // 机器人loading状态
  const [isBotThinking, setIsBotThinking] = useState<boolean>(false);
  const [isChatEnd, setIsChatEnd] = useState<boolean>(true);
  const [messageApi, contextHolder] = message.useMessage();
  const [stream, setStream] = useState<boolean>(true);
  const [isComposing, setIsComposing] = useState<boolean>(false);
  const inputRef = useRef<any>(null);
  const { BotAvatar, UserAvatar, transformMessages, splitJson } = useIndex();

  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const [openModal, setOpenModal] = useState<boolean>(false);
  const [showSlider, setShowSlider] = useState<boolean>(false);
  const pdfRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    if (containerRef.current) {
      window.requestAnimationFrame(() => {
        // messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        containerRef.current.scrollTop =
          containerRef.current.scrollHeight - containerRef.current.clientHeight;
      });
    }
  };
  // 监听滚动事件，判断是否在底部
  const handleScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    // 允许 5px 误差
    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight <= 5;
    // console.log(
    //   "isAtBottom",
    //   isAtBottom,
    //   el.scrollHeight,
    //   el.scrollTop,
    //   el.clientHeight
    // );
    setAutoScroll(isAtBottom);
  };
  useEffect(() => {
    clear();
  }, [location]);
  useEffect(() => {
    dispatch(
      setDbTabs([
        {
          id: "m72",
          name: "DeepResearch",
        },
      ])
    );
    setMessages([{ from: "bot", text: helps }]);
    isMounted.current = true;
    return () => {
      // 可选的清理工作，如重置状态
      setIsStep(false);
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (autoScroll) {
      scrollToBottom();
    }
    pdfRefs.current = Array(messages.length)
      .fill(null)
      .map((_, i) => pdfRefs.current[i] || null);
  }, [messages]);
  // 参数
  const getQuery = (userInput: string) => {
    console.log(messages, "query");
    let history: Array<TransformedMessage> = transformMessages(messages);
    return {
      input: userInput,
      history: [],
      stream,
      user: sessionId,
      increase: false,
      model_name: model,
    };
  };

  // 流式请求
  const fetchBotResponseStream = async ({
    userInput,
  }: FetchBotResponseParams): Promise<any> => {
    return new Promise(async (resolve, reject) => {
      try {
        const response = await GenerateStream(
          JSON.stringify(getQuery(userInput)),
          user.userId
        );

        // 检查浏览器是否支持流
        if (!response.body) {
          reject();
          throw new Error("ReadableStream not supported in this browser.");
        }
        if (!response.ok) {
          console.log("error");
          setIsStep(false);
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const reader = response.body.getReader();
        let receivedLength = 0; // 接收到的字节数
        // Stream 数据处理
        let lastOutput = "";
        let buffer = "";
        setIsBotThinking(false);
        setIsChatEnd(false);

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            // 流数据结束，退出循环
            scrollToBottom();
            setIsChatEnd(true);
            resolve("");
            setMessages((prevMessages) => {
              if (prevMessages.length === 0) {
                return prevMessages;
              }
              // 更新消息数组
              const updatedMessages = [...prevMessages];
              updatedMessages[updatedMessages.length - 1].stepCurrent = 1;
              return updatedMessages; // 返回新的消息数组
            });
            break;
          }
          // 处理每一块流数据
          const textChunk = new TextDecoder().decode(value, { stream: true });
          receivedLength += value.length;
          buffer += textChunk;
          let splitValue = splitJson(buffer);

          let { text } = splitValue;
          let newContent = text.replace(lastOutput, "");
          if (newContent) {
            setMessages((prevMessages) => {
              const newMessages: any[] = [...prevMessages];
              for (let i = newMessages.length - 1; i >= 0; i--) {
                if (newMessages[i].from == "bot") {
                  if (newContent.trim() !== "" || newContent.length > 1) {
                    newMessages[i].content = newContent;
                    newMessages[i].text = "";
                  } else {
                  }
                  break;
                }
              }
              return newMessages;
            });
          }
        }

        console.log(`Received ${receivedLength} bytes of data`);
      } catch (error) {
        setIsChatEnd(true);
        setIsBotThinking(false);
        isMounted.current = false;
        setMessages((prevMessages) => {
          if (prevMessages.length === 0) {
            return prevMessages;
          }
          const updatedMessages = [...prevMessages];
          updatedMessages[updatedMessages.length - 1].text = errorText;
          return updatedMessages; // 返回新的消息数组
        });

        console.error("Stream fetching error:", error);
      }
    });
  };

  // 正常请求
  const fetchBotResponse = async ({
    userInput,
  }: FetchBotResponseParams): Promise<any> => {
    return new Promise((resolve, reject) => {
      Generate(getQuery(userInput))
        .then((res: any) => {
          console.log(res, "res");
          if (res.code == "200") {
            let text = res.data;
            // setIsEnd(res.end);
            setIsBotThinking(false);
            console.log(text, "text");
            setMessages((prevMessages) => {
              const updatedMessages = [...prevMessages];
              updatedMessages[updatedMessages.length - 1].content = text;
              updatedMessages[updatedMessages.length - 1].text = "";
              updatedMessages[updatedMessages.length - 1].stepCurrent = 1;
              return updatedMessages;
            });

            console.log(textAreaRef.current);
            setIsChatEnd(true);

            setTimeout(() => {
              scrollToBottom();
              if (textAreaRef.current) {
                textAreaRef.current.focus();
              }
            }, 200);
            resolve({ text });
          }
        })
        .catch(() => {
          isMounted.current = false;
          console.log("catch");
          setIsBotThinking(false);
          setIsStep(false);
          setIsChatEnd(true);
          setMessages((prevMessages) => {
            if (prevMessages.length === 0) {
              return prevMessages;
            }
            const updatedMessages = [...prevMessages];
            updatedMessages[updatedMessages.length - 1].text = errorText;
            return updatedMessages; // 返回新的消息数组
          });

          setTimeout(() => {
            if (textAreaRef.current) {
              textAreaRef.current.focus();
            }
          }, 200);
          reject("");
        });
    });
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // 检查是否按下了 Command (针对 Mac 用户) 或 Ctrl (针对 Windows/Linux 用户) 和 Enter 键
    if (e.key === "Enter" && !isComposing) {
      // 在这里执行发送消息的逻辑
      if (!isChatEnd || isEnd) return;
      sendMessage();
      e.preventDefault(); // 防止默认行为，例如换行
    }
  };
  const handleSend = (e: any) => {
    if (userInput.trim() === "") return;
    // 在这里执行发送消息的逻辑
    sendMessage();
    e.preventDefault(); // 防止默认行为，例如换行
  };
  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  const sendMessage = async () => {
    if (!userInput.trim()) {
      setUserInput(null);
      messageApi.open({
        type: "info",
        content: "请输入内容",
      });

      return;
    }
    if (!isChatEnd || isEnd) return;
    setIsStep(true);
    setIsChatEnd(false);
    const newMessages: Array<any> = [
      ...messages,
      {
        from: "user",
        text: userInput,
      },
    ];
    setMessages(newMessages);
    getChat(userInput);
    handleStep(userInput);
    scrollToBottom();
  };

  let getChat = (input: string) => {
    if (stream) {
      fetchBotResponseStream({ userInput: input });
    } else {
      fetchBotResponse({ userInput: input });
    }
    setUserInput(null);
  };

  let chatEnd = (isEnd: boolean) => {
    setIsChatEnd(isEnd);
    scrollToBottom();
  };
  let clear = () => {
    setMessages([{ from: "bot", text: helps }]);
    setItems([]);
    setShowSlider(false);
    setSessionId("userid_" + new Date().getTime());
  };
  const onCreate = (list: any) => {
    dispatch(setDbTabs(list));
    setOpenModal(false);
  };
  const onCancel = () => {
    setOpenModal(false);
  };
  // new todo

  const handleStep = async (userInput: any) => {
    const botMessage: any = {
      from: "bot",
      text: t("data.waitText"),
      content: t("data.waitText"),
      exportName: userInput,
    };
    // 添加机器人的消息
    setMessages((prevMessages) => [...prevMessages, botMessage]);
    setItems([
      {
        title: "Analysis the user query ...",
        func_name: "",
        status: {
          WebSearch: "",
        },
        content: "",
        detailed_status: {},
        type: "",
      },
    ]);
    setShowSlider(true);
    setTimeout(async () => {
      await updateStep(userInput, botMessage);
    }, 2000);
  };
  const updateStep = async (userInput: any, botMessage: any) => {
    // 获取当前状态
    const res: any = await getStatus({
      topic: userInput,
      userid: sessionId,
    });

    // 如果数据中包含404错误码
    if (res.code !== "200") {
    } else {
      // 使用processData函数处理响应数据
      const data: any = processData(res.data);

      // 添加数据并检查type和content
      let latestData;
      setItems((prevItems: any[]) => {
        // 检查新数据和数组中最后一个数据的type
        if (prevItems.length > 0) {
          const lastItem = prevItems[prevItems.length - 1];
          if (
            lastItem.funcName == data?.funcName &&
            data.title == lastItem.title &&
            data.content == lastItem.content
          ) {
            // 新数据的type与最后一个数据的type一致，且新数据的content为空，不添加
            return prevItems;
          }
        }
        // 否则，添加新数据
        latestData = data; // 保存数据以便后续使用
        return [...prevItems, data];
      });

      // 确保我们使用了最新的data进行后续操作
      const useData: any = latestData || data;

      const func_name = useData.funcName;
      const text = useData?.title;
      const content = useData?.content;
      botMessage.text = text;
      const result = func_name?.indexOf("Generating final answer") > -1;

      if (!result) {
        botMessage.content = content;
      } else {
        botMessage.content = content;
      }
      botMessage.type = useData.type;

      // 更新消息数组
      setMessages((prevMessages) => {
        if (prevMessages.length === 0) {
          return prevMessages;
        }
        // 更新消息数组
        const updatedMessages = [...prevMessages];
        updatedMessages[updatedMessages.length - 1] = botMessage; // 更新最后一条消息
        return updatedMessages; // 返回新的消息数组
      });

      // 等待一段时间后继续请求新的状态
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // 判断是否结束
      if (result) {
        console.log("Report generated, completing task.");
        // 可以在这里添加结束逻辑
      } else {
        if (isMounted.current) {
          // 继续递归调用
          await updateStep(userInput, botMessage);
        }
      }
    }
  };

  const onStepChange = (value: number, index: number) => {
    console.log("onChange:", index);
    setMessages((prevMessages) => {
      // 创建新的消息数组
      const updatedMessages = [...prevMessages];
      updatedMessages[index].stepCurrent = value; // 更新最后一条消息
      return updatedMessages; // 返回新的消息数组
    });
  };
  function processData(item: any): any[] {
    let result: any[] = [];

    const { detailed_status, status_desc } = item;

    // 从 status 中提取 title，根据需要提取某个特定字段
    const title = status_desc;
    let func_name = status_desc;

    if (detailed_status?.url2favicon && detailed_status?.websearch_queries) {
      let d = Object.entries(detailed_status.url2favicon).map(([url, src]) => {
        return { url, src };
      });

      result.push({
        title: title, // 使用 status 中的值作为标题
        content: {
          list: detailed_status?.websearch_queries || [],
          urlList: d,
        },
        type: "url",
        funcName: func_name, // 保留 func_name
      });
    }

    if (detailed_status?.search_query) {
      result.push({
        title: title, // 使用 status 中的值作为标题
        content: detailed_status.search_query,
        type: "content",
        funcName: func_name, // 保留 func_name
      });
    }
    if (detailed_status?.search_plan) {
      result.push({
        title: title, // 使用 status 中的值作为标题
        content: detailed_status.search_plan,
        type: "content",
        funcName: func_name, // 保留 func_name
      });
    }
    if (
      detailed_status?.thinking_content ||
      detailed_status?.thinking_content == ""
    ) {
      result.push({
        title: title, // 使用 status 中的值作为标题
        content: detailed_status.thinking_content,
        type: "content",
        funcName: func_name, // 保留 func_name
      });
    }
    if (detailed_status?.sql_query) {
      result.push({
        title: title, // 使用 status 中的值作为标题
        content: {
          sql_query: detailed_status.sql_query,
          sql_result: detailed_status.sql_result,
          tableqa_answer: detailed_status.tableqa_answer,
        },
        type: "sql",
        funcName: func_name, // 保留 func_name
      });
    }
    if (!detailed_status || Object.keys(detailed_status).length === 0) {
      result.push({
        title: title,
        content: "",
        type: "content",
        funcName: func_name,
      });
    }

    console.log("func_name", func_name);
    return result[0];
  }

  return (
    <div className="index_wrap" style={{ flexDirection: "row" }}>
      <div className="content">
        <div className="chat-container">
          <div className="chat-head flex justify-between">
            <div>
              <h2
                className="flex flex-wrap align-start justify-center"
                style={{ fontSize: 20, fontWeight: 600 }}
              >
                DeepResearch
              </h2>
              {/* <span className="search_title">Model</span>
              <Select
                value={model}
                options={selectOption}
                allowClear
                style={{ width: "200px" }}
                onChange={(e) => setModel(e)}
              /> */}
            </div>
            <div style={{ marginRight: "0px" }}>
              <span className="search_title">{t("btn.stream")}</span>
              <Switch value={stream} onChange={(e: any) => setStream(e)} />
            </div>
          </div>
          <div
            className="messages-container"
            ref={containerRef}
            onScroll={handleScroll}
            style={{
              height: `calc(100% - ${inputRef.current?.offsetHeight}px - 30px)`,
            }}
          >
            <div className="scroll_container">
              <div className="scroll_item">
                {messages.map((message: any, index) => {
                  return (
                    <div key={index} className={`message ${message.from}`}>
                      {message.from === "user"
                        ? UserAvatar()
                        : BotAvatar(common.dbTabs[0]?.name)}
                      <div className={`message-box ${message.from}`}>
                        {message.from === "user" ? (
                          <div className="user-bg">{message.text}</div>
                        ) : (
                          <div className="step-bg">
                            <div
                              className="bot-bg"
                              ref={(el) => (pdfRefs.current[index] = el)}
                            >
                              {message.text && <p
                                className="bot-title"
                                style={{ marginBottom: 10 }}
                              >
                                {message.text}
                              </p>}
                              <div
                                className="bot-answer"
                                style={{ padding: "10px 30px 0px" }}
                              >
                                <StepContent message={message} />
                              </div>
                              {message.stepCurrent && message.content && (
                                <div className="export-btn flex justify-end">
                                  <ExportButton
                                    content={message.content}
                                    name={message.exportName}
                                    dom={pdfRefs.current[index]}
                                  />
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              {isBotThinking && (
                <div className="message bot">
                  {BotAvatar(common.dbTabs[0]?.name)}
                  <div className={`message-box bot bot-loading`}>
                    <Loading />
                  </div>
                </div>
              )}
            
              <div ref={messagesEndRef} />
            </div>
          </div>

          {
            <div className="input-area" ref={inputRef}>
              <div
                className="flex justify-between align-center"
                style={{ marginBottom: 10, color: "#878aab", fontSize: 12 }}
              >
                <p></p>
                <Typography.Text
                  type="secondary"
                  onClick={clear}
                  disabled={!isChatEnd}
                  style={{ cursor: "pointer" }}
                >
                  <RetweetOutlined style={{ marginRight: 3 }} />
                  <span style={{ fontSize: 16 }}>{t("index.reset")}</span>
                </Typography.Text>
              </div>
              <div className="input_border">
                {isEnd && <div className="input_disable"></div>}
                <TextArea
                  autoSize={{ minRows: 2, maxRows: 3 }}
                  value={userInput}
                  ref={textAreaRef}
                  disabled={!isChatEnd}
                  placeholder={t("index.input")}
                  style={{ border: "none", outline: "none", boxShadow: "none" }}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                    setUserInput(e.target.value)
                  }
                  onKeyDown={handleKeyDown}
                  onCompositionStart={handleCompositionStart}
                  onCompositionEnd={handleCompositionEnd}
                />
                <span
                  onClick={handleSend}
                  className={[
                    "send",
                    userInput && userInput.length == 0 ? "send_disable" : "",
                  ].join(" ")}
                >
                  <SendOutlined style={{ color: "white" }} />
                </span>
              </div>
            </div>
          }
        </div>
      </div>
      {showSlider && (
        <InferenceSidebar items={items} setShowSidebar={setShowSlider} />
      )}
      <ItemModel
        open={openModal}
        onCreate={onCreate}
        onCancel={onCancel}
        initList={common.dbTabs}
      />
    </div>
  );
};

export default Dash;
