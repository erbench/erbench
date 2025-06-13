import {queryJobs} from "./query";

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const data = await queryJobs({
        sortField: 'createdAt',
        sortOrder: 'desc',
        first: 0,
        rows: 100,
        ...req.query,
      });

      return res.status(200).json(data);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      return res.status(500).json({error: "Failed to fetch jobs"});
    }
  }

  return res.status(405).json({error: 'Method not allowed'});
}
