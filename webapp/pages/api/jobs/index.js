import prisma from "../../../prisma/client";

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const jobs = await prisma.job.findMany({
        where: {
          status: 'pending'
        },
        include: {
          filteringAlgo: true,
          matchingAlgo: true,
          dataset: true
        }
      });

      return res.status(200).json(jobs);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      return res.status(500).json({error: "Failed to fetch jobs"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
