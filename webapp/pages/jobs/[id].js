import React, {useState, useEffect} from 'react';

import prisma from "../../prisma/client";
import {Panel} from "primereact/panel";
import {DataTable} from "primereact/datatable";
import {Column} from "primereact/column";
import Head from 'next/head';
import {hideEmail} from "../../utils/formattingUtils";
import {Button} from "primereact/button";
import {renderParams} from "../../utils/jobUtils";

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
            <div className="flex justify-content-between mb-2">
              <span className="font-medium">Dataset:</span>
              <span className="white-space-nowrap">{job.dataset.name}</span>
            </div>
            <div className="flex justify-content-between">
              <span className="font-medium">Filtering Algorithm:</span>
              <span className="white-space-nowrap">{job.filteringAlgo.name}</span>
            </div>
            <div className="flex justify-content-between mb-2">
              <span className="font-medium">Filtering Params:</span>
              <span className="white-space-nowrap">{renderParams(job.filteringParams)}</span>
            </div>
          </div>
        </div>
        <div className="col-6">
          <div className="flex flex-column gap-2">
            <div className="flex justify-content-between">
              <span className="font-medium">Matching Algorithm:</span>
              <span className="white-space-nowrap">{job.matchingAlgo.name}</span>
            </div>
            <div className="flex justify-content-between">
              <span className="font-medium">Matching Params:</span>
              <span className="white-space-nowrap">{renderParams(job.matchingParams)}</span>
            </div>
            {job.notifyEmail && (
              <div className="flex justify-content-between">
                <span className="font-medium">Notification Email:</span>
                <span className="white-space-nowrap">{job.notifyEmail}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid">
        <div className="col-6">
          <div className="flex flex-column gap-2">
            <div className="flex justify-content-between">
              <span className="font-medium">Created:</span>
              <span className="white-space-nowrap">{new Date(job.createdAt).toISOString()}</span>
            </div>
          </div>
        </div>
        <div className="col-6">
          <div className="flex flex-column gap-2">
            {job.result && (
              <div className="flex justify-content-between">
                <span className="font-medium">Completed:</span>
                <span className="white-space-nowrap">{new Date(job.result.updatedAt).toISOString()}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Panel>

    {job.result && (
      <Panel header="Filtering Results" className="mt-3">
        <div className="grid">
          <div className="col-6">
            <div className="flex flex-column gap-2">
              <div className="flex justify-content-between">
                <span className="font-medium">F1 Score:</span>
                <span>{job.result.filteringF1 !== null ? job.result.filteringF1.toFixed(6) : 'N/A'}</span>
              </div>
              <div className="flex justify-content-between">
                <span className="font-medium">Precision:</span>
                <span>{job.result.filteringPrecision !== null ? job.result.filteringPrecision.toFixed(6) : 'N/A'}</span>
              </div>
              <div className="flex justify-content-between">
                <span className="font-medium">Recall:</span>
                <span>{job.result.filteringRecall !== null ? job.result.filteringRecall.toFixed(6) : 'N/A'}</span>
              </div>
              {job.result.filteringTime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Filtering time:</span>
                  <span>{(Number(job.result.filteringTime) / 1000).toFixed(3)}s</span>
                </div>
              )}
            </div>
          </div>
          <div className="col-6">
            <div className="flex flex-column gap-2">
              {job.result.filteringCandidates !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Candidate Pairs:</span>
                  <span>{Number(job.result.filteringCandidates)}</span>
                </div>
              )}
              {job.result.filteringEntriesA !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Entities in Table A:</span>
                  <span>{Number(job.result.filteringEntriesA)}</span>
                </div>
              )}
              {job.result.filteringEntriesB !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Entities in Table B:</span>
                  <span>{Number(job.result.filteringEntriesB)}</span>
                </div>
              )}
              {job.result.filteringMatches !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Entities in Matches:</span>
                  <span>{Number(job.result.filteringMatches)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </Panel>
    )}

    {job.result && job.status === 'completed' && (
      <Panel header="Matching Results" className="mt-3">
        <div className="grid">
          <div className="col-6">
            <div className="flex flex-column gap-2">
              <div className="flex justify-content-between">
                <span className="font-medium">F1 Score:</span>
                <span>{job.result.f1 !== null ? job.result.f1.toFixed(6) : 'N/A'}</span>
              </div>
              <div className="flex justify-content-between">
                <span className="font-medium">Precision:</span>
                <span>{job.result.precision !== null ? job.result.precision.toFixed(6) : 'N/A'}</span>
              </div>
              <div className="flex justify-content-between">
                <span className="font-medium">Recall:</span>
                <span>{job.result.recall !== null ? job.result.recall.toFixed(6) : 'N/A'}</span>
              </div>
              {job.result.trainTime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Train time:</span>
                  <span>{(Number(job.result.trainTime) / 1000).toFixed(3)}s</span>
                </div>
              )}
              {job.result.evalTime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Evaluation time:</span>
                  <span>{(Number(job.result.evalTime) / 1000).toFixed(3)}s</span>
                </div>
              )}
              {job.result.totalRuntime !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Total Runtime:</span>
                  <span>{(Number(job.result.totalRuntime) / 1000).toFixed(3)}s</span>
                </div>
              )}
            </div>
          </div>
          <div className="col-6">
            <div className="flex flex-column gap-2">
              {job.result.cpuAllocated !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">CPUs Allocated:</span>
                  <span>{Number(job.result.cpuAllocated)}</span>
                </div>
              )}
              {job.result.cpuUtilized !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">CPU Usage (core-walltime):</span>
                  <span>{(Number(job.result.cpuUtilized) / 1000).toFixed(2)}s</span>
                </div>
              )}
              {job.result.memUtilized !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">CPU Memory:</span>
                  <span>{(Number(job.result.memUtilized) / 1024 / 1024 / 1024).toFixed(2)} GB</span>
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
                      <span>{Number(job.result.gpuUtilized)}s</span>
                    </div>
                  )}
                  {job.result.gpuMemUtilized !== null && (
                    <div className="flex justify-content-between">
                      <span className="font-medium">GPU Memory:</span>
                      <span>{(Number(job.result.gpuMemUtilized) / 1024).toFixed(2)} GB</span>
                    </div>
                  )}
                </>
              )}
              {job.result.energyConsumed !== null && (
                <div className="flex justify-content-between">
                  <span className="font-medium">Energy Consumed:</span>
                  <span>{Math.round(Number(job.result.energyConsumed) / 1000)} kJ</span>
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

