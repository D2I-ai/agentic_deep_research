declare module 'echarts' {
    interface ECharts {
        init: (dom: HTMLElement, theme?: string) => ECharts;
        setOption: (option: any, notMerge?: boolean, lazyUpdate?: boolean) => void;
        // 可以根据需要添加更多方法
    }

    const echarts: {
        init: (dom: HTMLElement, theme?: string) => ECharts;
        // 其他 ECharts 方法的类型定义
    };
    export = echarts;
}
