import zhCN from "antd/es/locale/zh_CN";
import enUS from "antd/es/locale/en_US";
import i18n from "i18next";
import enTranslation from "./en.json";
import zhTranslation from "./zh.json";

export const useLocales = (language: string) => {
  const localeMap: any = {
    zh: zhCN,
    en: enUS,
  };

  i18n.init({
    fallbackLng: language,
    debug: false,
    interpolation: {
      escapeValue: false, // React 已经安全地转义了
    },
    resources: {
      en: {
        translation: enTranslation,
      },
      zh: {
        translation: zhTranslation,
      },
    },
    detection: ["sessionStorage"],
  });
  return {
    locale: localeMap
  }
};
