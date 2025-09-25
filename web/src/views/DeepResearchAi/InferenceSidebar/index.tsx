import React, { useEffect, useRef, useState } from "react";
import { Layout, Typography, Button, Collapse, theme, List } from "antd";
import { CloseOutlined, DownOutlined, UpOutlined } from "@ant-design/icons";
import { CSSTransition } from "react-transition-group";
import "./InferenceSidebar.scss";
import botImg from "@/assets/img/bot.jpg";
import { CaretRightOutlined } from "@ant-design/icons";
import Avatar from "@/components/Avatar";
import InferenceContent from "./InferenceContent";
const BotAvatar = (name?: string) => {
  return (
    <div className="inter-bot-avatar">
      <img src={botImg} alt="Bot" />
      {name}
    </div>
  );
};

const { Sider } = Layout;
const { Paragraph } = Typography;

interface InferenceItem {
  title: string;
  content: any;
  type?: string;
}

interface InferenceSidebarProps {
  items: InferenceItem[];
  setShowSidebar: (show: boolean) => void;
}

const InferenceSidebar: React.FC<InferenceSidebarProps> = ({
  items,
  setShowSidebar,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  // 用于监听 items 的变化并滚动到底部
  useEffect(() => {
    const messagesContainer = messagesEndRef.current;

    if (messagesContainer && !isHovering) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight;
    }
  }, [items]);

  return (
    <CSSTransition in={true} appear={true} timeout={300} classNames="slide-in">
      <Sider
        width={"25%"}
        style={{
          background: "#fff",
          height: "100%",
          padding: "20px 15px",
          borderLeft: '1px solid #f0f0f0'

        }}
      >
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={() => setShowSidebar(false)}
          style={{ position: "absolute", top: 10, right: 20 }}
        />
        <div
          ref={messagesEndRef}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
          style={{ height: "calc(100vh - 40px)", overflowY: "auto" }}
        >
          {items.map((item, index) => (
            <InferenceItemContent item={item} key={index} />
          ))}
        </div>
      </Sider>
    </CSSTransition>
  );
};

const InferenceItemContent: React.FC<{ item: InferenceItem }> = ({ item }) => {
  const { token } = theme.useToken();

  const panelStyle: React.CSSProperties = {
    marginBottom: 24,
    background: token.colorFillAlter,
    borderRadius: token.borderRadiusLG,
    border: "none",
  };
  return (
    <div style={{ marginBottom: 10 }}>
      <Collapse
        accordion
        bordered={false}
        defaultActiveKey={[]}
        style={{ background: "#000000e0", ...panelStyle }}
        expandIconPosition="end"
        expandIcon={({ isActive }) => (
          <CaretRightOutlined rotate={isActive ? 90 : 0} />
        )}
        items={[
          {
            key: "1",
            showArrow: item.content ? true : false,
            label: (
              <div className="flex align-center" style={{ marginLeft: -10 }}>
                {BotAvatar()} {item.title}
              </div>
            ),
            children: (
              <div style={{ paddingLeft: 10 }}>
                <InferenceContent message={item} />
              </div>
            ),
          },
        ]}
      />
    </div>
  );
};

export default InferenceSidebar;
