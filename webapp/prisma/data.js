export const algorithms = [
  // splitters
  {code: 'splitter_random', name: 'Random Splitter', scenarios: ['filtering'], params: {recall: 'number', neg_pairs_ratio: 'number'}},
  {code: 'splitter_deepblocker', name: 'DeepBlocker', scenarios: ['filtering'], params: {recall: 'dropdown=0.85|0.90|0.95'}},
  {code: 'splitter_knnjoin', name: 'kNN-Join', scenarios: ['filtering'], params: {recall: 'dropdown=0.85|0.90|0.95', 'default': 'boolean'}},
  // matchers
  {code: 'deepmatcher', name: 'DeepMatcher', scenarios: ['matching'], params: {epochs: 'number'}},
  {code: 'ditto', name: 'DITTO', scenarios: ['matching'], params: {epochs: 'number', model: 'dropdown=BERT|RoBERTa|DistilBERT|XLNet'}},
  {code: 'emtransformer', name: 'EMTransformer', scenarios: ['matching'], params: {epochs: 'number', model: 'dropdown=BERT|RoBERTa|DistilBERT|XLNet'}},
  {code: 'gnem', name: 'GNEM', scenarios: ['matching'], params: {epochs: 'number', model: 'dropdown=BERT|DistilBERT|XLNet|ALBERT'}},
  {code: 'hiermatcher', name: 'HierMatcher', scenarios: ['matching'], params: {epochs: 'number'}},
  {code: 'magellan', name: 'Magellan', scenarios: ['matching'], params: {method: 'dropdown=DecisionTree|SVM|RF|LogReg|LinReg|NaiveBayes'}},
  {code: 'zeroer', name: 'ZeroER', scenarios: ['matching'], params: {full: 'boolean'}},
];

export const datasets = [
  {code: 'd1_fodors_zagats', name: 'D1. Fodors-Zagats (Restaurants)'},
  {code: 'd2_abt_buy', name: 'D2. Abt-Buy (Products)'},
  {code: 'd3_amazon_google', name: 'D3. Amazon-Google (Products)'},
  {code: 'd4_dblp_acm', name: 'D4. DBLP-ACM (Citations)'},
  {code: 'd5_imdb_tmdb', name: 'D5. IMDB-TMDB (Movies)'},
  {code: 'd6_imdb_tvdb', name: 'D6. IMDB-TVDB (Movies)'},
  {code: 'd7_tmdb_tvdb', name: 'D7. TMDB-TVDB (Movies)'},
  {code: 'd8_amazon_walmart', name: 'D8. Amazon-Walmart (Electronics)'},
  {code: 'd9_dblp_scholar', name: 'D9. DBLP-Scholar (Citations)'},
  // {code: 'd10_imdb_dbpedia', name: 'D10. IMDB-DBPedia (Movies)'},
  // {code: 'd11_itunes_amazon', name: 'D11. iTunes-Amazon (Music)'},
  // {code: 'd12_beeradvo_ratebeer', name: 'D12. BeerAdvo-RateBeer (Beer)'},
];
