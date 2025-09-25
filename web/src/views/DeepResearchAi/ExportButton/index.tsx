import React from "react";
import { Button, Select, message } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import html2canvas from "html2canvas";
import { PDFDocument, rgb } from "pdf-lib";
import renderHeader from "./renderHeader";
interface ExportButtonProps {
  content: string;
  name: string; // 新增 name 属性
  dom: any; // 新增 name 属性
}
interface ExportOptions {
  topMarginPt?: number; // 第二页起顶部间距（pt）
  bottomMarginPt?: number; // 页尾留白（pt）
  bgColor?: string; // 背景色，默认 #f6f6f9
  showPageNumbers?: boolean; // 是否显示页码
}
const ExportButton: React.FC<ExportButtonProps> = ({ content, name, dom }) => {
  const [format, setFormat] = React.useState<string>("pdf");

  const exportFile = () => {
    message.info("开始下载");

    if (format === "pdf") {
      exportToPDF(name, dom);
    } else if (format === "md") {
      exportToMarkdown(content, name);
    } else if (format === "image") {
      exportToImage(name, dom);
    } else {
      message.error("Unsupported format selected");
    }
  };
  const exportToImage = async (
    filename: string,
    element: HTMLDivElement | null
  ) => {
    if (!element) {
      message.error("Content element not found.");
      return;
    }

    // 克隆元素
    const clonedElement = element.cloneNode(true) as HTMLDivElement;
    clonedElement.style.width = "90%";
    clonedElement.style.padding = "20px 6% 60px";

    // 应用样式，确保字体和颜色正确设置
    const style = document.createElement("style");
    style.innerHTML = `
      h1,h2,h3,h4,h5,h6 {
        font-family: Arial, sans-serif !important;
        color: #333333 !important;
      }
      p,span,li {
        font-family: Arial, sans-serif !important;
        color: #666666 !important;
      }
    `;
    clonedElement.prepend(style);

    removeTitle(clonedElement);
    addHeader(clonedElement);

    clonedElement.style.position = "absolute";
    clonedElement.style.top = "-9999px";
    document.body.appendChild(clonedElement);

    setTimeout(async () => {
      const canvas = await html2canvas(clonedElement, { scale: 2 });

      const imageData = canvas.toDataURL("image/png");
      const elementLink = document.createElement("a");
      elementLink.href = imageData;
      elementLink.download = `${filename}.png`;
      document.body.appendChild(elementLink);
      elementLink.click();
      document.body.removeChild(elementLink);
      document.body.removeChild(clonedElement);
    }, 200); // 微小延迟，确保渲染完成
  };

  const exportToPDF = async (
  filename: string,
  element: HTMLDivElement | null
) => {
  if (!element) {
    message.error("Content element not found.");
    return;
  }

  // === 克隆 DOM ===
  const clonedElement = element.cloneNode(true) as HTMLDivElement;
  clonedElement.style.width = "90%";
  clonedElement.style.boxSizing = "border-box";

  // 保真颜色：同步原 DOM 中的颜色，防止 a 链接变紫/变蓝
  const origNodes = element.querySelectorAll("*");
  const clonedNodes = clonedElement.querySelectorAll("*");
  origNodes.forEach((orig, idx) => {
    const cs = getComputedStyle(orig);
    (clonedNodes[idx] as HTMLElement).style.color = cs.color;
    if (clonedNodes[idx].tagName === "A") {
      (clonedNodes[idx] as HTMLElement).style.textDecoration = "none";
    }
  });

  // 保留项目的自定义逻辑
  removeTitle(clonedElement);
  addHeader(clonedElement);

  clonedElement.style.position = "absolute";
  clonedElement.style.top = "-9999px";
  clonedElement.style.left = "0";

  // ✅ 新的 padding（上30px，左右6%，下80px）
  clonedElement.style.padding = "30px 6% 80px";
  clonedElement.style.background = "#f6f6f9";

  document.body.appendChild(clonedElement);

  await new Promise(res => setTimeout(res, 300));

  const fullCanvas = await html2canvas(clonedElement, {
    scale: 2,
    useCORS: true
  });
  const ctxFull = fullCanvas.getContext("2d")!;

  const A4_WIDTH = 595.28;
  const A4_HEIGHT = 841.89;
  const imgWidth = A4_WIDTH;
  const basePageHeightPx = (fullCanvas.width / imgWidth) * A4_HEIGHT;

  // 背景色
  const bgR = 246, bgG = 246, bgB = 249;
  const tolerance = 8;
  const isBgColor = (r: number, g: number, b: number) =>
    Math.abs(r - bgR) <= tolerance &&
    Math.abs(g - bgG) <= tolerance &&
    Math.abs(b - bgB) <= tolerance;

  const topMarginPt = 40;    // 第二页及以后顶部间距
  const bottomMarginPx = 60; // 每页尾部留白
  const searchRange = 60;    // 向上查找范围
  const minBlankRatio = 0.95;// 背景判定比例

  let renderedHeight = 0;
  const pageImages: HTMLCanvasElement[] = []; // 保存每页的Canvas

  // === 分页生成每页Canvas ===
  while (renderedHeight < fullCanvas.height) {
    let sliceHeight =
      renderedHeight + basePageHeightPx < fullCanvas.height
        ? basePageHeightPx - bottomMarginPx
        : fullCanvas.height - renderedHeight;

    if (renderedHeight + sliceHeight < fullCanvas.height) {
      let foundOffset = -1;

      // 1. 找背景行
      for (let offset = 0; offset < searchRange; offset++) {
        const testY = renderedHeight + sliceHeight - offset;
        const row = ctxFull.getImageData(0, testY, fullCanvas.width, 1).data;
        let rowBgCount = 0;
        const rowTotalPx = row.length / 4;
        for (let i = 0; i < row.length; i += 4) {
          if (isBgColor(row[i], row[i + 1], row[i + 2])) {
            rowBgCount++;
          }
        }
        if (rowBgCount / rowTotalPx >= minBlankRatio) {
          foundOffset = offset;
          break;
        }
      }

      // 2. 没有背景行 → 用亮度变化补救
      if (foundOffset === -1) {
        let prevBrightness = null;
        for (let offset = 0; offset < searchRange; offset++) {
          const testY = renderedHeight + sliceHeight - offset;
          const row = ctxFull.getImageData(0, testY, fullCanvas.width, 1).data;
          let brightnessSum = 0;
          const totalPixels = row.length / 4;
          for (let i = 0; i < row.length; i += 4) {
            const brightness = 0.299 * row[i] + 0.587 * row[i + 1] + 0.114 * row[i + 2];
            brightnessSum += brightness;
          }
          const avgBrightness = brightnessSum / totalPixels;
          if (prevBrightness !== null) {
            if (Math.abs(avgBrightness - prevBrightness) > 15) {
              foundOffset = offset;
              break;
            }
          }
          prevBrightness = avgBrightness;
        }
      }

      if (foundOffset > 0) {
        sliceHeight -= foundOffset;
      }
    }

    const pageCanvas = document.createElement("canvas");
    pageCanvas.width = fullCanvas.width;
    pageCanvas.height = sliceHeight;
    const ctx = pageCanvas.getContext("2d")!;
    ctx.drawImage(
      fullCanvas,
      0,
      renderedHeight,
      fullCanvas.width,
      sliceHeight,
      0,
      0,
      fullCanvas.width,
      sliceHeight
    );

    pageImages.push(pageCanvas);
    renderedHeight += sliceHeight;
  }

  const totalPages = pageImages.length;
  const pdfDoc = await PDFDocument.create();

  // === 将页面添加到 PDF ===
  for (let i = 0; i < pageImages.length; i++) {
    const pageCanvas = pageImages[i];
    const imgHeightPt = (pageCanvas.height * imgWidth) / pageCanvas.width;
    const pageIndex = i + 1;

    const page = pdfDoc.addPage([imgWidth, A4_HEIGHT]);

    // 背景色填充
    page.drawRectangle({
      x: 0,
      y: 0,
      width: imgWidth,
      height: A4_HEIGHT,
      color: rgb(bgR / 255, bgG / 255, bgB / 255)
    });

    const yOffsetTop = pageIndex > 1 ? topMarginPt : 0;
    const imgData = pageCanvas.toDataURL("image/png");
    const image = await pdfDoc.embedPng(imgData);

    // 绘图
    page.drawImage(image, {
      x: 0,
      y: A4_HEIGHT - imgHeightPt - yOffsetTop,
      width: imgWidth,
      height: imgHeightPt
    });

    // 页码（含总页数）
    const pageNumText = `${pageIndex} / ${totalPages}`;
    page.drawText(pageNumText, {
      x: imgWidth - pageNumText.length * 5 - 20,
      y: 20,
      size: 10
    });
  }

  const pdfBytes = await pdfDoc.save();
  download(pdfBytes, `${filename}.pdf`, "application/pdf");

  document.body.removeChild(clonedElement);
};
  const removeTitle = (element: HTMLDivElement) => {
    // `.bot-title` 类
    const titleElements = element.querySelectorAll(".bot-title");
    titleElements.forEach((title) => title.remove());

    // `.export-btn` 类
    const exportBtnElements = element.querySelectorAll(".export-btn");
    exportBtnElements.forEach((btn) => btn.remove());
  };

  const addHeader = (element: HTMLDivElement) => {
    const headerContainer = document.createElement("div");
    element.prepend(headerContainer);
    renderHeader(headerContainer);
  };
  const download = (data: Uint8Array, filename: string, mimeType: string) => {
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = filename;

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  const exportToMarkdown = (content: string, filename: string) => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: "text/markdown" });
    element.href = URL.createObjectURL(file);
    element.download = `${filename}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      <Select
        value={format}
        onChange={(value) => setFormat(value)}
        style={{ width: 120, marginRight: 10 }}
      >
        <Select.Option value="pdf">PDF</Select.Option>
        <Select.Option value="md">Markdown</Select.Option>
        <Select.Option value="image">Image</Select.Option>
      </Select>
      <Button
        type="primary"
        shape="circle"
        onClick={exportFile}
        icon={<DownloadOutlined />}
      />
    </div>
  );
};

export default ExportButton;
