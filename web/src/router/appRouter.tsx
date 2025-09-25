import { lazy } from "react";
import layoutRouter from './layoutRouter'
const item = [
  {
    path: "/",
    meta: {
      title: "首页",
      isShow:true
    },
    component: lazy(() => import("@/Layout")),
    children: layoutRouter
  },
  {
    path: "/404",
    meta: {
      title: "404",
    },
  }
];

export default item;
