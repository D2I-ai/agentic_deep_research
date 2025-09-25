import React, { useEffect, useState } from 'react';
import { useTranslation } from "react-i18next";
import { Radio } from 'antd';
const LanguageSwitcher = () => {
  const { i18n,t } = useTranslation();
  const changeLanguage = (e: any) => {
    setValue(e.target.value);
    i18n.changeLanguage(e.target.value);
  };
  useEffect(() => {
    setValue(i18n.language);
  },[])
  const [value, setValue] = useState('zh');
  const options = [
    { label: t('btn.english'), value: 'en' },
    { label: t('btn.chinese'), value: 'zh' },
  ];
  return (
    <div>
       <Radio.Group
        options={options}
        onChange={changeLanguage}
        value={value}
        optionType="button"
        buttonStyle="solid"
      />
    </div>
  );
};

export default LanguageSwitcher;
