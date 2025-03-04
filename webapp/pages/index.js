import React, {useState} from 'react';
import {useRouter} from 'next/navigation';
import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {Button} from 'primereact/button';
import {RadioButton} from 'primereact/radiobutton';
import {InputNumber} from 'primereact/inputnumber';
import {Dropdown} from 'primereact/dropdown';
import {InputText} from "primereact/inputtext";

import prisma from "../prisma/client";
import {Checkbox} from "primereact/checkbox";
import {renderParams} from "../utils/jobUtils";

export const getServerSideProps = async ({req}) => {
  const algorithms = await prisma.algorithm.findMany();
  const datasets = await prisma.dataset.findMany();

  return {
    props: {
      algorithms: JSON.parse(JSON.stringify(algorithms)),
      datasets: JSON.parse(JSON.stringify(datasets)),
    }
  }
}

export default function Home({datasets, algorithms}) {
  const router = useRouter();
  const filteringRecallOptions = [0.65, 0.75, 0.85];

  // fields
  const [selectedDataset, setSelectedDataset] = useState(datasets[0]);
  const [selectedFilteringAlgo, setSelectedFilteringAlgo] = useState(algorithms.find(algo => algo.scenarios.includes('filtering')));
  const [filteringRecall, setFilteringRecall] = useState(filteringRecallOptions[0]);
  const [filteringEpochs, setFilteringEpochs] = useState(5);
  const [selectedMatchingAlgo, setSelectedMatchingAlgo] = useState(algorithms.find(algo => algo.scenarios.includes('matching')));
  const [matchingRecall, setMatchingRecall] = useState(0.85);
  const [matchingEpochs, setMatchingEpochs] = useState(10);
  const [email, setEmail] = useState('');

  // state
  const [isLoading, setLoading] = useState(false);
  const [formDisabled, setDisabled] = useState(false);

  // data
  const [results, setResults] = useState([]);
  const [forceSubmit, setForceSubmit] = useState(false);
  const [job, setJob] = useState(null);

  const onSubmit = (e) => {
    setDisabled(true);

    let filteringParams = {};
    if (selectedFilteringAlgo.params.includes('recall')) {
      filteringParams.recall = filteringRecall;
    }
    if (selectedFilteringAlgo.params.includes('epochs')) {
      filteringParams.epochs = filteringEpochs;
    }

    let matchingParams = {};
    if (selectedMatchingAlgo.params.includes('recall')) {
      matchingParams.recall = matchingRecall;
    }
    if (selectedMatchingAlgo.params.includes('epochs')) {
      matchingParams.epochs = matchingEpochs;
    }

    fetch('/api/submit', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        datasetId: selectedDataset.id,
        filteringAlgoId: selectedFilteringAlgo.id,
        filteringParams: filteringParams,
        matchingAlgoId: selectedMatchingAlgo.id,
        matchingParams: matchingParams,
        notifyEmail: email,
      })
    })
      .then((res) => {
        return res.json().then((data) => {
          console.log(res, data);

          if (res.status === 201) {
            setJob(data);
            router.push(`/jobs/${data.id}`);
          } else {
            setResults(data);
          }
        })
      });
  }

  if (isLoading) return <p>Loading...</p>
  if (!algorithms || !datasets) return <p>Something went wrong</p>

  return <div>
    <h1 className="text-4xl font-bold">No-code Benchmarking of Entity Resolution</h1>

    <div className="grid mt-4">
      <div className="col">
        <h2>Dataset</h2>

        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="dataset">Predefined dataset</label>
          <Dropdown id="dataset" aria-describedby="dataset-help" className="w-full"
                    value={selectedDataset} onChange={(e) => setSelectedDataset(e.value)}
                    disabled={formDisabled}
                    options={datasets} optionLabel="name"
                    placeholder="Select a dataset"/>
          <small id="dataset-help">You can select one of the common dataset, or upload your own
            below</small>
        </div>

        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="filtering-algorithm">Filtering Algorithm</label>
          <Dropdown id="filtering-algorithm" aria-describedby="filtering-algorithm-help" className="w-full"
                    value={selectedFilteringAlgo} onChange={(e) => setSelectedFilteringAlgo(e.value)}
                    disabled={formDisabled}
                    options={algorithms.filter(algo => algo.scenarios.includes('filtering'))}
                    optionLabel="name"
                    placeholder="Select an algorithm"/>
          <small id="filtering-algorithm-help">Which algorithm to use for filtering the dataset</small>
        </div>

        <div className={(selectedFilteringAlgo != null && selectedFilteringAlgo.params.includes('recall') ? null : "hidden")}>
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="filtering-recall">Filtering Recall</label>
            <Dropdown id="filtering-recall" aria-describedby="filtering-recall-help" className="w-full"
                      value={filteringRecall} onChange={(e) => setFilteringRecall(e.value)}
                      disabled={formDisabled}
                      options={filteringRecallOptions}
                      placeholder="Select an algorithm"/>
            <small id="filtering-recall-help">A recall value for filtering</small>
          </div>
        </div>

        <div className={(selectedFilteringAlgo != null && selectedFilteringAlgo.params.includes('epochs') ? null : "hidden")}>
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="filtering-epochs">Filtering Epochs</label>
            <InputNumber id="filtering-epochs" aria-describedby="filtering-epochs-help" className="w-full"
                         value={filteringEpochs} onValueChange={(e) => setFilteringEpochs(e.value)}
                         disabled={formDisabled}
                         minFractionDigits={0} min={5} max={50} step={5} showButtons/>
            <small id="filtering-epochs-help">A numbers of epochs to run for filtering</small>
          </div>
        </div>

        {/*<div className="flex flex-column gap-2 mb-3">
          <label htmlFor="dataset_file">Own dataset</label>
          <FileUpload id="dataset_file" aria-describedby="dataset_first-help" mode="basic"
                      name="dataset_file[]" accept="text/*" maxFileSize={1000000}
                      disabled={formDisabled}/>
          <small id="dataset_first-help">Please select the first part</small>

          <FileUpload id="dataset_second" aria-describedby="dataset_second-help" mode="basic"
                      name="dataset_file[]" accept="text/*" maxFileSize={1000000}
                      disabled={formDisabled}/>
          <small id="dataset_second-help">Please select the second part</small>

          <FileUpload id="dataset_ground" aria-describedby="dataset_ground-help" mode="basic"
                      name="dataset_file[]" accept="text/*" maxFileSize={1000000}
                      disabled={formDisabled}/>
          <small id="dataset_ground-help">Ground truth</small>
        </div>*/}
      </div>

      <div className="col">
        <h2>Model</h2>

        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="matching-algorithm">Matching Algorithm</label>
          <Dropdown id="matching-algorithm" aria-describedby="matching-algorithm-help" className="w-full"
                    value={selectedMatchingAlgo} onChange={(e) => setSelectedMatchingAlgo(e.value)}
                    disabled={formDisabled}
                    options={algorithms.filter(algo => algo.scenarios.includes('matching'))}
                    optionLabel="name"
                    placeholder="Select a model"/>
          <small id="matching-algorithm-help">Which algorithm / model to use</small>
        </div>

        <div className={(selectedMatchingAlgo != null && selectedMatchingAlgo.params.includes('recall') ? null : "hidden")}>
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="matching-recall">Matching Recall</label>
            <InputNumber id="matching-recall" aria-describedby="matching-recall-help" className="w-full"
                         value={matchingRecall} onValueChange={(e) => setMatchingRecall(e.value)}
                         disabled={formDisabled}
                         minFractionDigits={2} min={0} max={1} step={0.05} mode="decimal"
                         showButtons/>
            <small id="matching-recall-help">A recall value between 0 and 1</small>
          </div>
        </div>

        <div className={(selectedMatchingAlgo != null && selectedMatchingAlgo.params.includes('epochs') ? null : "hidden")}>
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="matching-epochs">Matching Epochs</label>
            <InputNumber id="matching-epochs" aria-describedby="matching-epochs-help" className="w-full"
                         value={matchingEpochs} onValueChange={(e) => setMatchingEpochs(e.value)}
                         disabled={formDisabled}
                         minFractionDigits={0} min={5} max={50} step={5} showButtons/>
            <small id="matching-epochs-help">A numbers of epochs to run</small>
          </div>
        </div>
      </div>
    </div>

    <div className="grid align-items-center">
      <div className="col">
        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="email">Email</label>
          <InputText id="email" aria-describedby="email-help" className="w-full"
                     value={email} onChange={(e) => setEmail(e.target.value)}
                     disabled={formDisabled}/>
          <small id="email-help">We will notify when training is complete, it may take some time</small>
        </div>
      </div>
    </div>

    <div className="grid">
      <div className="col-auto">
        <Button label="Submit" onClick={onSubmit} disabled={results.length > 0 && !forceSubmit}/>
      </div>
      {results.length > 0 && (
        <div className="col">
          <Checkbox inputId="force" onChange={e => setForceSubmit(e.checked)} checked={forceSubmit}></Checkbox>
          <label htmlFor="force" className="p-checkbox-label pl-2">I want to submit a new job</label>
        </div>
      )}
    </div>

    {results.length > 0 && (
      <div className="grid">
        <div className="col">
          <h4>We have found some similar results already computed</h4>

          <DataTable value={results} onRowClick={e => router.push(`/jobs/${e.data.id}`)} stripedRows size="small" rowClassName="p-selectable-row">
            <Column field="id" header="Job ID" body={(rowData) => <a href={`/jobs/${rowData.id}`}>{rowData.id}</a>}></Column>
            <Column field="dataset.name" header="Dataset"></Column>
            <Column field="filteringAlgo.name" header="Filtering Algorithm"></Column>
            <Column body={(row) => renderParams(row.filteringParams)} header="Filtering Params"></Column>
            <Column field="matchingAlgo.name" header="Matching Algorithm"></Column>
            <Column body={(row) => renderParams(row.matchingParams)} header="Matching Params"></Column>
            <Column field="createdAt" header="Created"></Column>
          </DataTable>
        </div>
      </div>
    )}
  </div>
}

