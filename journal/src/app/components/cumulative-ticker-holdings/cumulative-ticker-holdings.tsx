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
import { useRouter, useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";

import "./cumulative-ticker-holdings.css";

import {
  ColumnDef,
  ColumnFiltersState,
  FilterFn,
  SortingState,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { DEFAULT_NUMBER_FORMAT_OPTIONS } from "../../constants";
import mApi from "../../utils/m-api";
declare module "@tanstack/table-core" {
  interface FilterFns {
    fuzzy: FilterFn<unknown>;
  }
}
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
  total_commission_cost: number;
  is_completed: boolean;
  adjusted_avg_cost: number;
  pnl_amount: number;
  pnl_ratio: number;
  first_transaction_at: string;
  last_transaction_at: string;
};

const defaultColumns: ColumnDef<CumulativeTickerHolding>[] = [
  {
    header: " ",
    columns: [
      {
        accessorFn: (row) => row.ticker,
        id: "ticker_code",
        header: () => "Ticker",
        cell: (info) => (info.getValue() as any).code,
        enableSorting: true,
        enableMultiSort: true,
        enableColumnFilter: true,
      },
      {
        accessorFn: (row) => row.ticker,
        id: "market_code",
        header: () => "Market",
        cell: (info) => (info.getValue() as any).market.code,
        enableSorting: false,
        enableColumnFilter: true,
      },
      {
        accessorFn: (row) => row.is_completed,
        id: "status",
        header: () => "Status",
        cell: (info) => (info.getValue() ? "Completed" : "Open"),
        enableSorting: false,
        enableColumnFilter: true,
      },
    ],
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
        id: "avg_cost",
        header: () => "Avg Cost",
        enableColumnFilter: false,
        enableSorting: false,
      },
      {
        accessorFn: (row) => row.count.toFixed(2),
        id: "count",
        header: () => "Count",
        enableColumnFilter: false,
        enableSorting: false,
      },
      {
        accessorFn: (row) => row.total_buys.toFixed(2),
        id: "Total Buys",
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) => row.total_sells.toFixed(2),
        id: "Total Sells",
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          `${row.total_buy_amount.toLocaleString(
            undefined,
            DEFAULT_NUMBER_FORMAT_OPTIONS
          )} ${row.ticker.market.currency.code}`,
        id: "total_buy_amount",
        header: () => "Total Buy Amount",
        enableSorting: true,
        enableMultiSort: true,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          `${row.total_sell_amount.toLocaleString(
            undefined,
            DEFAULT_NUMBER_FORMAT_OPTIONS
          )} ${row.ticker.market.currency.code}`,
        id: "total_sell_amount",
        header: () => "Total Sell Amount",
        enableSorting: true,
        enableMultiSort: true,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          `${row.total_commission_cost.toLocaleString(
            undefined,
            DEFAULT_NUMBER_FORMAT_OPTIONS
          )} ${row.ticker.market.currency.code}`,
        id: "total_commission_cost",
        header: () => "Total Comm.",
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          row.pnl_amount
            ? `${row.pnl_amount.toLocaleString(
                undefined,
                DEFAULT_NUMBER_FORMAT_OPTIONS
              )} ${row.ticker.market.currency.code}`
            : "-",
        id: "pnl_amount",
        header: () => "PnL",
        enableSorting: true,
        enableMultiSort: true,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          row.pnl_ratio
            ? `${(row.pnl_ratio * 100).toLocaleString(
                undefined,
                DEFAULT_NUMBER_FORMAT_OPTIONS
              )} %`
            : "-",
        id: "pnl_ratio",
        header: () => "PnL %",
        enableSorting: true,
        enableMultiSort: true,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          new Date(`${row.first_transaction_at}Z`).toLocaleDateString("tr-TR"),
        id: "First Transaction At",
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) =>
          row.last_transaction_at
            ? new Date(`${row.last_transaction_at}Z`).toLocaleDateString(
                "tr-TR"
              )
            : "-",
        id: "Last Transaction At",
        enableSorting: false,
        enableColumnFilter: false,
      },
    ],
  },

  {
    header: "Account",
    columns: [
      {
        accessorFn: (row) => row.investment_account.title,
        id: "account_title",
        header: () => "Title",
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) => row.investment_account.owner.email,
        id: "owner_email",
        header: () => "Owner Email",
        enableSorting: false,
        enableColumnFilter: false,
      },
      {
        accessorFn: (row) => row.investment_account.owner,
        id: "owner_name",
        header: () => "Owner Name",
        enableSorting: false,
        cell: (info) =>
          info.getValue().first_name + " " + info.getValue().last_name,
        enableColumnFilter: false,
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
  const [columnVisibility, setColumnVisibility] = useState({
    "Total Buys": false,
    "Total Sells": false,
    total_commission_cost: false,
    account_title: false,
    owner_email: false,
    owner_name: false,
    avg_cost: false,
    count: false,
  });
  const [sorting, setSorting] = useState<SortingState>([]);

  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  );
  const [globalFilter, setGlobalFilter] = React.useState("");

  const table = useReactTable({
    data: tableData,
    columns,
    state: {
      columnVisibility,
      sorting,
      columnFilters,
      globalFilter,
    },
    filterFns: {
      fuzzy: undefined,
    },
    onColumnFiltersChange: setColumnFilters,
    onSortingChange: setSorting,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  });

  const generateOrderingString = () => {
    return sorting.map((sort) => `${sort.desc ? "-" : ""}${sort.id}`).join(",");
  };

  const fetchTableData = async () => {
    const filterParams = columnFilters
      .map((f) => {
        return [f.id.toLowerCase(), f.value];
      })
      .reduce((acc, [key, value]) => {
        if (key === "status") {
          if ((value as string).toLowerCase() === "completed") {
            acc["is_completed"] = true;
          } else if ((value as string).toLowerCase() === "open") {
            acc["is_completed"] = false;
          }
        } else {
          acc[key as string] = value;
        }
        return acc;
      }, {} as any);

    mApi
      .get("/journal/cumulative_ticker_holdings", {
        params: {
          ordering: generateOrderingString(),
          ...filterParams,
        },
      })
      .then((response) => {
        setTableData(response.data as unknown as CumulativeTickerHolding[]);
      });
  };

  const router = useRouter();
  const searchParams = useSearchParams();
  useEffect(() => {
    fetchTableData();
  }, [sorting, columnFilters]);

  return (
    <>
      {
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
                      {header.isPlaceholder ? null : (
                        <div
                          {...{
                            className: header.column.getCanSort()
                              ? "cursor-pointer select-none"
                              : "",

                            onClick: () => {
                              header.column.toggleSorting(undefined, true);
                            },
                          }}
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          {{
                            asc: " ▲",
                            desc: " ▼",
                          }[
                            header.column.getCanSort()
                              ? (header.column.getIsSorted() as string)
                              : "null"
                          ] ?? null}
                        </div>
                      )}

                      {header.column.getCanFilter() ? (
                        <div>
                          <Filter column={header.column} table={table} />
                        </div>
                      ) : null}
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
      }
    </>
  );
}

function Filter({
  column,
  table,
}: {
  column: Column<any, unknown>;
  table: Table<any>;
}) {
  const columnFilterValue = column.getFilterValue();
  return (
    <>
      <DebouncedInput
        type="text"
        value={(columnFilterValue ?? "") as string}
        onChange={(value) => {
          column.setFilterValue(value);
        }}
        placeholder={"Filter..."}
        className="w-24 border shadow rounded"
      />
    </>
  );
}

// A debounced input react component
function DebouncedInput({
  value: initialValue,
  onChange,
  debounce = 500,
  ...props
}: {
  value: string | number;
  onChange: (value: string | number) => void;
  debounce?: number;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange">) {
  const [value, setValue] = React.useState(initialValue);

  React.useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  React.useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(value);
    }, debounce);

    return () => clearTimeout(timeout);
  }, [value]);

  return (
    <input
      {...props}
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
}
