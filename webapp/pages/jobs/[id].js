import React, {useState, useEffect} from 'react';

import prisma from "../../prisma/client";
import {Panel} from "primereact/panel";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import Head from 'next/head';
import {hideEmail} from "../../utils/formattingUtils";
import {Button} from "primereact/button";

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
  const [predictions, setPredictions] = useState(null);
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [totalPredictions, setTotalPredictions] = useState(0);
  const [predictionsState, setPredictionsState] = useState({
    first: 0,
    rows: 20,
    page: 1,
    sortField: 'probability',
    sortOrder: 1,
    filters: {
      tableA_id: {value: '', matchMode: 'equals'},
      tableB_id: {value: '', matchMode: 'equals'},
      probability: {value: '', matchMode: 'gte'},
    }
  });

  useEffect(() => {
    loadLazyPredictions();
  }, [predictionsState]);

  const loadLazyPredictions = async () => {
    setLoadingPredictions(true);
    try {
      const response = await fetch(`/api/jobs/${job.id}/predictions/query`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(predictionsState)
      });
      const results = await response.json();
      setPredictions(results.data);
      setTotalPredictions(results.page.total);
    } catch (error) {
      console.error("Failed to load predictions:", error);
    } finally {
      setLoadingPredictions(false);
    }
  };

  const setPredictionsStateAndResetPage = (e) => {
    e.first = 0;
    setPredictionsState(e);
  }

  const idFilterOptions = [
    {label: 'Contains', value: 'contains'},
    {label: 'Equals', value: 'equals'}
  ];

  const probabilityFilterOptions = [
    {label: 'Greater than or equal to', value: 'gte'},
    {label: 'Less than or equal to', value: 'lte'},
    {label: 'Equals', value: 'equals'}
  ];

  if (!job) {
    return <div>
      <h1 className="text-4xl font-bold">Job not found</h1>
    </div>
  }

  const predictionsFooter = (
    <div className="flex justify-content-between align-items-center">
      <div>Total predictions: {totalPredictions}</div>
      <Button type="button" size="small" icon="pi pi-file-export" rounded data-pr-tooltip="Export to CSV"
              onClick={() => window.open(`/api/jobs/${job.id}/predictions/csv`, '_blank')}/>
    </div>
  );

  return <div>
    <Head>
      <title>Job: {job.id} | ERBench</title>
      <meta name="description" content={`Job ${job.id} details, including status, parameters, and results.`}/>
    </Head>

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
              {job.result.totalRuntime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Total Runtime:</span>
                  <span>{job.result.totalRuntime}</span>
                </div>
              )}
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

    {job.status === 'completed' && (
      <Panel header="Predictions" footer={predictionsFooter} className="mt-3 p-panel-no-padding">
        <DataTable value={predictions} lazy stripedRows size="small" emptyMessage={"No predictions returned"} loading={loadingPredictions}
                   paginator first={predictionsState.first} rows={predictionsState.rows} totalRecords={totalPredictions}
                   sortField={predictionsState.sortField} sortOrder={predictionsState.sortOrder}
                   filters={predictionsState.filters} filterDisplay="row" filterDelay={500} onFilter={setPredictionsStateAndResetPage}
                   onPage={setPredictionsState} onSort={setPredictionsState}>
          <Column field="tableA_id" header="Table A (ID)" sortable filter filterPlaceholder="Filter results" filterMatchModeOptions={idFilterOptions}/>
          <Column field="tableB_id" header="Table B (ID)" sortable filter filterPlaceholder="Filter results" filterMatchModeOptions={idFilterOptions}/>
          <Column field="probability" header="Probability" sortable filter filterPlaceholder="Filter results"
                  filterMatchModeOptions={probabilityFilterOptions}/>
        </DataTable>
      </Panel>
    )}
  </div>
}

