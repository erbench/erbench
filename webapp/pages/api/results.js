import prisma from "../../prisma/client";

export default async function handler(req, res) {
  if (req.method === 'POST') {

    if (!req.body.jobId || !req.body.status) {
      res.status(400)
    }

    if (req.body.status === 'completed') {
      await prisma.result.upsert({
        where: {
          jobId: req.body.jobId
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
          jobId: req.body.jobId,

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
    }

    await prisma.job.update({
      where: {
        id: req.body.jobId
      },
      data: {
        status: req.body.status
      }
    });

    return res.status(200).end();
  } else {
    return res.status(405).end();
  }
}
