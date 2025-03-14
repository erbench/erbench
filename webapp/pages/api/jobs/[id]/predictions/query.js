import prisma from "../../../../../prisma/client";

/**
 * @param jobId {string}
 * @param params {{first?: string, rows?: string, sortField?: string, sortOrder?: string, filters?: {tableA_id?: {value: string, matchMode: string}, tableB_id?: {value: string, matchMode: string}, probability?: {value: string, matchMode: string}}}}
 * @returns {Promise<{page: {rows: number, first: number, total: number}, data: Array}>}
 */
export async function queryPredictions(jobId, params) {
  const first = parseInt(params.first) || 0;
  const rows = parseInt(params.rows) || 20;

  const sortField = params.sortField || 'probability';
  const sortOrder = parseInt(params.sortOrder) === -1 || (typeof params.sortOrder === 'string' && params.sortOrder?.toLowerCase() === 'desc') ? 'desc' : 'asc';

  const whereClause = {
    jobId: jobId
  };

  if (params.filters) {
    if (params.filters.tableA_id?.value) {
      if (params.filters.tableA_id.matchMode === 'contains') {
        whereClause.tableA_id = {contains: params.filters.tableA_id.value};
      } else {
        whereClause.tableA_id = params.filters.tableA_id.value;
      }
    }

    if (params.filters.tableB_id?.value) {
      if (params.filters.tableB_id.matchMode === 'contains') {
        whereClause.tableB_id = {contains: params.filters.tableB_id.value};
      } else {
        whereClause.tableB_id = params.filters.tableB_id.value;
      }
    }

    if (params.filters.probability?.value) {
      const probValue = parseFloat(params.filters.probability.value);
      if (!isNaN(probValue)) {
        if (params.filters.probability.matchMode === 'gte') {
          whereClause.probability = {gte: probValue};
        } else if (params.filters.probability.matchMode === 'lte') {
          whereClause.probability = {lte: probValue};
        } else {
          whereClause.probability = probValue;
        }
      }
    }
  }

  const predictions = await prisma.predictions.findMany({
    where: whereClause,
    skip: first,
    take: rows,
    orderBy: {
      [sortField]: sortOrder,
    }
  });

  const totalCount = await prisma.predictions.count({
    where: whereClause,
  });

  return {
    page: {
      rows: rows,
      first: first,
      total: totalCount,
    },
    data: predictions,
  };
}

export default async function handler(req, res) {
  const jobId = req.query.id;

  if (req.method === 'POST') {
    try {
      const data = await queryPredictions(jobId, req.body);
      return res.status(200).json(data);
    } catch (error) {
      console.error("Error fetching predictions:", error);
      return res.status(500).json({error: "Failed to fetch predictions"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
