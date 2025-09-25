import { useState, useEffect } from "react";
import { Modal, Button, Row, Col,Tooltip } from "antd";
import { getDb, createDb } from "@/api/dataSql";
import itemImg from "@/assets/img/data_item.jpg";

const Title = ({ open, onCancel }: any) => {
  const [myItem, setMyItem] = useState<any>([]);
  const Item = ({
    title,
    subtitle,
    img,
    btn,
    btnWidth = "80px",
    tops = "",
    active,
    onClick,
  }: any) => {
    return (
      <div
        className={`data_item ${active ? "data_item_active" : ""}`}
        onClick={onClick}
      >
        <img src={img} />
        <div className="left_item">
          <div className="flex">
            <Tooltip
              placement="topLeft"
              color={"#fff"}
              overlayInnerStyle={{ color: "#333" }}
              title={title}
            >
              <h3>{title}</h3>
            </Tooltip>
            {tops && (
              <span
                className={`item_tips ${tops == "官方" ? "tops" : "tops1"}`}
              >
                {tops}
              </span>
            )}
          </div>

          <span>{subtitle}</span>
        </div>
      </div>
    );
  };
  let clear = () => {
    onCancel();
  };
  useEffect(() => {
    init();
  }, []);
  let init = async () => {
    let res: any = await getDb({
      optype: "query",
      pageStart: 1,
      pageSize: 99,
    });
    if (res.code === 200) {
      let list = res.data.map((item: any) => {
        return {
          id: item.id,
          name: item.name,
          title: item.name,
          subtitle: item.description,
          img: itemImg,
          btn: (
            <Button
              type="default"
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              查看详情
            </Button>
          ),
        };
      });
      setMyItem([...list]);
    }
  };
  return (
    <Modal
      open={open}
      title={"选择模型"}
      width={520}
      onCancel={clear}
      maskClosable={false}
      footer={[]}
    >
      <Row gutter={[16, 16]}>
        {myItem.map((it: any, idx: number) => {
          return (
            <Col
              lg={{ span: idx == 0 ? 8 : 8 }}
              xs={{ span: 24 }}
              sm={{ span: 24 }}
              key={idx}
            >
              <Item
                {...it}
              />
            </Col>
          );
        })}
      </Row>
    </Modal>
  );
};

export default Title;
