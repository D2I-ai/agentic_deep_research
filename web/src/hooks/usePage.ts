import { useState } from "react";

export default function usePage() {
  const [originData, setOriginData] = useState<any>([]);
  const [record, setRecord] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState(false);
  const [Query, setQuery] = useState<any>({name:null});
  const [pagination, setPagination] = useState({
    total: 0,
    pageStart: 1,
    pageSize: 10,
    showSizeChanger: true,
    showTotal:(total:number) => `共 ${total} 条`
  });
  const onChange = (page: any) => {
    setPagination((prev) => {
      return {
        ...prev,
        ...page,
        pageStart: page.current,
      };
    });
  };
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    console.log("selectedRowKeys changed: ", newSelectedRowKeys);
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection:any = {
    selectedRowKeys,
    onChange: onSelectChange,
  };
  const btnItems = [
    {
      label: "批量添加",
      key: "1",
    },
    {
      label: "批量下载",
      key: "2",
    },
    {
      label: "批量删除",
      key: "3",
    },
  ];
  return {
    originData,
    setOriginData,
    record,
    setRecord,
    open,
    setOpen,
    edit,
    setEdit,
    pagination,
    setPagination,
    btnItems,
    onChange,
    selectedRowKeys,
    rowSelection,
    Query,
    setQuery,
  };
}
