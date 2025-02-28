import React, {useState} from 'react';

import prisma from "../../prisma/client";
import {Panel} from "primereact/panel";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";

const capitalize = s => s && String(s[0]).toUpperCase() + String(s).slice(1);

const hideEmail = email => {
  if (!email) return '';
  const [localPart, domain] = email.split('@');
  return `${localPart.substring(0, 3)}***@${domain}`;
};

BigInt.prototype.toJSON = function () {
  const int = Number.parseInt(this.toString());
  return int ?? this.toString();
};

export const getServerSideProps = async ({query}) => {
  const {id} = query;

  const job = await prisma.job.findFirst({
    where: {
      id: id,
    },
    include: {
      filteringAlgo: true,
      matchingAlgo: true,
      dataset: true,
      result: true,
      predictions: true,
    }
  });

  job.notifyEmail = hideEmail(job.notifyEmail);

  return {
    props: {
      job: JSON.parse(JSON.stringify(job)),
    }
  }
}

export default function ViewJob({job}) {
  if (!job) {
    return <div>
      <h1 className="text-4xl font-bold">Job not found</h1>
    </div>
  }

  return <div>
    <h1 className="text-4xl font-bold"><span style={{color: '#777', fontWeight: 'normal'}}>Job:</span> {job.id}</h1>

    <Panel header={"Status: " + job.status}>
      <div className="grid">
        <div className="col-6">
          <div className="flex flex-column gap-2">
            <div className="flex justify-content-between">
              <span className="font-medium">Dataset:</span>
              <span>{job.dataset.name}</span>
            </div>
            <div className="flex justify-content-between">
              <span className="font-medium">Filtering Algorithm:</span>
              <span>{job.filteringAlgo.name}</span>
            </div>
            <div className="flex justify-content-between">
              <span className="font-medium">Matching Algorithm:</span>
              <span>{job.matchingAlgo.name}</span>
            </div>
            <div className="flex justify-content-between">
              <span className="font-medium">Created:</span>
              <span>{new Date(job.createdAt).toISOString()}</span>
            </div>
            {job.result && (
              <div className="flex justify-content-between">
                <span className="font-medium">Completed At:</span>
                <span>{new Date(job.result.createdAt).toISOString()}</span>
              </div>
            )}
          </div>
        </div>
        <div className="col-6">
          <div className="flex flex-column gap-2">
            {job.filteringParams.recall && (
              <div className="flex justify-content-between">
                <span className="font-medium">Filtering Recall:</span>
                <span>{job.filteringParams.recall}</span>
              </div>
            )}
            {job.filteringParams.epochs && (
              <div className="flex justify-content-between">
                <span className="font-medium">Filtering Epochs:</span>
                <span>{job.filteringParams.epochs}</span>
              </div>
            )}
            {job.matchingParams.recall && (
              <div className="flex justify-content-between">
                <span className="font-medium">Matching Recall:</span>
                <span>{job.matchingParams.recall}</span>
              </div>
            )}
            {job.matchingParams.epochs && (
              <div className="flex justify-content-between">
                <span className="font-medium">Matching Epochs:</span>
                <span>{job.matchingParams.epochs}</span>
              </div>
            )}
            {job.notifyEmail && (
              <div className="flex justify-content-between">
                <span className="font-medium">Notification Email:</span>
                <span>{job.notifyEmail}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Panel>

    {job.result && (
      <Panel header="Results" className="mt-3">
        <div className="grid">
          <div className="col-6">
            <div className="flex flex-column gap-2">
              <div className="flex justify-content-between">
                <span className="font-medium">F1 Score:</span>
                <span>{job.result.f1 !== null ? job.result.f1.toFixed(4) : 'N/A'}</span>
              </div>
              <div className="flex justify-content-between">
                <span className="font-medium">Precision:</span>
                <span>{job.result.precision !== null ? job.result.precision.toFixed(4) : 'N/A'}</span>
              </div>
              <div className="flex justify-content-between">
                <span className="font-medium">Recall:</span>
                <span>{job.result.recall !== null ? job.result.recall.toFixed(4) : 'N/A'}</span>
              </div>
              {job.result.trainTime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Train time:</span>
                  <span>{(Number(job.result.trainTime) / 1000).toFixed(2)}s</span>
                </div>
              )}
              {job.result.evalTime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Evaluation time:</span>
                  <span>{(Number(job.result.evalTime) / 1000).toFixed(2)}s</span>
                </div>
              )}
              <div className="flex justify-content-between">
                <span className="font-medium">Total Runtime:</span>
                <span>{job.result.totalRuntime}</span>
              </div>
            </div>
          </div>
          <div className="col-6">
            <div className="flex flex-column gap-2">
              {job.result.cpuUtilized !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">CPU Usage (walltime):</span>
                  <span>{(Number(job.result.cpuUtilized) / 1000000000).toFixed(2)}s</span>
                </div>
              )}
              {job.result.memUtilized !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Memory Usage:</span>
                  <span>{Math.round(Number(job.result.memUtilized) / 1024 / 1024)}MB</span>
                </div>
              )}
              {job.result.gpuAllocated && (
                <>
                  <div className="flex justify-content-between">
                    <span className="font-medium">GPUs Allocated:</span>
                    <span>{Number(job.result.gpuAllocated)}</span>
                  </div>
                  {job.result.gpuUtilized !== null && (
                    <div className="flex justify-content-between">
                      <span className="font-medium">GPU Usage:</span>
                      <span>{(Number(job.result.gpuUtilized) / 1000000000).toFixed(2)}s</span>
                    </div>
                  )}
                  {job.result.gpuMemUtilized !== null && (
                    <div className="flex justify-content-between">
                      <span className="font-medium">GPU Memory:</span>
                      <span>{job.result.gpuMemUtilized}MB</span>
                    </div>
                  )}
                </>
              )}
              {job.result.energyConsumed !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Energy Consumed:</span>
                  <span>{job.result.energyConsumed}J</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Panel>
    )}

    {(job.result && job.predictions) && (
      <Panel header="Predictions" className="mt-3 p-panel-no-padding">
        <DataTable value={job.predictions} stripedRows size="small" emptyMessage={"No predictions returned"}>
          <Column field="tableA_id" header="Table A (ID)"/>
          <Column field="tableB_id" header="Table B (ID)"/>
          <Column field="probability" header="Match Probability"/>
        </DataTable>
      </Panel>
    )}
  </div>
}

