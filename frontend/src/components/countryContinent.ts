/**
 * Correspondance code ISO numérique du pays → continent.
 * Utilisé par WorldMapCard pour colorer la carte du monde (world-atlas) par
 * continent. Le topojson world-atlas identifie chaque pays par son code ISO
 * numérique (geo.id). On regroupe ici ces codes par continent.
 *
 * Continents alignés sur le backend : Afrique, Europe, Amérique, Asie, Océanie.
 * (L'Antarctique n'est pas pris en compte.)
 */

export type Continent = 'Afrique' | 'Europe' | 'Amérique' | 'Asie' | 'Océanie';

// Codes ISO 3166-1 numériques regroupés par continent.
const PAR_CONTINENT: Record<Continent, number[]> = {
  Afrique: [
    12, 24, 72, 86, 108, 120, 132, 140, 148, 174, 178, 180, 204, 226, 231, 232,
    262, 266, 270, 288, 324, 384, 404, 426, 430, 434, 450, 454, 466, 478, 480,
    504, 508, 516, 562, 566, 624, 646, 678, 686, 690, 694, 706, 710, 716, 728,
    729, 732, 748, 768, 788, 800, 818, 834, 854, 894,
  ],
  Europe: [
    // NB : la Russie (643) est transcontinentale ; rattachée à l'Asie (majorité
    // du territoire en Sibérie) — voir la liste Asie ci-dessous.
    8, 20, 40, 56, 70, 100, 112, 191, 203, 208, 233, 234, 246, 250, 276, 292,
    300, 304, 348, 352, 372, 380, 428, 440, 442, 470, 492, 498, 499, 528, 578,
    616, 620, 642, 674, 688, 703, 705, 724, 752, 756, 804, 807, 826, 831,
    832, 833, 336,
  ],
  Amérique: [
    28, 32, 44, 52, 60, 68, 76, 84, 92, 124, 136, 152, 170, 188, 192, 212, 214,
    218, 222, 238, 254, 304 /*Groenland*/, 308, 312, 320, 328, 332, 340, 388,
    474, 484, 500, 531, 533, 534, 535, 558, 591, 600, 604, 630, 652, 659, 660,
    662, 663, 666, 670, 740, 780, 796, 840, 850, 858, 862,
  ],
  Asie: [
    643, /* Russie — transcontinentale, rattachée à l'Asie (Sibérie majoritaire) */
    4, 31, 48, 50, 51, 64, 96, 104, 116, 144, 156, 196, 268, 275, 344, 356, 360,
    364, 368, 376, 392, 398, 400, 408, 410, 414, 417, 418, 422, 446, 458, 462,
    496, 512, 524, 586, 608, 624 /*ne pas dupliquer*/, 626, 634, 682, 702, 704,
    760, 762, 764, 784, 792, 795, 860, 887,
  ],
  Océanie: [
    36, 90, 162, 166, 184, 242, 258, 296, 316, 520, 540, 548, 554, 570, 574,
    580, 583, 584, 585, 598, 612, 772, 776, 798, 876, 882,
  ],
};

// Index inversé : code ISO numérique → continent.
const CODE_TO_CONTINENT: Record<number, Continent> = {};
(Object.keys(PAR_CONTINENT) as Continent[]).forEach(continent => {
  PAR_CONTINENT[continent].forEach(code => {
    if (!(code in CODE_TO_CONTINENT)) CODE_TO_CONTINENT[code] = continent;
  });
});

/** Continent d'un pays à partir de son code ISO numérique (string ou number). */
export const continentOf = (geoId: string | number): Continent | null => {
  const code = typeof geoId === 'string' ? parseInt(geoId, 10) : geoId;
  return CODE_TO_CONTINENT[code] ?? null;
};
