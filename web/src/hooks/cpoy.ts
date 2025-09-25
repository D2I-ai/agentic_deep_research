import { useState } from 'react';

// 备选方法复制文本
function fallbackCopyTextToClipboard(text: string): boolean {
    const textArea = document.createElement('textarea');
    textArea.value = text;

    // 避免在屏幕上出现
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    let successful = false;
    try {
        successful = document.execCommand('copy');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }

    document.body.removeChild(textArea);
    return successful;
}

// 自定义 Hook，用于复制文本
export const useClipboard = () => {
    const [isCopied, setIsCopied] = useState<boolean>(false);
    const copyTextToClipboard = async (text: string) => {
        // 使用 navigator.clipboard API 如果可用
        return new Promise(async(reslove, reject) => {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                try {
                    await navigator.clipboard.writeText(text);
                    setIsCopied(true);
                    setTimeout(() => setIsCopied(false), 2000); // 2秒后重置状态
                    reslove(text)
                } catch (err) {
                    reject(err)
                    console.error('Async: Could not copy text: ', err);
                }
            } else {
                // 使用 fallback 方法
                setIsCopied(fallbackCopyTextToClipboard(text));
                setTimeout(() => setIsCopied(false), 2000); // 2秒后重置状态
                reslove('')
            }
        })

    };

    return { isCopied, copyTextToClipboard };
};