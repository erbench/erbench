import React, {useState} from 'react';
import {useRouter} from 'next/navigation';
import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {FilterMatchMode} from "primereact/api";

import prisma from "../../prisma/client";
import {dropdownFilterTemplate, renderDate, renderParams, renderStatusTemplate, statusRowFilterTemplate} from "../../utils/jobUtils";
import Head from "next/head";

export const getServerSideProps = async () => {
  const jobs = await prisma.job.findMany({
    take: 10,
    orderBy: {
      createdAt: 'desc'
    },
    include: {
      filteringAlgo: true,
      matchingAlgo: true,
      dataset: true,
    }
  });

  return {
    props: {
      useContainer: false,
      jobs: JSON.parse(JSON.stringify(jobs)),
    }
  }
}

export default function ListJobs({jobs}) {
  const router = useRouter()
  const [filters, setFilters] = useState({
    id: {value: null, matchMode: FilterMatchMode.CONTAINS},
    status: {value: null, matchMode: FilterMatchMode.EQUALS},
    'dataset.name': {value: null, matchMode: FilterMatchMode.EQUALS},
    'filteringAlgo.name': {value: null, matchMode: FilterMatchMode.EQUALS},
    'matchingAlgo.name': {value: null, matchMode: FilterMatchMode.EQUALS},
  });

  const statusOptions = [...new Set(jobs?.map(job => job.status) || [])];
  const datasetOptions = [...new Set(jobs?.map(job => job.dataset?.name).filter(Boolean) || [])];
  const filteringAlgoOptions = [...new Set(jobs?.map(job => job.filteringAlgo?.name).filter(Boolean) || [])];
  const matchingAlgoOptions = [...new Set(jobs?.map(job => job.matchingAlgo?.name).filter(Boolean) || [])];

  if (!jobs) {
    return <div>
      <h1 className="text-4xl font-bold">No jobs found</h1>
    </div>
  }

  return <div>
    <Head>
      <title>Jobs list | ERBench</title>
      <meta name="description" content="List of submitted jobs for entity resolution"/>
    </Head>

    <h1 className="text-4xl font-bold">Jobs list</h1>

    <div className="card">
      <DataTable value={jobs} stripedRows size="small" rowClassName="p-selectable-row"
                 onRowClick={e => router.push(`/jobs/${e.data.id}`)}
                 sortMode="single" filters={filters} filterDisplay="row" onFilter={(e) => setFilters(e.filters)}>
        <Column field="id" header="Job ID" sortable filter filterPlaceholder="Search by ID" filterMatchMode="contains"
                body={(rowData) => <a href={`/jobs/${rowData.id}`}>{rowData.id}</a>}/>
        <Column field="status" header="Status" sortable body={renderStatusTemplate}
                filter showFilterMenu={false} filterElement={(options) => statusRowFilterTemplate(options, statusOptions)}/>
        <Column field="dataset.name" header="Dataset" sortable
                filter showFilterMenu={false} filterElement={(options) => dropdownFilterTemplate(options, datasetOptions)}/>
        <Column field="filteringAlgo.name" header="Filtering Algorithm" sortable
                filter showFilterMenu={false} filterElement={(options) => dropdownFilterTemplate(options, filteringAlgoOptions)}/>
        <Column body={(row) => renderParams(row.filteringParams)} header="Filtering Params"/>
        <Column field="matchingAlgo.name" header="Matching Algorithm" sortable
                filter showFilterMenu={false} filterElement={(options) => dropdownFilterTemplate(options, matchingAlgoOptions)}/>
        <Column body={(row) => renderParams(row.matchingParams)} header="Matching Params"/>
        <Column field="createdAt" header="Created" sortable body={(row) => renderDate(row.createdAt)}/>
      </DataTable>
    </div>
  </div>
}

