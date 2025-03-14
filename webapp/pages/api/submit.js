// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

import prisma from "../../prisma/client";

export default async function handler(req, res) {
  if (req.method === 'POST') {
    if (!req.body.datasetId || !req.body.algorithmId) {
      res.status(400)
    }

    if (!req.body.force) {
      const existingResults = await prisma.job.findMany({
        where: {
          status: 'completed',
          datasetId: req.body.datasetId,
          filteringAlgoId: req.body.filteringAlgoId,
          matchingAlgoId: req.body.matchingAlgoId,
          // Use Prisma's JSON query operators
          filteringParams: req.body.filteringParams ? { equals: req.body.filteringParams } : null,
          matchingParams: req.body.matchingParams ? { equals: req.body.matchingParams } : null,
        },
        include: {
          filteringAlgo: true,
          matchingAlgo: true,
          dataset: true,
          result: true,
        },
      });

      if (existingResults.length > 0) {
        return res.status(200).json(existingResults);
      }
    }

    const newJob = await prisma.job.create({
      data: {
        datasetId: req.body.datasetId,
        filteringAlgoId: req.body.filteringAlgoId,
        filteringParams: req.body.filteringParams,
        matchingAlgoId: req.body.matchingAlgoId,
        matchingParams: req.body.matchingParams,
        notifyEmail: req.body.notifyEmail,
      }
    });

    return res.status(201).json(newJob);
  } else {
    return res.status(405).end();
  }
}
