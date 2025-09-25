import { useState, useEffect } from "react";
import { Drawer, Button, Row, Tag, message } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import Table from "@/components/Table";
import "./index.scss";
const Title = ({ open, onCancel, onCreate, value }: any) => {
  const [messageApi, contextHolder] = message.useMessage();
  const { t } = useTranslation();
  const { info } = value;
  // 函数用于转换对象为可渲染的数组
  const convertToRenderableArray = (
    info: Record<string, any>
  ): Array<JSX.Element> => {
    return (
      info &&
      Object.entries(info).map(([key, value]) => (
        <div key={key} className="info_item">
          <h2>{key}</h2>
          <div>
            <Tag color="">Chinese: {value.chinese}</Tag>
            <Tag>Grade: {value.grade}</Tag>
            <Tag>Rank: {value.rank}</Tag>
          </div>
        </div>
      ))
    );
  };
  const other_Array =
    info?.other_info && convertToRenderableArray(info.other_info);
  const other_rewite_Array =
    info?.rewrite_other_info &&
    convertToRenderableArray(info.rewrite_other_info);
  let clear = () => {
    onCancel();
  };
  useEffect(() => {
    init();
  }, []);
  useEffect(() => {
    if (open) {
    }
  }, [open]);

  let submit = () => {
    onCreate();
  };
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text); // 使用 Clipboard API 复制文本
      messageApi.success("复制成功");
    } catch (err) {}
  };

  let init = async () => {};
  const Copy = ({ text }: any) => {
    return (
      <CopyOutlined
        style={{ marginLeft: 10, color: "#666" }}
        onClick={() => copyToClipboard(text)}
      />
    );
  };
  return (
    <div className="detail-model-container">
      {contextHolder}
      <Drawer
        open={open}
        title="Details"
        width={"40%"}
        onClose={clear}
        maskClosable={true}
      >
        <div className="detail-model">
          <div className="detail-model-item">
            <div className="answer">
              <p className="title">Answer:</p>
              <div className="detail-model-item-content">
                <p>{info?.answer}</p>
              </div>
            </div>
            <div className="detail-model-item-title">Other_Info</div>

            <div className="detail-model-item-content">
              <div className="detail_sql">{other_Array}</div>
            </div>
          </div>
          <div className="detail-model-item">
            <div className="answer">
              <p className="title">Rewrite_Answer:</p>
              <div className="detail-model-item-content">
                <p>{info?.rewrite_answer || ''}</p>
              </div>
            </div>
            <div className="detail-model-item-title">Rewrite_Other_Info</div>
            <div className="detail-model-item-content">
              <div className="detail_sql">{other_rewite_Array}</div>
            </div>
          </div>
        </div>
      </Drawer>
    </div>
  );
};

export default Title;
