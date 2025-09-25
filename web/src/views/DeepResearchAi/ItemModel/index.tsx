import { useState, useEffect } from "react";
import { Modal, Button, Row, Col, Tooltip } from "antd";
import { getDb, createDb } from "@/api/dataSql";
import itemImg from "@/assets/img/bot.jpeg";
import { useTranslation } from "react-i18next";

import "./index.scss";
const Title = ({ open, onCancel, onCreate, initList }: any) => {
  const [myItem, setMyItem] = useState<any>([]);
  const [activeList, setActiveList] = useState<Array<any>>([]);
  const { t } = useTranslation();

  const Item = ({ name, subtitle, img, active, onClick }: any) => {
    return (
      <div
        className={`model_item ${active ? "model_item_active" : ""}`}
        onClick={onClick}
      >
        <img style={{ width: 35, height: 35 }} src={img} />
        <div className="left_item">
          <h3>{name}</h3>
          {/* <span>{subtitle}</span> */}
        </div>
      </div>
    );
  };
  let clear = () => {
    setActiveList([]);
    onCancel();
  };
  useEffect(() => {
    init();
  }, []);
  useEffect(() => {
    if (open) {
      setActiveList(initList);
    }
  }, [open]);
  let handleClick = (item: any) => {
    setActiveList((prevList) => {
      // 如果当前项已在列表中，则取消高亮
      if (prevList.some((activeItem) => activeItem.id === item.id)) {
        return prevList.filter((activeItem) => activeItem.id !== item.id);
      }

      // 如果当前项不在列表中，则添加至列表
      // const newList = [...prevList, item];
      const newList = [item];

      // 限制最多只能选中 2 项
      return newList.length > 2 ? newList.slice(1) : newList;
    });
  };
  let submit = () => {
    onCreate(activeList);
  };
  const mockList = [
    {
      id: "m72",
      name: "英语陪练",
    },
    // {
    //   id: "m14",
    //   name: "ChatBI-mini",
    // },
  ];
  let init = async () => {
    let list = mockList.map((item: any) => {
      return {
        id: item.id,
        name: item.name,
        title: item.name,
        img: itemImg,
      };
    });
    setMyItem([...list]);
    // let res: any = await getDb({
    //   optype: "query",
    //   pageStart: 1,
    //   pageSize: 3,
    // });
    // if (res.code === 200) {

    // }
  };
  return (
    <Modal
      open={open}
      title={t("index.choose")}
      width={800}
      onCancel={clear}
      maskClosable={false}
      footer={[]}
    >
      <div style={{ marginBottom: 10, textAlign: "right" }}>
      </div>
      <Row gutter={[16, 16]} style={{ margin: "20px 0", minHeight: "100px" }}>
        {myItem.map((it: any, idx: number) => {
          return (
            <Col xs={{ span: 12 }} sm={{ span: 12 }} key={idx}>
              <Item
                {...it}
                active={activeList.some((item) => item.id === it.id)}
                onClick={() => handleClick(it)}
              />
            </Col>
          );
        })}
      </Row>
      <div className="flex justify-end">
        <Button onClick={onCancel}>{t("btn.cancel")}</Button>
        <Button style={{ marginLeft: "10px" }} type="primary" onClick={submit}>
          {t("btn.confirm")}
        </Button>
      </div>
    </Modal>
  );
};

export default Title;
