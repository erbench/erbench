import prisma from "../../../prisma/client";

export default async function handler(req, res) {
  if (req.method === 'POST') {
    if (!req.body.datasetId || !req.body.filteringAlgoId || !req.body.matchingAlgoId) {
      return res.status(400).json({error: 'datasetId and algorithmId are required'});
    }

    try {
      const job = await prisma.job.create({
        data: {
          datasetId: req.body.datasetId,
          filteringAlgoId: req.body.filteringAlgoId,
          filteringParams: req.body.filteringParams,
          matchingAlgoId: req.body.matchingAlgoId,
          matchingParams: req.body.matchingParams,
          notifyEmail: req.body.notifyEmail,
        }
      });

      return res.status(201).json(job);
    } catch (error) {
      console.error("Error creating job:", error);
      return res.status(500).json({error: "Failed to create job"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
