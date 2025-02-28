import React from 'react';
import { useRouter } from 'next/navigation';
import {DataTable} from 'primereact/datatable';
import {Column} from 'primereact/column';

import prisma from "../../prisma/client";
import {renderParams, renderStatusTemplate} from "../../utils/jobUtils";

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

  if (!jobs) {
    return <div>
      <h1 className="text-4xl font-bold">No jobs found</h1>
    </div>
  }

  return <div>
    <h1 className="text-4xl font-bold">Jobs list</h1>

    <div className="card">
      <DataTable value={jobs} onRowClick={e => router.push(`/jobs/${e.data.id}`)} stripedRows size="small" rowClassName="p-selectable-row">
        <Column field="id" header="Job ID" body={(rowData) => <a href={`/jobs/${rowData.id}`}>{rowData.id}</a>}></Column>
        <Column field="status" header="Status" body={renderStatusTemplate}></Column>
        <Column field="dataset.name" header="Dataset"></Column>
        <Column field="filteringAlgo.name" header="Filtering Algorithm"></Column>
        <Column body={(row) => renderParams(row.filteringParams)} header="Filtering Params"></Column>
        <Column field="matchingAlgo.name" header="Matching Algorithm"></Column>
        <Column body={(row) => renderParams(row.matchingParams)} header="Matching Params"></Column>
        <Column field="createdAt" header="Created"></Column>
      </DataTable>
    </div>
  </div>
}

