import React, { useEffect, useState } from "react";
import type { TableProps } from "antd";
import { Table, Form } from "antd";
type TableRowSelection<T extends object = object> =
  TableProps<T>["rowSelection"];

const TableComponent = ({
  data,
  columns,
  EditableCell,
  form,
  pagination,
  onChange,
  rowKey='id',
  check=true,
  rowSelection,
  backgroundColor="#f3f3f6"
}: any) => {

  return (
    <>
      <Form form={form} component={false}>
        <Table
          rowKey={rowKey}
          rowSelection={check ? rowSelection : undefined}
          components={{
            body: {
              cell: EditableCell,
            },
            header: {
              cell: ({ children }: any) => (
                <th
                  style={{ backgroundColor, padding: "10px 16px" }}
                >
                  {children}
                </th>
              ),
            },
          }}
          bordered
          dataSource={data}
          columns={columns}
          rowClassName="editable-row"
          pagination={pagination}
          onChange={onChange}
        />
      </Form>
    </>
  );
};

export default TableComponent;
