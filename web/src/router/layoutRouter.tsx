import DeepResearchAi from '@/views/DeepResearchAi'

const item = [
  {
    path: "",
    meta: {
      title: "menu.home",
      key: "0",
    },
    children: [
      {
        path: "/",
        meta: {
          title: "DeepResearch",
        },
        component: DeepResearchAi,
      }
    ],
  },
];

export default item;
