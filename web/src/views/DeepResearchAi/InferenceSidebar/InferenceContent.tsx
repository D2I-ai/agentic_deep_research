import { useState } from "react";
import Avatar from "@/components/Avatar";
import { Typography, List } from "antd";
import { DownOutlined, UpOutlined } from "@ant-design/icons";

const StepContent = ({ message }: any) => {
  const { type, content } = message;
  const [expanded, setExpanded] = useState(false);
  const { Paragraph } = Typography;

  if (type === "text") {
    return (
      <Paragraph
        ellipsis={{
          rows: 3,
          expandable: true,
          symbol: expanded ? (
            <UpOutlined onClick={() => setExpanded(!expanded)} />
          ) : (
            <DownOutlined onClick={() => setExpanded(!expanded)} />
          ),
          onExpand: () => setExpanded(true),
        }}
      >
        {content}
      </Paragraph>
    );
  }

   if (type === "list" || type === "url") {
     return (
       <div style={{ overflow: "hidden", padding: "0 0px" }}>
         <List
           dataSource={content.list}
           renderItem={(item) => renderListItem(item, 'list')}
         />
         <List
           dataSource={content.urlList}
           grid={{ gutter: 6, column: 2 }}
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
        <p>
          tableqa_answer:
          <Paragraph
            ellipsis={{
              rows: 3,
              expandable: true,
              symbol: expanded ? (
                <UpOutlined onClick={() => setExpanded(!expanded)} />
              ) : (
                <DownOutlined onClick={() => setExpanded(!expanded)} />
              ),
              onExpand: () => setExpanded(true),
            }}
          >
            {content.tableqa_answer}
          </Paragraph>
        </p>
      </div>
    );
  }
  if (type === "content") {
    return (
      <Paragraph
        ellipsis={{
          rows: 3,
          expandable: true,
          symbol: expanded ? (
            <UpOutlined onClick={() => setExpanded(!expanded)} />
          ) : (
            <DownOutlined onClick={() => setExpanded(!expanded)} />
          ),
          onExpand: () => setExpanded(true),
        }}
      >
        {content}
      </Paragraph>
    );
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
            style={{ 'whiteSpace':'nowrap',overflow:'hidden',textOverflow:'ellipsis',width:'80%' }}
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
