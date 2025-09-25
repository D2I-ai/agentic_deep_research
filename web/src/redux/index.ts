// store.js
import { Reducer, configureStore } from '@reduxjs/toolkit';
import rootReducer from './modules';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

const persistConfig = {
  key: 'redux-state',
  storage,
  // 你可以在这里指定要持久化的reducer
  whitelist: ['user'],
};

const persistedReducer = persistReducer(persistConfig, rootReducer as Reducer<any>);
export const store = configureStore({
  reducer: persistedReducer,
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: false,
    })
});
export const persistor = persistStore(store);