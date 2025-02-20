import prisma from "../../prisma/client";

export default async function handler(req, res) {
  if (req.method === 'POST') {
    if (!req.body.jobId) {
      res.status(400)
    }

    const predictions = req.body.predictions.map(prediction => ({
      jobId: req.body.jobId,
      tableA_id: prediction.tableA_id,
      tableB_id: prediction.tableB_id,
      probability: prediction.probability,
    }));

    await prisma.predictions.createMany({
      data: predictions
    });

    res.status(200);
  } else {
    res.status(405)
  }
}
