import ChatText from "./ChatText";
import { List } from "antd";
import Avatar from "@/components/Avatar";

const StepContent = ({ message }: any) => {
  const { type, content } = message;
  
  if (type === "text") {
    return <div>vvv<ChatText text={content}></ChatText></div>;
  }

  if (type === "list" || type === "url") {
    return (
      <div style={{ padding: "0 0px" }}>
        <List
          dataSource={content.list}
          renderItem={(item) => renderListItem(item, 'list')}
        />
        <List
          dataSource={content.urlList}
          grid={{ gutter: 16, column: 2 }}
          renderItem={(item) => renderListItem(item, 'url')}
        />
      </div>
    );
  }
  if (type === "sql") {
    return (
      <div>
        <p>sql_query:{content.sql_query}</p>
        <p>sql_result:{content.sql_result}</p>
        <p>tableqa_answer: <ChatText text={content.tableqa_answer}></ChatText></p>
      </div>
    );
  }
  if (type === "content") {
    return <ChatText text={content}></ChatText>;
  }

  // 如果没有匹配的类型，则返回 null
  return null;
};

const renderListItem = (item: any, type: string) => {
  if (type === "url") {
    return (
      <List.Item>
        <div className="flex align-center" style={{ marginBottom: 10 }}>
          <Avatar src={item.src} alt={item.url} />
          <a
            href={item.url}
            target="_blank"
            style={{ 'whiteSpace':'nowrap',overflow:'hidden',textOverflow:'ellipsis',width:'50%',maxWidth:'300px' }}
            rel="noreferrer"
          >
            {item.url}
          </a>
        </div>
      </List.Item>
    );
  } else {
    return <List.Item>{item}</List.Item>;
  }
};

export default StepContent;
