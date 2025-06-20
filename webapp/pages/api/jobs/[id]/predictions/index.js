import prisma from "../../../../../prisma/client";
import {queryPredictions} from "./query";

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '20mb',
    },
  },
}

export default async function handler(req, res) {
  const jobId = req.query.id;

  if (req.method === 'GET') {
    try {
      const data = await queryPredictions(jobId, {
        sortField: 'probability',
        sortOrder: 'desc',
        first: 0,
        rows: 100,
        ...req.query,
      });

      return res.status(200).json(data);
    } catch (error) {
      console.error("Error fetching job predictions:", error);
      return res.status(500).json({error: "Failed to fetch predictions"});
    }
  }

  if (req.method === 'POST' || req.method === 'PUT') {
    try {
      const predictions = req.body.map(p => ({
        jobId: jobId,
        tableA_id: p.tableA_id,
        tableB_id: p.tableB_id,
        probability: p.probability,
      }));

      await prisma.predictions.createMany({
        data: predictions,
        skipDuplicates: true,
      });

      return res.status(200).end();
    } catch (error) {
      console.error("Error inserting predictions:", error);
      return res.status(500).json({error: "Failed to save predictions"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
