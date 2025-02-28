import React from 'react';
import { ProgressBar } from 'primereact/progressbar';

export const renderStatusTemplate = (rowData) => {
  let classNames = '';
  let progress = 0;

  if (rowData.status === 'completed') {
    progress = 100;
    classNames = 'p-progressbar-success';
  } else if (rowData.status === 'failed') {
    progress = 100;
    classNames = 'p-progressbar-failed';
  } else if (rowData.status === 'running') {
    progress = 30;
  }

  return (
    <React.Fragment>
      <ProgressBar value={progress} showValue={false} className={classNames}/>
    </React.Fragment>
  );
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
