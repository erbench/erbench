import process from "node:process";
import {PrismaClient} from "@prisma/client";
import {algorithms, datasets} from "./data.js";
import {hashElement} from "folder-hash";

const prisma = new PrismaClient()

const load = async () => {
  // Remove algorithms not in the list
  const algorithmCodes = algorithms.map(algo => algo.code);
  await prisma.algorithm.deleteMany({
    where: {
      code: {
        notIn: algorithmCodes,
      },
    },
  });

  for (const algo of algorithms) {
    const a = await prisma.algorithm.upsert({
      where: {code: algo.code},
      update: {
        name: algo.name,
        scenarios: algo.scenarios,
        params: algo.params,
      },
      create: {
        code: algo.code,
        name: algo.name,
        scenarios: algo.scenarios,
        params: algo.params,
      },
    })
    console.log('Added/updated algorithm:', algo.code, a)
  }

  for (const dataset of datasets) {
    const datasetHash = await hashElement('../datasets/' + dataset.code, {
      files: {include: ['tableA.csv', 'tableB.csv', 'matches.csv']},
    });

    const r = await prisma.dataset.upsert({
      where: {code: dataset.code},
      update: {
        name: dataset.name,
        hash: datasetHash.hash,
        isCustom: false,
      },
      create: {
        code: dataset.code,
        name: dataset.name,
        hash: datasetHash.hash,
        isCustom: false,
      },
    })
    console.log('Added/updated dataset:', dataset.code, r)
  }
}

try {
  await load();
} catch (e) {
  console.error(e)
  process.exit(1)
} finally {
  await prisma.$disconnect()
}
