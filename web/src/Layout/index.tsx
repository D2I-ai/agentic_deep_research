import { useState } from "react";
import Menu from "./components/Menu";
import { Layout, Button, theme } from "antd";
import { Outlet } from "react-router-dom";
import logo from "@/assets/img/logo.jpg";
import { useTranslation } from "react-i18next";
import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";
const { Content, Sider, Header } = Layout;
const LayoutWrap = () => {
  const [collapsed, setCollapsed] = useState(false);
  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };
  const { t } = useTranslation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  return (
    <>
      <Layout
        style={{ height: "100vh", background: "white" }}
        className="layout"
      >
        {/* <Sider
          style={{
            borderRight: "1px solid #e7e8ee",
            marginTop: 0,
            height: "100%",
            overflowY: "auto",
          }}
          width={"18%"}
          theme={"light"}
          trigger={null}
          collapsible
          collapsed={collapsed}
        >
          <Header
            className="flex align-center justify-center"
            style={{
              padding: 0,
              background: colorBgContainer,
              marginBottom: 20,
              flexWrap: "wrap",
              minWidth: !collapsed?140:0,
            }}
          >
            <img
              src={logo}
              style={{
                width: 36,
                height: 36,
                borderRadius: borderRadiusLG,
                marginRight: 5,
                marginTop: collapsed?30:0,
              }}
            />
            {!collapsed && (<h2
              className="flex flex-wrap align-start justify-center"
              style={{ fontSize: 20, fontWeight: 600 }}
            >
              {t("menu.title")}
            </h2>)}
          </Header>
          <div style={{ position: "absolute", right: "0", top: '0' }}>
            <Button onClick={toggleCollapsed} size="small">
              {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            </Button>
          </div>
          <Menu />
        </Sider> */}
        <Layout style={{ backgroundColor: colorBgContainer }}>
          <Content
            style={{
              overflowY: "auto",
              height: "calc(100vh - 0px)",
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </>
  );
};

export default LayoutWrap;
