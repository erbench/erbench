import React, {useState} from 'react';
import {useRouter} from 'next/navigation';
import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {Button} from 'primereact/button';
import {InputNumber} from 'primereact/inputnumber';
import {Dropdown} from 'primereact/dropdown';
import {InputText} from "primereact/inputtext";

import prisma from "../prisma/client";
import {Checkbox} from "primereact/checkbox";
import {renderDate, renderParams} from "../utils/jobUtils";
import Head from "next/head";

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

  // fields
  const [selectedDataset, setSelectedDataset] = useState(datasets[0]);

  const [selectedFilteringAlgo, setSelectedFilteringAlgo] = useState(algorithms.find(algo => algo.scenarios.includes('filtering')));
  const [filteringRecall, setFilteringRecall] = useState(0.90);
  const [filteringNegPairsRatio, setFilteringNegPairsRatio] = useState(10);
  const [filteringDefault, setFilteringDefault] = useState(false);

  const [selectedMatchingAlgo, setSelectedMatchingAlgo] = useState(algorithms.find(algo => algo.scenarios.includes('matching')));
  const [matchingEpochs, setMatchingEpochs] = useState(10);
  const [matchingModel, setMatchingModel] = useState(null);
  const [matchingMethod, setMatchingMethod] = useState(null);
  const [matchingFull, setMatchingFull] = useState(false);

  const [email, setEmail] = useState('');

  // state
  const [isLoading, setLoading] = useState(false);
  const [formDisabled, setDisabled] = useState(false);

  // data
  const [results, setResults] = useState([]);
  const [forceSubmit, setForceSubmit] = useState(false);

  const onSubmit = async (e) => {
    setResults([]);
    setDisabled(true);

    let filteringParams = {};
    if ('recall' in selectedFilteringAlgo.params) {
      filteringParams.recall = filteringRecall;
    }
    if ('neg_pairs_ratio' in selectedFilteringAlgo.params) {
      filteringParams.neg_pairs_ratio = filteringNegPairsRatio;
    }
    if ('default' in selectedFilteringAlgo.params) {
      filteringParams.default = filteringDefault;
    }

    let matchingParams = {};
    if ('epochs' in selectedMatchingAlgo.params) {
      matchingParams.epochs = matchingEpochs;
    }
    if ('model' in selectedMatchingAlgo.params) {
      matchingParams.model = matchingModel;
    }
    if ('method' in selectedMatchingAlgo.params) {
      matchingParams.method = matchingMethod;
    }
    if ('full' in selectedMatchingAlgo.params) {
      matchingParams.full = matchingFull;
    }

    if (!forceSubmit) {
      const response = await fetch('/api/jobs/query', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filters: {
            datasetId: {value: selectedDataset.id, matchMode: 'equals'},
            filteringAlgoId: {value: selectedFilteringAlgo.id, matchMode: 'equals'},
            filteringParams: {value: filteringParams, matchMode: 'equals'},
            matchingAlgoId: {value: selectedMatchingAlgo.id, matchMode: 'equals'},
            matchingParams: {value: matchingParams, matchMode: 'equals'},
          },
        }),
      });

      const json = await response.json();
      if (json?.page?.total > 0) {
        setResults(json.data);
        return;
      }
    }

    const response = await fetch('/api/jobs', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        datasetId: selectedDataset.id,
        filteringAlgoId: selectedFilteringAlgo.id,
        filteringParams: filteringParams,
        matchingAlgoId: selectedMatchingAlgo.id,
        matchingParams: matchingParams,
        notifyEmail: email,
      }),
    });

    const job = await response.json();
    router.push(`/jobs/${job.id}`);
  }

  if (isLoading) return <p>Loading...</p>
  if (!algorithms || !datasets) return <p>Something went wrong</p>

  return <div>
    <Head>
      <title>Submit a new job | SMBench</title>
      <meta name="description" content="On this page you can submit a new job for entity resolution benchmarking"/>
    </Head>

    <h1 className="text-4xl font-bold">SMBench: No-code Benchmarking of Learning-based Entity Matching</h1>

    <div className="grid mt-4">
      <div className="col">
        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="dataset">Dataset</label>
          <Dropdown id="dataset" aria-describedby="dataset-help" className="w-full"
                    value={selectedDataset} onChange={(e) => setSelectedDataset(e.value)}
                    disabled={formDisabled}
                    options={datasets} optionLabel="name"
                    placeholder="Select a dataset"/>
          <small id="dataset-help">Select one of nine datasets that are popular in the literature</small>
        </div>

        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="filtering-algorithm">Filtering Algorithm</label>
          <Dropdown id="filtering-algorithm" aria-describedby="filtering-algorithm-help" className="w-full"
                    value={selectedFilteringAlgo} onChange={(e) => setSelectedFilteringAlgo(e.value)}
                    disabled={formDisabled}
                    options={algorithms.filter(algo => algo.scenarios.includes('filtering'))}
                    optionLabel="name"
                    placeholder="Select an algorithm"/>
          <small id="filtering-algorithm-help">Which Filtering method to use for generating the candidate pairs</small>
        </div>

        {selectedFilteringAlgo != null && 'recall' in selectedFilteringAlgo.params && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="filtering-recall">Filtering Recall</label>
            {selectedFilteringAlgo.params.recall === 'number' && (
              <InputNumber id="filtering-recall" aria-describedby="filtering-recall-help" className="w-full"
                           value={filteringRecall} onValueChange={(e) => setFilteringRecall(e.value)}
                           disabled={formDisabled}
                           minFractionDigits={2} min={0} max={1} step={0.05} mode="decimal"
                           showButtons/>
            )}
            {selectedFilteringAlgo.params.recall.startsWith('dropdown') && (
              <Dropdown id="filtering-recall" aria-describedby="filtering-recall-help" className="w-full"
                        value={filteringRecall} onChange={(e) => setFilteringRecall(e.value)}
                        disabled={formDisabled}
                        options={selectedFilteringAlgo.params.recall.split('=')[1].split('|').map(v => parseFloat(v))}
                        placeholder="Select an algorithm"/>
            )}
            <small id="filtering-recall-help">The minimum acceptable recall, against which we maximize precision</small>
          </div>
        )}

        {selectedFilteringAlgo != null && 'neg_pairs_ratio' in selectedFilteringAlgo.params && selectedFilteringAlgo.params.neg_pairs_ratio === 'number' && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="filtering-negpairs">Negative Pairs Ratio</label>
            <InputNumber id="filtering-negpairs" aria-describedby="filtering-negpairs-help" className="w-full"
                         value={filteringNegPairsRatio} onValueChange={(e) => setFilteringNegPairsRatio(e.value)}
                         disabled={formDisabled}
                         minFractionDigits={1} min={0} max={50} step={0.1} mode="decimal"
                         showButtons/>
            <small id="filtering-negpairs-help">The number of negative instances per positive one in the candidate pairs generated by Random Splitter</small>
          </div>
        )}

        {selectedFilteringAlgo != null && 'default' in selectedFilteringAlgo.params && selectedFilteringAlgo.params.default === 'boolean' && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="filtering-default">Default settings</label>
            <Checkbox id="filtering-default" aria-describedby="filtering-default-help" className="w-full"
                      checked={filteringDefault} onChange={e => setFilteringDefault(e.checked)}
                      disabled={formDisabled}/>
            <small id="filtering-default-help">Whether to use default settings or fine-tuned for the dataset</small>
          </div>
        )}

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
        <div className="flex flex-column gap-2 mb-3">
          <label htmlFor="matching-algorithm">Matching Algorithm</label>
          <Dropdown id="matching-algorithm" aria-describedby="matching-algorithm-help" className="w-full"
                    value={selectedMatchingAlgo} onChange={(e) => setSelectedMatchingAlgo(e.value)}
                    disabled={formDisabled}
                    options={algorithms.filter(algo => algo.scenarios.includes('matching'))}
                    optionLabel="name"
                    placeholder="Select a model"/>
          <small id="matching-algorithm-help">Which Verification method to apply to the candidate pairs</small>
        </div>

        {selectedMatchingAlgo != null && 'epochs' in selectedMatchingAlgo.params && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="matching-epochs">Matching Epochs</label>
            <InputNumber id="matching-epochs" aria-describedby="matching-epochs-help" className="w-full"
                         value={matchingEpochs} onValueChange={(e) => setMatchingEpochs(e.value)}
                         disabled={formDisabled}
                         minFractionDigits={0} min={5} max={50} step={5} showButtons/>
            <small id="matching-epochs-help">A numbers of epochs to run</small>
          </div>
        )}

        {selectedMatchingAlgo != null && 'model' in selectedMatchingAlgo.params && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="matching-model">Language Model</label>
            {selectedMatchingAlgo.params.model.startsWith('dropdown') && (
              <Dropdown id="matching-model" aria-describedby="matching-model-help" className="w-full"
                        value={matchingModel} onChange={(e) => setMatchingModel(e.value)}
                        disabled={formDisabled}
                        options={selectedMatchingAlgo.params.model.split('=')[1].split('|')}
                        placeholder="Select an algorithm"/>
            )}
            <small id="matching-model-help">The language model generating the embedding vectors</small>
          </div>
        )}

        {selectedMatchingAlgo != null && 'method' in selectedMatchingAlgo.params && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="matching-method">Matching Method</label>
            {selectedMatchingAlgo.params.method.startsWith('dropdown') && (
              <Dropdown id="matching-method" aria-describedby="matching-method-help" className="w-full"
                        value={matchingMethod} onChange={(e) => setMatchingMethod(e.value)}
                        disabled={formDisabled}
                        options={selectedMatchingAlgo.params.method.split('=')[1].split('|')}
                        placeholder="Select an algorithm"/>
            )}
            <small id="matching-method-help">A method value for matching</small>
          </div>
        )}

        {selectedMatchingAlgo != null && 'full' in selectedMatchingAlgo.params && selectedMatchingAlgo.params.full === 'boolean' && (
          <div className="flex flex-column gap-2 mb-3">
            <label htmlFor="matching-full">Use full dataset</label>
            <Checkbox id="matching-full" aria-describedby="matching-full-help" className="w-full"
                      checked={matchingFull} onChange={e => setMatchingFull(e.checked)}
                      disabled={formDisabled}/>
            <small id="matching-full-help">Whether to use full dataset or just the test part</small>
          </div>
        )}
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
          <Checkbox inputId="force" onChange={e => setForceSubmit(e.checked)} checked={forceSubmit}/>
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
            <Column field="createdAt" header="Created" body={(row) => renderDate(row.createdAt)}></Column>
          </DataTable>
        </div>
      </div>
    )}
  </div>
}

