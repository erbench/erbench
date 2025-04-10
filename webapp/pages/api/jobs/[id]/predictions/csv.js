import prisma from "../../../../../prisma/client";

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({error: 'Method not allowed'});
  }

  try {
    const job = await prisma.job.findUnique({
      where: {id: req.query.id},
      include: {
        dataset: true,
        filteringAlgo: true,
        matchingAlgo: true,
        result: true,
        predictions: {
          orderBy: {probability: 'desc'},
        },
      }
    });

    if (!job) {
      return res.status(404).json({error: 'Job not found'});
    }

    if (!job.predictions || job.predictions.length === 0) {
      return res.status(404).json({error: 'No predictions found for this job'});
    }

    const csvContent = generatePredictionsCsv(job);

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename="job-${job.id}-predictions.csv"`);
    return res.status(200).send(csvContent);
  } catch (error) {
    console.error("Error generating CSV:", error);
    return res.status(500).json({error: "Failed to generate CSV"});
  }
}

function generatePredictionsCsv(job) {
  let csv = `# Job ID: ${job.id}\n`;
  csv += `# Dataset: ${job.dataset.name}\n`;
  csv += `# Filtering Algorithm: ${job.filteringAlgo.name}\n`;
  csv += `# Filtering Parameters: ${JSON.stringify(job.filteringAlgo.parameters)}\n`;
  csv += `# Matching Algorithm: ${job.matchingAlgo.name}\n`;
  csv += `# Matching Parameters: ${JSON.stringify(job.matchingAlgo.parameters)}\n`;
  csv += `# Created: ${new Date(job.createdAt).toISOString()}\n`;
  if (job.result) {
    csv += `# Filtering: f1 ${job.result.filteringF1}, precision ${job.result.filteringPrecision}, recall ${job.result.filteringRecall}, filteringTime ${job.result.filteringTime}, candidates ${job.result.filteringCandidates}, entriesA ${job.result.filteringEntriesA}, entriesB ${job.result.filteringEntriesB}, matches ${job.result.filteringMatches}\n`;
    csv += `# Matching: f1 ${job.result.f1}, precision ${job.result.precision}, recall ${job.result.recall}, trainTime ${job.result.trainTime}, evalTime ${job.result.evalTime}\n`;
  }
  csv += `# Total Predictions: ${job.predictions.length}\n\n`;

  // Add data
  csv += 'tableA_id,tableB_id,probability\n';
  csv += job.predictions.map(p => `${p.tableA_id},${p.tableB_id},${p.probability}`).join('\n');
  return csv;
}
