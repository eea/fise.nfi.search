/* eslint-disable */
import { fetchFacets, fetchSearch, fetch } from './config';

export function fetchCountries() {
  return fetchFacets('country/');
}

export function fetchCountry(id) {
  return fetchFacets(`country/${id}/`);
}

export function fetchDataSets() {
  return fetchFacets('data-set/');
}

export function fetchDataSet() {
  return fetchFacets(`data-set/${id}/`);
}

export function fetchDataTypes() {
  return fetchFacets(`data-type/`);
}

export function fetchDataType(id) {
  return fetchFacets(`data-type/${id}/`);
}

export function fetchInfoLevels() {
  return fetchFacets(`info-level/`);
}

export function fetchInfoLevel(id) {
  return fetchFacets(`info-level/${id}/`);
}

export function fetchKeywords() {
  return fetchFacets(`keyword/`);
}

export function fetchKeyword(id) {
  return fetchFacets(`keyword/${id}/`);
}

export function fetchLanguages() {
  return fetchFacets(`language/`);
}

export function fetchLanguage(id) {
  return fetchFacets(`language/${id}/`);
}

export function fetchNutsLevels() {
  return fetchFacets(`nuts-level/`);
}

export function fetchNutsLevel(id) {
  return fetchFacets(`nuts-level/${id}/`);
}

export function fetchResourceTypes() {
  return fetchFacets(`resource-type/`);
}

export function fetchResourceType(id) {
  return fetchFacets(`resource-type/${id}/`);
}

export function fetchTopicCategories() {
  return fetchFacets(`topic-category/`);
}

export function fetchTopicCategory(id) {
  return fetchFacets(`topic-category/${id}/`);
}

export function fetchCollectionsRange() {
  return fetch(`collections_range/`);
}

export function getCollectionYearsFormatted() {
  return new Promise((resolve, reject) => {
    fetchCollectionsRange()
      .then(response => {
        let max = response.data.max;
        let min = response.data.min;
        let result = Array.from({ length: max + 1 - min }, (v, k) => { return { id: k + min, name: k + min + ''} });

        resolve({ data: result });
      })
      .catch(error => {
        reject(error);
      });
  });
}

export function fetchPublicationYears() {
  return fetch(`publication_years/`);
}

export function getPublicationYearsFormatted() {
  return new Promise((resolve, reject) => {
    fetchPublicationYears()
      .then(response => {
        let result = [];

        response.data.map((item) => {
          result.push({ id: item, name: item + '' })
        })

        resolve({ data: result });
      })
      .catch(error => {
        reject(error);
      });
  });
}


export function search(term) {
  return fetchSearch(term);
}

export function searchId(id) {
  return fetchSearch(`?ids=${id}/`);
}

export { searchFullUrl } from './config';