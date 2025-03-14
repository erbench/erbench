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

  return res.status(405).json({error: 'Method not allowed'});
}
