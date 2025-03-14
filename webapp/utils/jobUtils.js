import React from 'react';
import {Tag} from "primereact/tag";
import {capitalize} from "./formattingUtils";
import {Dropdown} from "primereact/dropdown";

const getSeverity = (status) => {
  const severityMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  };

  return severityMap[status] || 'contrast';
}

const statusItemTemplate = (option) => {
  return <Tag value={capitalize(option)} severity={getSeverity(option)}/>;
};

export const renderStatusTemplate = (rowData) => {
  return statusItemTemplate(rowData.status);
};

export const statusRowFilterTemplate = (options, statuses) => {
  return <Dropdown value={options.value} options={statuses} placeholder="Select One" className="p-column-filter" showClear
                   onChange={(e) => options.filterApplyCallback(e.value)} itemTemplate={statusItemTemplate}/>;
};

export const dropdownFilterTemplate = (options, possibleOptions) => {
  return <Dropdown value={options.value} options={possibleOptions} placeholder="Select One" className="p-column-filter" showClear
                   onChange={(e) => options.filterApplyCallback(e.value)}/>;
};

export const renderParams = (params) => {
  return (
    <div className="flex flex-col gap-2">
      {Object.entries(params).map(([key, value]) => {
        return <div key={key} className="flex gap-2">
          <span>{key}</span>
          <span className="font-medium">{value}</span>
        </div>
      })}
    </div>
  );
};

export const renderDate = (dateString) => {
  if (!dateString) return '';

  const date = new Date(dateString);
  return date.toISOString().replace('T', ' ').substring(0, 19);
}
