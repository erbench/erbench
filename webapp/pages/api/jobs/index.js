import prisma from "../../../prisma/client";

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const {
        status = 'pending',
        notifyEmail,
        datasetId,
        filteringAlgoId,
        matchingAlgoId,
        limit,
        skip
      } = req.query;

      const sortField = req.query.sortField || 'createdAt';
      const sortOrder = req.query.sortOrder === '-1' || req.query.sortOrder.toLowerCase() === 'desc' ? 'desc' : 'asc';

      // Build where clause based on provided filters
      const whereClause = {};

      if (status) {
        whereClause.status = status;
      }

      if (notifyEmail) {
        whereClause.notifyEmail = notifyEmail;
      }

      if (datasetId) {
        whereClause.datasetId = datasetId;
      }

      if (filteringAlgoId) {
        whereClause.filteringAlgoId = filteringAlgoId;
      }

      if (matchingAlgoId) {
        whereClause.matchingAlgoId = matchingAlgoId;
      }

      const jobs = await prisma.job.findMany({
        where: whereClause,
        include: {
          filteringAlgo: true,
          matchingAlgo: true,
          dataset: true
        },
        orderBy: {
          [sortField]: sortOrder
        },
        take: parseInt(limit) || 100,
        skip: parseInt(skip) || 0
      });

      return res.status(200).json(jobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      return res.status(500).json({error: "Failed to fetch jobs"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
