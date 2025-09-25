import React from "react";
import ReactDOM from "react-dom/client";
import logoSrc from "@/assets/img/bot.jpg";
interface HeaderProps {
}

const Header: React.FC<HeaderProps> = () => {
  return (
    <div className="export-header">
      <h2 style={{ textAlign: "center", marginBottom: 50 }}>
        {/* 阿里云-大数据与智能实验室 */}
      </h2>
      <div style={{ display: "flex", alignItems: "center", marginBottom: 50 }}>
        <img
          src={logoSrc}
          alt="Logo"
          style={{ width: "40px", height: "40px", marginRight: "10px",borderRadius: '50%' }}
        />
        <h3 style={{margin: 0,fontWeight: 500}}>DeepResearch</h3>
      </div>
    </div>
  );
};

const renderHeader = (element: HTMLDivElement) => {
  const root = ReactDOM.createRoot(element);
  root.render(<Header />);
};

export default renderHeader;
