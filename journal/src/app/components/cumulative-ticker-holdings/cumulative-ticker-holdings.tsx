"use client";
import {
  Table,
  TableBody,
  TableCell,
  TableFoot,
  TableFooterCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from "@tremor/react";

import React, { useEffect, useState } from "react";

import "./cumulative-ticker-holdings.css";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { DEFAULT_NUMBER_FORMAT_OPTIONS } from "../../constants";
import mApi from "../../utils/m-api";

type CumulativeTickerHolding = {
  id: number;
  ticker: {
    id: number;
    title: string;
    code: string;
    market: {
      id: number;
      title: string;
      code: string;
      currency: {
        id: number;
        title: string;
        code: string;
        symbol: string;
      };
    };
  };
  investment_account: {
    id: number;
    title: string;
    owner: {
      id: number;
      first_name: string;
      last_name: string;
      email: string;
    };
  };
  avg_cost: number;
  count: number;
  total_buys: number;
  total_sells: number;
  total_buy_amount: number;
  total_sell_amount: number;
  is_completed: boolean;
  adjusted_avg_cost: number;
  pnl_amount: number;
  pnl_ratio: number;
  first_transaction_at: string;
  last_transaction_at: string;
};

const defaultColumns: ColumnDef<CumulativeTickerHolding>[] = [
  {
    accessorFn: (row) => row.ticker,
    id: "Ticker",
    cell: (info) => (info.getValue() as any).code,
  },
  {
    accessorFn: (row) => row.ticker,
    id: "Market",
    cell: (info) => (info.getValue() as any).market.code,
  },
  {
    accessorFn: (row) => row.is_completed,
    id: "Status",
    cell: (info) => (info.getValue() ? "Completed" : "Open"),
  },

  {
    header: "Numbers",
    columns: [
      {
        accessorFn: (row) =>
          `${row.avg_cost.toLocaleString(
            undefined,
            DEFAULT_NUMBER_FORMAT_OPTIONS
          )} ${row.ticker.market.currency.code}`,
        id: "Avg Cost",
      },
      {
        accessorFn: (row) => row.count.toFixed(2),
        id: "Count",
      },
      {
        accessorFn: (row) => row.total_buys.toFixed(2),
        id: "Total Buys",
      },
      {
        accessorFn: (row) => row.total_sells.toFixed(2),
        id: "Total Sells",
      },
      {
        accessorFn: (row) =>
          `${row.total_buy_amount.toLocaleString(
            undefined,
            DEFAULT_NUMBER_FORMAT_OPTIONS
          )} ${row.ticker.market.currency.code}`,
        id: "Total Buy Amount",
      },
      {
        accessorFn: (row) =>
          `${row.total_sell_amount.toLocaleString(
            undefined,
            DEFAULT_NUMBER_FORMAT_OPTIONS
          )} ${row.ticker.market.currency.code}`,
        id: "Total Sell Amount",
      },
      {
        accessorFn: (row) =>
          row.pnl_amount
            ? `${row.pnl_amount.toLocaleString(
                undefined,
                DEFAULT_NUMBER_FORMAT_OPTIONS
              )} ${row.ticker.market.currency.code}`
            : "-",
        id: "PnL Amount",
      },
      {
        accessorFn: (row) =>
          row.pnl_ratio
            ? `${(row.pnl_ratio * 100).toLocaleString(
                undefined,
                DEFAULT_NUMBER_FORMAT_OPTIONS
              )} %`
            : "-",
        id: "PnL %",
      },
      {
        accessorFn: (row) =>
          new Date(`${row.first_transaction_at}Z`).toLocaleDateString("tr-TR"),
        id: "First Transaction At",
      },
      {
        accessorFn: (row) =>
          row.last_transaction_at
            ? new Date(`${row.last_transaction_at}Z`).toLocaleDateString(
                "tr-TR"
              )
            : "-",
        id: "Last Transaction At",
      },
    ],
  },

  {
    header: "Account",
    columns: [
      {
        accessorFn: (row) => row.investment_account.title,
        id: "Title",
      },
      {
        accessorFn: (row) => row.investment_account.owner.email,
        id: "Owner Email",
      },
      {
        accessorFn: (row) => row.investment_account.owner,
        id: "Owner Name",
        cell: (info) =>
          info.getValue().first_name + " " + info.getValue().last_name,
      },
    ],
  },
];

export interface CumulativeTickerHoldingsProps {
  page: number;
}

export default function CumulativeTickerHoldings({
  page = 1,
}: CumulativeTickerHoldingsProps) {
  const [tableData, setTableData] = useState<CumulativeTickerHolding[]>([]);
  const [columns] = useState<typeof defaultColumns>(() => [...defaultColumns]);
  const [columnVisibility, setColumnVisibility] = React.useState({});

  const table = useReactTable({
    data: tableData,
    columns,
    state: {
      columnVisibility,
    },
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  });

  useEffect(() => {
    mApi.get("/journal/cumulative_ticker_holdings").then((response) => {
      setTableData(response.data as unknown as CumulativeTickerHolding[]);

      let total = 0;
      (response.data as unknown as CumulativeTickerHolding[]).forEach((element) => {
        console.log(element.pnl_amount);
        total += element.pnl_amount || 0;
      });

      console.log(
        "nanemolla",
        total.toLocaleString(),
      );
    });
  }, [table, columns]);
  return (
    <>
      {tableData.length === 0 && <>Loading...</>}
      {tableData.length > 0 && (
        <div className="p-2">
          <div className="inline-block border border-black shadow rounded">
            <div className="px-1 border-b border-black">
              <label>
                <input
                  {...{
                    type: "checkbox",
                    checked: table.getIsAllColumnsVisible(),
                    onChange: table.getToggleAllColumnsVisibilityHandler(),
                  }}
                />{" "}
                Toggle All
              </label>
            </div>
            {table.getAllLeafColumns().map((column) => {
              return (
                <div key={column.id} className="px-1">
                  <label>
                    <input
                      {...{
                        type: "checkbox",
                        checked: column.getIsVisible(),
                        onChange: column.getToggleVisibilityHandler(),
                      }}
                    />{" "}
                    {column.id}
                  </label>
                </div>
              );
            })}
          </div>
          <div className="h-4" />

          <Table>
            <TableHead>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHeaderCell key={header.id} colSpan={header.colSpan}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHeaderCell>
                  ))}
                </TableRow>
              ))}
            </TableHead>
            <TableBody>
              {table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>

            <TableFoot>
              {table.getFooterGroups().map((footerGroup) => (
                <TableRow key={footerGroup.id}>
                  {footerGroup.headers.map((header) => (
                    <TableFooterCell key={header.id} colSpan={header.colSpan}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.footer,
                            header.getContext()
                          )}
                    </TableFooterCell>
                  ))}
                </TableRow>
              ))}
            </TableFoot>
          </Table>
        </div>
      )}
    </>
  );
}
