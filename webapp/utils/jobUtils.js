import React from 'react';
import {Tag} from "primereact/tag";
import {capitalize} from "./formattingUtils";
import {Dropdown} from "primereact/dropdown";

const getSeverity = (status) => {
  const severityMap = {
    pending: 'secondary',
    queued: 'info',
    filtering: 'warning',
    matching: 'warning',
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
  const sortedOptions = possibleOptions ? [...possibleOptions].sort((a, b) => a.localeCompare(b)) : [];
  return <Dropdown value={options.value} options={sortedOptions} placeholder="Select One" className="p-column-filter" showClear
                   onChange={(e) => options.filterApplyCallback(e.value)}/>;
};

export const renderNameAndParams = (name, params) => {
  return (
    <>
      <div>{name}</div>
      <div className="flex flex-column text-xs">
        {Object.entries(params).map(([key, value]) => {
          return <div key={key} className="flex gap-2">
            <span className="font-medium">{key}</span>
            <span>{value}</span>
          </div>
        })}
      </div>
    </>
  );
};

export const renderParams = (params) => {
  return (
    <div className="flex flex-column">
      {Object.entries(params).map(([key, value]) => {
        return <div key={key} className="flex justify-content-between gap-2">
          <span>{key}</span>
          <span className="font-medium">{value}</span>
        </div>
      })}
    </div>
  );
};

export const renderFilteringResults = (result) => {
  return result ? (
    <div className="flex flex-column text-xs">
      <div className="flex justify-content-between">
        <span className="font-medium">F1 Score:</span>
        <span className="white-space-nowrap">{result.filteringF1 !== null ? result.filteringF1.toFixed(3) : 'N/A'}</span>
      </div>
      <div className="flex justify-content-between">
        <span className="font-medium">Precision:</span>
        <span className="white-space-nowrap">{result.filteringPrecision !== null ? result.filteringPrecision.toFixed(3) : 'N/A'}</span>
      </div>
      <div className="flex justify-content-between">
        <span className="font-medium">Recall:</span>
        <span className="white-space-nowrap">{result.filteringRecall !== null ? result.filteringRecall.toFixed(3) : 'N/A'}</span>
      </div>
      {result.filteringTime !== null && (
        <div className="flex justify-content-between">
          <span className="font-medium">Filtering time:</span>
          <span className="white-space-nowrap">{(Number(result.filteringTime) / 1000).toFixed(3)}s</span>
        </div>
      )}
    </div>
  ) : null;
};

export const renderResults = (result) => {
  return result ? (
    <div className="flex flex-column text-xs">
      <div className="flex justify-content-between">
        <span className="font-medium">F1 Score:</span>
        <span className="white-space-nowrap">{result.f1 !== null ? result.f1.toFixed(3) : 'N/A'}</span>
      </div>
      <div className="flex justify-content-between">
        <span className="font-medium">Precision:</span>
        <span className="white-space-nowrap">{result.precision !== null ? result.precision.toFixed(3) : 'N/A'}</span>
      </div>
      <div className="flex justify-content-between">
        <span className="font-medium">Recall:</span>
        <span className="white-space-nowrap">{result.recall !== null ? result.recall.toFixed(3) : 'N/A'}</span>
      </div>
      {result.trainTime !== null && (
        <div className="flex justify-content-between">
          <span className="font-medium">Train time:</span>
          <span className="white-space-nowrap">{(Number(result.trainTime) / 1000).toFixed(2)}s</span>
        </div>
      )}
      {result.evalTime !== null && (
        <div className="flex justify-content-between">
          <span className="font-medium">Evaluation time:</span>
          <span className="white-space-nowrap">{(Number(result.evalTime) / 1000).toFixed(2)}s</span>
        </div>
      )}
      {result.totalRuntime !== null && (
        <div className="flex justify-content-between">
          <span className="font-medium">Total Runtime:</span>
          <span className="white-space-nowrap">{(Number(result.totalRuntime) / 1000).toFixed(0)}s</span>
        </div>
      )}
      {result.memUtilized !== null && (
        <div className="flex justify-content-between">
          <span className="font-medium">CPU Memory:</span>
          <span className="white-space-nowrap">{(Number(result.memUtilized) / 1024 / 1024 / 1024).toFixed(2)} GB</span>
        </div>
      )}
      {result.gpuAllocated && result.gpuMemUtilized !== null && (
        <div className="flex justify-content-between">
          <span className="font-medium">GPU Memory:</span>
          <span className="white-space-nowrap">{(Number(result.gpuMemUtilized) / 1024).toFixed(2)} GB</span>
        </div>
      )}
    </div>
  ) : null;
};

export const renderDate = (dateString) => {
  if (!dateString) return '';

  const date = new Date(dateString);
  return date.toISOString().replace('T', ' ').substring(0, 19);
}
