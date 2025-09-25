import React, { useState, useEffect } from "react";
import { Button } from "antd";
import './markdown.scss';
import "./index.scss";
import { useStreamMarkdown } from "@/hooks/useStreamMarkdown";
interface TypingMessageProps {
  text: string;
  visibleHtml?: any;
  stream?: boolean;
  end?: (f: boolean) => void;
  time?: number;
  isChatEnd?: boolean;
  info?: any;
  subTable?: any;
  popverData?: any;
  sendText?: any;
  img?: any;
  code?: any;
  handleOpen?:any
}

const TypingMessage: React.FC<TypingMessageProps> = ({
  text,
  time = 10,
  end= (f:boolean)=>{},
  stream = true,
  isChatEnd = false,
  info,
  sendText,
  handleOpen
}) => {
  const [visibleText, setVisibleText] = useState("");
  const [visibleHtml, setVisibleHtml] = useState([]);
  // const [showCursor, setShowCursor] = useState(true);
  const [textEnd, setTextEnd] = useState(false);
  const { htmlContent } = useStreamMarkdown(text);

  useEffect(() => {
    let intervalId: any;
    // const regex = /"([^"]+)"/g;
    const citationRegex = /\[citation:\s*(\d+)\]/g;
    // 使用正则表达式分割原始文本
    let parts: any;
    if (text != undefined) {
      parts = text.split(citationRegex);
    }
    // console.log(parts);

    if (!stream) {
      text = text || ''
      intervalId = setInterval(() => {
          setVisibleText((currentText) => {
              const nextText = text && text.slice(0, currentText.length + 1);
              if (nextText.length === text.length) {
                  clearInterval(intervalId);
                  setTextEnd(true)
              }
              return nextText;
          });
      }, time);

      setVisibleText(text);
      // setVisibleHtml(parts);
      // setTextEnd(true);
    } else {
      setVisibleText(text);
      setVisibleHtml(parts);
    }
    return () => clearInterval(intervalId);
  }, [text]);

  useEffect(() => {
    if (!!textEnd) {
      // setShowCursor(false);
      end(true);
    }
  }, [textEnd]);
  useEffect(() => {
    if (!!isChatEnd) {
      setTextEnd(true);
      end(true);
    }
  }, [isChatEnd]);

  return (
    <div>
      <div className={`message-text ${visibleText && "visible"}`}>
        {/* <pre>{htmlContent}</pre> */}
        <div className="flex">
          <div className="markdown-body flex-sub align-center">
            {htmlContent && (
              <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
            )}
          </div>
        </div>
        <div className="flex justify-center">
          {info && (
            <>
              <Button
                className="btn"
                type="primary"
                size="small"
                onClick={handleOpen}
              >
                Details
              </Button>
              {/* <Button
                type="primary"
                onClick={() => handleOpen("img")}
                style={{ marginLeft: 10 }}
              >
                Image Refine
              </Button> */}
            </>
          )}
        </div>

        {/* <span className={`cursor ${!showCursor && 'hidden'}`}></span> */}
      </div>
      {/* {textEnd && <ChatToggle text={visibleText} />} */}
    </div>
  );
};

export default TypingMessage;
