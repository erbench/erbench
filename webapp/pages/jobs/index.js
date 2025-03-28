import React, {useState} from 'react';
import {useRouter} from 'next/navigation';
import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';
import {FilterMatchMode} from "primereact/api";
import Link from 'next/link';
import Head from "next/head";

import prisma from "../../prisma/client";
import {dropdownFilterTemplate, renderDate, renderParams, renderStatusTemplate, statusRowFilterTemplate} from "../../utils/jobUtils";

export const getServerSideProps = async (context) => {
  const {email} = context.query || {};

  const where = {};
  if (email) {
    where.notifyEmail = email;
  }

  const jobs = await prisma.job.findMany({
    where,
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
      filterEmail: email || null,
    }
  }
}

export default function ListJobs({jobs, filterEmail}) {
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

  // Show message when no jobs found with the specified email
  if (filterEmail && (!jobs || jobs.length === 0)) {
    return (
      <div>
        <Head>
          <title>Jobs for {filterEmail} | ERBench</title>
          <meta name="description" content={`Jobs filtered by email ${filterEmail}`}/>
        </Head>

        <h1 className="text-4xl font-bold">Jobs for {filterEmail}</h1>
        <div className="mt-4">
          <p>No jobs found for this email address.</p>
          <Link href="/jobs" className="text-blue-500 hover:underline">View all jobs</Link>
        </div>
      </div>
    );
  }

  if (!jobs || jobs.length === 0) {
    return <div>
      <h1 className="text-4xl font-bold">No jobs found</h1>
    </div>
  }

  return <div>
    <Head>
      <title>{filterEmail ? `Jobs for ${filterEmail}` : 'All jobs list'} | ERBench</title>
      <meta name="description" content={filterEmail ? `Jobs filtered by email ${filterEmail}` : "List of submitted jobs for entity resolution"}/>
    </Head>

    <div className="flex justify-content-between align-items-center mb-4">
      <h1 className="text-4xl font-bold">
        {filterEmail ? `Jobs for ${filterEmail}` : 'Jobs list'}
      </h1>

      {!filterEmail && (
        <div className="flex gap-2 align-items-center">
          <span className="text-sm text-gray-600 white-space-nowrap">Want to find your jobs?</span>
          <div className="p-inputgroup">
            <input id="emailFilter" type="email" placeholder="Enter email address" className="p-inputtext p-component p-2"
                   onKeyDown={(e) => e.key === 'Enter' && router.push(`/jobs?email=${e.target.value}`)}/>
            <button className="p-button p-component p-2 bg-blue-500 text-white"
                    onClick={() => {
                      const email = document.getElementById('emailFilter').value;
                      if (email) router.push(`/jobs?email=${email}`);
                    }}>
              Filter
            </button>
          </div>
        </div>
      )}
    </div>

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
