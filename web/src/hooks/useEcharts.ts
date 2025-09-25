import * as echarts from 'echarts';
import { useEffect, useRef } from 'react';
/**
 * @description
 * @param {Element} data
 * @param {Object} options
 * @return
 * */
export const useEcharts = (options: any, data?: any, isChange?: boolean, clickFn?: any) => {
	const myChart = useRef<any>();
	const echartsRef = useRef<HTMLDivElement>(null);
	const echartsResize = () => {
		echartsRef && myChart?.current?.resize();
	};

	useEffect(() => {
		if (data?.length !== 0) {
			myChart?.current?.setOption(options);
		}
	}, [data, isChange]);

	useEffect(() => {
		setTimeout(() => {
			echartsResize();
		}, 50);
	}, [isChange]);
	useEffect(() => {
		if (echartsRef?.current) {
			myChart.current = echarts.init(echartsRef.current);
		}
		myChart?.current?.setOption(options);
		window.addEventListener('resize', echartsResize, false);
		myChart?.current?.on('click', function (params: any) {
			if (clickFn) {
				const { evalUuid, index } = params.data;
				console.log(evalUuid);
				if (evalUuid) clickFn(evalUuid, index);
			}
		});

		return () => {
			window.removeEventListener('resize', echartsResize);
			myChart?.current?.dispose();
		};
	}, []);

	return [echartsRef];
};
