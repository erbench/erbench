import prisma from "../../../../prisma/client";

export default async function handler(req, res) {
  const jobId = req.query.id;

  if (req.method === 'GET') {
    try {
      const job = await prisma.job.findUnique({
        where: {
          id: jobId,
        },
        include: {
          filteringAlgo: true,
          matchingAlgo: true,
          dataset: true,
          results: true,
        }
      });

      if (!job) {
        return res.status(404).json({error: "Job not found"});
      }

      return res.status(200).json(job);
    } catch (error) {
      console.error("Error fetching job:", error);
      return res.status(500).json({error: "Failed to fetch job"});
    }
  }

  if (req.method === 'PUT') {
    if (!req.body.status) {
      return res.status(400).json({error: 'status is required'});
    }

    try {
      const job = await prisma.job.update({
        where: {
          id: jobId,
        },
        data: {
          status: req.body.status,
          filteringSlurmId: req.body.filteringSlurmId,
          matchingSlurmId: req.body.matchingSlurmId,
        }
      });

      return res.status(200).json(job);
    } catch (error) {
      console.error("Error updating job:", error);
      return res.status(500).json({error: "Failed to updating job"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
