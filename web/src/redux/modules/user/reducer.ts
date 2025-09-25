import * as types from '../../mutation-types'
// 初始用户状态
const initialState = {
    username: '',
    userId: 'guest',
    token: '',
    isLogin: false,
  };
  

  
  // 用户reducer函数
  const userReducer = (state = initialState, action:any) => {
    switch (action.type) {
      case types.SET_TOKEN:
        // 处理登录action
        return {
          ...state,
          token: action.token,
          isLogin: true,
        };
      case types.LOGIN:
        // 处理登录action
        return {
          ...state,
          username: action.payload.username,
          isLogin: true,
        };
      case types.LOGOUT:
        // 处理登出action
        return {
          ...state,
          username: '',
          token: '',
          isLogin: false,
        };
      default:
        // 对于未知的action类型，返回当前的state
        return state;
    }
  };
  
  export default userReducer;
  