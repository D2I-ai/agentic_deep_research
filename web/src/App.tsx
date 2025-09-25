import Router from "./router";
import AppRouter from "@/router/appRouter";
import { HashRouter } from "react-router-dom";
import { ConfigProvider } from "antd";
import { PersistGate } from "redux-persist/integration/react";
import { Provider } from "react-redux";
import { store, persistor } from "./redux";
import "@/styles/index.scss";
import i18n from "i18next";
import { I18nextProvider, useTranslation } from "react-i18next";
import { useLocales } from "./locales/index";

function App() {
  const { locale = {} }: any = useLocales("en"); // 确保 locale 不为 undefined
  const language = i18n.language || "en";
  return (
    <>
      <ConfigProvider
        locale={locale[i18n.language]}
        theme={{
          components: {
            Menu: {},
          },
          token: {
            // Seed Token，影响范围大
            colorPrimary: "#624aff",
            colorLink: "#624aff",
            fontSize: 14,
            borderRadius: 4,
            // 派生变量，影响范围小
            colorBgContainer: "#fff",
          },
        }}
      >
        <I18nextProvider i18n={i18n}>
          <HashRouter>
            <Provider store={store}>
              <PersistGate loading={null} persistor={persistor}>
                <Router routes={AppRouter} />
              </PersistGate>
            </Provider>
          </HashRouter>
        </I18nextProvider>
      </ConfigProvider>
    </>
  );
}

export default App;
