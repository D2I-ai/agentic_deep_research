import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import type { MenuProps } from "antd";
import { Menu } from "antd";
import layoutRouter from "@/router/layoutRouter.tsx";
type MenuItem = Required<MenuProps>["items"][number];
import { useTranslation } from "react-i18next";
import enTranslation from "@/locales/en.json";
import zhTranslation from "@/locales/zh.json";
let RouterItem = JSON.parse(JSON.stringify(layoutRouter));
RouterItem = RouterItem.filter((item: any) => {
  item.children = item.children.filter((it: any) => {
    return !it.meta.noShow;
  });
  return !item.meta.noShow;
});
const items: MenuItem[] = RouterItem.map((item: any) => {
  return {
    key: item.meta.path || item.meta.title,
    label: item.meta.title,
    icon: item.meta.icon,
    type: "group",
    children:
      item.children &&
      item.children.map((child: any) => {
        return {
          key: child.path,
          label: child.meta.title,
          title: child.meta.title,
          icon: child?.meta.icon,
          zh: child?.meta.zh,
          en: child?.meta.en,
        };
      }),
  };
});

const App: React.FC = () => {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const [menuItems, setMenuItems] = useState(items);
  const handleClick: MenuProps["onClick"] = (e) => {
    navigate(e.key);
  };
  const location = useLocation();
  const [defaultSelectedKeys, setDefaultSelectedKeys] = useState<any>(["/"]);
  useEffect(() => {
    if (
      location.pathname.includes(defaultSelectedKeys[0]) &&
      defaultSelectedKeys[0] !== "/"
    ) {
      setDefaultSelectedKeys(defaultSelectedKeys);
    } else {
      setDefaultSelectedKeys([location.pathname]);
    }
  }, [location.pathname]);
  const getItems = (items: any) => {
    return items.map((item: any) => {
      if (item.children) {
        item.children =
          item.children.map((child: any) => {
            return {
              ...child,
              // label: i18n.language === "zh" ? getValueByKeyString(zhTranslation, child.title)  : getValueByKeyString(enTranslation, child.title),
              label: child.title,
            };
          });
      }
      return {
        ...item,
        label: t(item.label),
      };
    });
  };
  const getValueByKeyString = (data: any, keyString: string) => {
    return keyString.split('.').reduce((accumulator, currentKey) => {
      if (accumulator && currentKey in accumulator) {
        return accumulator[currentKey];
      }
      return undefined; // 如果找不到对应的键，则返回 undefined
    }, data);
  };
  useEffect(() => {
    setMenuItems(() => {
      return getItems(items);
    });
  }, [i18n.language]);

  return (
    <Menu
      onClick={handleClick}
      mode="inline"
      defaultSelectedKeys={defaultSelectedKeys}
      selectedKeys={defaultSelectedKeys}
      items={menuItems}
    />
  );
};

export default App;
