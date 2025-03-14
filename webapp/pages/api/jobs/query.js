import prisma from "../../../prisma/client";

/**
 * @param params {{first?: string, rows?: string, sortField?: string, sortOrder?: string, filters?: {status?: {value: string, matchMode: string}, notifyEmail?: {value: string}, datasetId?: {value: string}, filteringAlgoId?: {value: string}, filteringParams?: {value: string}, matchingAlgoId?: {value: string}, matchingParams?: {value: string}}, include?: {}}}
 * @returns {Promise<{page: {rows: number, first: number, total: number}, data: Array}>}
 */
export async function queryJobs(params) {
  const first = parseInt(params.first) || 0;
  const rows = parseInt(params.rows) || 20;

  const sortField = params.sortField || 'createdAt';
  const sortOrder = parseInt(params.sortOrder) === -1 || (typeof params.sortOrder === 'string' && params.sortOrder?.toLowerCase() === 'desc') ? 'desc' : 'asc';

  const whereClause = {
    status: 'pending',
  };

  if (params.filters) {
    if (params.filters.status?.value) {
      whereClause.status = params.filters.status.value;
    }

    if (params.filters.notifyEmail?.value) {
      if (params.filters.notifyEmail.matchMode === 'contains') {
        whereClause.notifyEmail = {contains: params.filters.notifyEmail.value};
      } else {
        whereClause.notifyEmail = params.filters.notifyEmail.value;
      }
    }

    if (params.filters.datasetId?.value) {
        whereClause.datasetId = params.filters.datasetId.value;
    }

    if (params.filters.filteringAlgoId?.value) {
        whereClause.filteringAlgoId = params.filters.filteringAlgoId.value;
    }

    if (params.filters.matchingAlgoId?.value) {
        whereClause.matchingAlgoId = params.filters.matchingAlgoId.value;
    }

    if (params.filters.filteringParams?.value) {
        whereClause.filteringParams = {equals: params.filters.filteringParams.value};
    }

    if (params.filters.matchingParams?.value) {
        whereClause.matchingParams = {equals: params.filters.matchingParams.value};
    }
  }

  const jobs = await prisma.job.findMany({
    where: whereClause,
    skip: first,
    take: rows,
    orderBy: {
      [sortField]: sortOrder,
    },
    include: {
      filteringAlgo: true,
      matchingAlgo: true,
      dataset: true,
      result: true,
      ...params.include,
    },
  });

  const totalCount = await prisma.job.count({
    where: whereClause,
  });

  return {
    page: {
      rows: rows,
      first: first,
      total: totalCount,
    },
    data: jobs,
  };
}

export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const data = await queryJobs(req.body);
      return res.status(200).json(data);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      return res.status(500).json({error: "Failed to fetch jobs"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
