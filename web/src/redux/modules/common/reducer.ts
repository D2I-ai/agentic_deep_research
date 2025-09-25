import * as types from "../../mutation-types";
// 初始用户状态
const initialState = {
  dbId: "saudi_bank",
  dbName: "官方数据库",
  dbTabs: [],
};

// 用户reducer函数
const commonReducer = (state = initialState, action: any) => {
  switch (action.type) {
    case types.SET_DBID:
      // 处理登录action
      return {
        ...state,
        dbId: action.dbId,
        dbName: action.dbName,
      };
    case types.SET_DBTABS:
      // 处理登录action
      return {
        ...state,
        dbTabs: action.dbtabs,
      };

    default:
      // 对于未知的action类型，返回当前的state
      return state;
  }
};

export default commonReducer;
