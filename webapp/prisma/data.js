export const algorithms = [
  // splitters
  {code: 'splitter_random', name: 'Random Split', scenarios: ['filtering'], params: {recall: 'number', neg_pairs_ratio: 'number'}},
  {code: 'splitter_deepblocker', name: 'DeepBlocker', scenarios: ['filtering'], params: {recall: 'number'}},
  {code: 'splitter_knnjoin', name: 'top kNN-Join', scenarios: ['filtering'], params: {recall: 'dropdown=0.85|0.90|0.95', 'default': 'boolean'}},
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
  {code: 'd1_fodors_zagats', name: 'Fodors-Zagats (Restaurants)'},
  {code: 'd2_abt_buy', name: 'Abt-Buy (Products)'},
  {code: 'd3_amazon_google', name: 'Amazon-Google (Products)'},
  {code: 'd4_dblp_acm', name: 'DBLP-ACM (Citations)'},
  {code: 'd5_imdb_tmdb', name: 'IMDB-TMDB (Movies)'},
  {code: 'd6_imdb_tvdb', name: 'IMDB-TVDB (Movies)'},
  {code: 'd7_tmdb_tvdb', name: 'TMDB-TVDB (Movies)'},
  {code: 'd8_amazon_walmart', name: 'Amazon-Walmart (Electronics)'},
  {code: 'd9_dblp_scholar', name: 'DBLP-Scholar (Citations)'},
  {code: 'd10_imdb_dbpedia', name: 'IMDB-DBPedia (Movies)'},
  {code: 'd11_itunes_amazon', name: 'iTunes-Amazon (Music)'},
  {code: 'd12_beeradvo_ratebeer', name: 'BeerAdvo-RateBeer (Beer)'},
];
