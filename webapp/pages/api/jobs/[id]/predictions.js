import prisma from "../../../../prisma/client";

export default async function handler(req, res) {
  const jobId = req.query.id;

  // Simply return all predictions for the job
  if (req.method === 'GET') {
    try {
      const predictions = await prisma.predictions.findMany({
        where: {
          jobId: jobId,
        },
        orderBy: {
          probability: 'desc'
        }
      });

      return res.status(200).json(predictions);
    } catch (error) {
      return res.status(500).json({error: "Failed to fetch predictions"});
    }
  }

  // Fetch predictions with pagination and filtering
  if (req.method === 'POST') {
    const params = req.body;

    const skip = parseInt(params.first) || 0;
    const take = parseInt(params.rows) || 20;

    const sortField = req.query.sortField || 'probability';
    const sortOrder = req.query.sortOrder === '-1' ? 'asc' : 'desc';

    const whereClause = {
      jobId: jobId
    };

    if (params.filters) {
      if (params.filters.tableA_id?.value) {
        if (params.filters.tableA_id.matchMode === 'contains') {
          whereClause.tableA_id = { contains: params.filters.tableA_id.value };
        } else {
          whereClause.tableA_id = params.filters.tableA_id.value;
        }
      }

      if (params.filters.tableB_id?.value) {
        if (params.filters.tableB_id.matchMode === 'contains') {
          whereClause.tableB_id = { contains: params.filters.tableB_id.value };
        } else {
          whereClause.tableB_id = params.filters.tableB_id.value;
        }
      }

      if (params.filters.probability?.value) {
        const probValue = parseFloat(params.filters.probability.value);
        if (!isNaN(probValue)) {
          if (params.filters.probability.matchMode === 'gte') {
            whereClause.probability = { gte: probValue };
          } else if (params.filters.probability.matchMode === 'lte') {
            whereClause.probability = { lte: probValue };
          } else {
            whereClause.probability = probValue;
          }
        }
      }
    }

    try {
      const predictions = await prisma.predictions.findMany({
        where: whereClause,
        skip: skip,
        take: take,
        orderBy: {
          [sortField]: sortOrder
        }
      });

      const totalCount = await prisma.predictions.count({
        where: whereClause
      });

      return res.status(200).json({
        predictions,
        total: totalCount
      });
    } catch (error) {
      console.error("Error fetching job predictions:", error);
      return res.status(500).json({error: "Failed to fetch predictions"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
