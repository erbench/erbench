import prisma from "../../../../prisma/client";

export default async function handler(req, res) {
  const jobId = req.query.id;

  if (req.method === 'GET') {
    try {
      const results = await prisma.result.findUnique({
        where: {
          jobId: jobId,
        }
      });

      return res.status(200).json(results);
    } catch (error) {
      return res.status(500).json({error: "Failed to fetch results"});
    }
  }

  if (req.method === 'PUT') {
    if (!req.body.status) {
      return res.status(400).json({error: 'status is required'});
    }

    if (req.body.status === 'completed') {
      try {
        await prisma.result.upsert({
          where: {
            jobId: jobId,
          },
          update: {
            f1: req.body.f1,
            precision: req.body.precision,
            recall: req.body.recall,
            trainTime: req.body.trainTime,
            evalTime: req.body.evalTime,

            cpuUtilized: req.body.cpuUtilized,
            memoryUtilized: req.body.memoryUtilized,
            gpuAllocated: req.body.gpuAllocated,
            gpuUtilized: req.body.gpuUtilized,
            gpuMemUtilized: req.body.gpuMemUtilized,
            energyConsumed: req.body.energyConsumed,
            totalRuntime: req.body.totalRuntime,
          },
          create: {
            jobId: jobId,

            f1: req.body.f1,
            precision: req.body.precision,
            recall: req.body.recall,
            trainTime: req.body.trainTime,
            evalTime: req.body.evalTime,

            cpuUtilized: req.body.cpuUtilized,
            memoryUtilized: req.body.memoryUtilized,
            gpuAllocated: req.body.gpuAllocated,
            gpuUtilized: req.body.gpuUtilized,
            gpuMemUtilized: req.body.gpuMemUtilized,
            energyConsumed: req.body.energyConsumed,
            totalRuntime: req.body.totalRuntime,
          }
        });
      } catch (error) {
        return res.status(500).json({error: "Failed to update results"});
      }
    }

    try {
      await prisma.job.update({
        where: {
          id: jobId,
        },
        data: {
          status: req.body.status
        }
      });

      return res.status(200).end();
    } catch (error) {
      return res.status(500).json({error: "Failed to save status"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
