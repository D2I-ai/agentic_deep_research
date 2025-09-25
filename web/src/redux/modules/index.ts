// reducers/index.js
import { combineReducers } from 'redux';
import user from './user/reducer';
import common from './common/reducer'
const rootReducer = combineReducers({
  user,
  common
  // ...其他reducers
});

export default rootReducer;
