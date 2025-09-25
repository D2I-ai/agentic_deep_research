import { useEcharts } from "@/hooks/useEcharts";
import * as echarts from "echarts";
const LineChart = (props: any) => {
	const { width = '100%', height = '33.3%', seriesType, data, noData=false } = props
	const json: any = {
		'cpu': { name: 'CPU', key: 'cpu', color: 'rgba(66,86,181,.5)' },
		'gpu': { name: 'GPU', key: 'gpu', color: 'rgba(126,196,97,.5)' },
		'memory': { name: '内存', key: 'memory', color: 'rgba(240,190,81,.5)' },
	}
	let series:any = {
		name: 'CPU',
		type: 'line',
		symbolSize: 0,
		areaStyle: {},
		smooth: true,
		emphasis: { focus: 'series' },
		lineStyle: {},
		data: data.yAxis.cpu
	}
	series.name = json[seriesType].name
	series.areaStyle = { color: json[seriesType].color }
	series.lineStyle = {color: json[seriesType].color}
	series.data = data.yAxis[json[seriesType].key]
	let option: any = data.xAxis.length == 0 ? {
		title: {
			text: noData ? '暂无数据' : '',
			left: '43%',
			top: '40%'
		}
	} : {
		title: {
			text:'',
		},
		tooltip: {
			trigger: 'axis',
			axisPointer: {
				label: {
					backgroundColor: '#6a7985'
				}
			},
			formatter: function (params: any) {
				var relVal = params[0].name
				relVal += '<br/>' + params[0].marker + params[0].seriesName + ' : ' + params[0].value + '%'
				return relVal
			}
		},
		legend: {
			data: ['CPU', 'GPU', '内存'],
			right: '4px',
			top: '-2px'
		},
		grid: {
			left: '10px',
			right: '6%',
			bottom: '10px',
			top: '10%',
			containLabel: true
		},
		xAxis: {
			type: 'category',
			boundaryGap: false,
			inverse: true,
			data: data.xAxis
		},
		dataZoom: [
			{
			  type: 'inside',
			  start: 0,
			  end: 100
			}
		  ],
		yAxis: [
			{
				type: 'value',
				max: 100,
				axisLabel: {
					formatter: '{value}%'
				}
			}
		],
		series: [series]
	};

	const [echartsRef] = useEcharts(option,data);
	return <div ref={echartsRef} className="chart" style={{ width: width, height: height }}></div>;
};

export default LineChart;
