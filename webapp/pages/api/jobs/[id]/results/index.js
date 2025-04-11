import prisma from "../../../../../prisma/client";

export default async function handler(req, res) {
  const jobId = req.query.id;

  if (req.method === 'GET') {
    try {
      const results = await prisma.result.findUnique({
        where: {jobId}
      });

      return res.status(200).json(results);
    } catch (error) {
      console.error("Error fetching job results:", error);
      return res.status(500).json({error: "Failed to fetch results"});
    }
  }

  if (req.method === 'POST' || req.method === 'PUT') {
    const {status, ...rest} = req.body;

    if (!status) {
      return res.status(400).json({error: 'status is required'});
    }

    if (status === 'matching' || status === 'completed') {
      try {
        await prisma.result.upsert({
          where: {jobId},
          update: rest,
          create: {jobId, ...rest}
        });
      } catch (error) {
        console.error("Error updating job results:", error);
        return res.status(500).json({error: "Failed to update results"});
      }
    }

    try {
      await prisma.job.update({
        where: {id: jobId},
        data: {status}
      });

      return res.status(200).end();
    } catch (error) {
      console.error("Error updating job status:", error);
      return res.status(500).json({error: "Failed to save status"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
