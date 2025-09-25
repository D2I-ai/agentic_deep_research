import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

interface CodeHighlighterProps {
  codeString: string; // 传入的代码字符串
  language: 'javascript' | 'typescript' | 'python' | 'java' | 'css' | 'html' | 'sql'; // 等等，根据需求选择需要的语言
  style?: any; // 可自定义样式
}

const CodeHighlighter: React.FC<CodeHighlighterProps> = ({ codeString, language, style}) => {
  return (
    <SyntaxHighlighter language={language} style={style}>
      {codeString}
    </SyntaxHighlighter>
  );
};

export default CodeHighlighter;
