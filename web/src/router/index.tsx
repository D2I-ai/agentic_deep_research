import { Navigate, useRoutes } from 'react-router-dom'
import { Suspense } from 'react';

// 渲染路由
const renderRoutes = (routes: any) => {
  return routes.map((item: any) => {
    const route: any = { meta: item.meta, path: item.path }
    if (item.component) {
      route.element = <item.component />
    }
    if (item.children) {
      route.children = renderRoutes(item.children)
    }
    if (item.redirect) {
      route.element = <Navigate to={item.redirect} />
    }
    return route
  })
}

// 懒加载动画
const SuspenseWrapper = (props:any)=> {
  return <Suspense fallback={<div className='full_loading'></div>}>{props.children}</Suspense>
}

export default function Router({routes}:any) {
  return (
    <SuspenseWrapper>
      {useRoutes(renderRoutes(routes))}
    </SuspenseWrapper>
  )
}