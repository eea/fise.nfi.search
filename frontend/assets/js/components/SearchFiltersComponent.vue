<template>
  <div class="">
    <h4 class="filters-title">Filters</h4>

    <hr>

    <!-- Select Country -->
    <h4 class="filter-heading">Countries and regions</h4>
    <div v-if="countries.length > 0">
      <country-component
        :dataList="countries"
        :componentName="'country'"
        :message="'Select country'"
        v-on:selected-country="handleSelectedCountry"
      ></country-component>
    </div>

    <hr>

    <!-- Select Nuts Levels -->
    <div v-if="facetsData.nuts_level" class="nuts">
      <check-box-buttons
        :dataList="facetsData.nuts_level"
        :componentName="'nutsLevels'"
        v-on:selected-nutsLevels="handleSelectedNutsLevels"
        :title="'NUTS levels'"
      ></check-box-buttons>
    </div>

    <hr>

    <div class="filter-heading">Date</div>

    <!-- Select Published Year -->
    <div v-if="facetsData.published_year">
      <h4 class="filter-heading--date">Published year</h4>
      <published-years
        :dataList="facetsData.published_year"
        :componentName="'published-year'"
        v-on:selected-published-year="handleSelectedPublishedYear"
      ></published-years>
    </div>

    <!-- Select Collection Years -->
    <div v-if="collectionsRange">
      <h4 class="filter-heading--date">Collection years</h4>
      <collection-years
        :dataList="collectionsRange"
        :componentName="'collections-range'"
        v-on:selected-collections-range="handleSelectedCollectionYears"
      ></collection-years>
    </div>

    <hr>

    <div v-if="showDateSets">
      <check-box-buttons
        :dataList="dataTypes[0].dataSets"
        :componentName="'dataSets-0'"
        :title="dataTypes[0].name"
        v-on:selected-dataSets-0="handleSelectedDataSetsRaster"
      ></check-box-buttons>

      <hr>

      <check-box-buttons
        :dataList="dataTypes[1].dataSets"
        :componentName="'dataSets-1'"
        :title="dataTypes[1].name"
        v-on:selected-dataSets-1="handleSelectedDataSetsSample"
      ></check-box-buttons>
    </div>

    <hr>

    <!-- Select Topic Category -->
    <div v-if="facetsData.topic_category">
      <check-box-buttons
        :dataList="facetsData.topic_category"
        :componentName="'topicCategory'"
        v-on:selected-topicCategory="handleSelectedTopicCategory"
        :title="'Topic'"
      ></check-box-buttons>
    </div>

    <hr>

    <!-- Select Result Formats -->
    <div v-if="facetsData.resource_type">
      <check-box-buttons
        :dataList="facetsData.resource_type"
        :componentName="'resourceTypes'"
        v-on:selected-resourceTypes="handleSelectedResourceTypes"
        :title="'Result format'"
      ></check-box-buttons>
    </div>

  </div>
</template>

<script>
import {
  fetchCountries,
  fetchDataSets,
  fetchDataTypes,
  fetchNutsLevels,
  fetchResourceTypes,
  fetchTopicCategories,
  fetchKeywords,
  fetchPublicationYears,
  fetchCollectionsRange,
  search
} from '../api';
import CheckBoxButtons from './CheckBoxButtons';
import PublishedYearsComponent from './PublishedYearsComponent';
import CollectionYearsComponent from './CollectionYearsComponent';
import CountryComponent from './CountryComponent';

const facets = {
  country: 'country',
  data_set: 'data_set',
  data_type: 'data_type',
  resource_type: 'resource_type',
  nuts_level: 'nuts_level',
  topic_category: 'topic_category',
  published_year: 'published_year',
  published_year_range: 'published_year__range',
  collections_range: 'collections_range',
  data_collection_end_year: 'data_collection_end_year',
  data_collection_start_year: 'data_collection_start_year',
  data_collection_start_year__lte: 'data_collection_start_year__lte',
  data_collection_end_year__gte: 'data_collection_end_year__gte',
  keyword: 'keyword',
}

const regions = ['EEA39', 'EU28', 'FAO234', 'SOEF46'];

const simpleFacets = {
  resource_type: { name: facets.resource_type, getFunction: fetchResourceTypes },
  nuts_level: { name: facets.nuts_level, getFunction: fetchNutsLevels },
  topic_category: { name: facets.topic_category, getFunction: fetchTopicCategories },
  published_year: { name: facets.published_year, getFunction: fetchPublicationYears },
}

/**
 * will create the facets using checkboxes, dropdowns, sliders and graphs
 * will autoupdate the count on each value of each facet
 */
export default {
  name: 'SearchFiltersComponent',

  components: {
    'check-box-buttons': CheckBoxButtons,
    'published-years': PublishedYearsComponent,
    'collection-years': CollectionYearsComponent,
    'country-component': CountryComponent,
  },

  props: {
    facets: {},
  },

  data() {
    return {
      countries: [],
      dataTypes: null,
      facetsData: {},
      selectedDataSetsSample: [],
      selectedDataSetsRaster: [],
      collectionsRange: null,
      showDateSets: false,
      selectedFilterOptions: {},
    };
  },

  created() {
    this.makeSelectedFilterOptions();
    this.getFacets();
  },

  methods: {
    /**
     * this.selectedFilterOptions will contain the names of all the facets names
     * here all the selected values from the facets will be available
     * based on these selections, the search query will be created
     */
    makeSelectedFilterOptions() {
      Object.keys(facets).map(key => {
        if(key === 'country') {
          this.selectedFilterOptions[key] = '';
        } else {
          this.selectedFilterOptions[key] = [];
        }
      });
    },

    /**
     * all requests are done at the same time, using one simple search to get the facets names and count
     * all facets that will show name and count and are not nested will be in simpleFacets
     * and will be handled the same way
     * dataTypes will nest dataSets, country will not show number, collectionRange wil only have min and max
     */
    getFacets() {
      const promises = [];
      const facetsData = {};
      
      Object.keys(simpleFacets).map(key => {
        const entity = simpleFacets[key];
        promises.push(this.wrapPromiseGetEntity(entity));
      });
      promises.push(this.searchByTerms());
      promises.push(fetchCountries());
      promises.push(fetchCollectionsRange());
      promises.push(fetchDataTypes());
      promises.push(fetchDataSets());

      Promise.all(promises).then(response => {
        const responseLength = response.length;
        const entities = response.slice(0, responseLength - 5);
        const facets = response[responseLength - 5].data.facets;
        
        entities.map(entity => {
          const entityName = entity.name;
          const entityData = entity.data;
          
          facetsData[entityName] = this.formatSets(
            facets[entityName],
            entityData
          );
        })
        // nuts levels need to be ordered
        facetsData.nuts_level = this.sortObjKeysAlphabetically(facetsData.nuts_level);
        // countries need to be reagions firs ordered and countries second and sorted
        this.facetsData = JSON.parse(JSON.stringify(facetsData));
        const countries = response[responseLength - 4].data.slice();
        this.countries = this.putRegionsAheadOfCountriesSorted(countries);
        this.collectionsRange = response[responseLength - 3].data;
        let dataTypes = response[responseLength - 2].data.slice();
        this.allSets = response[responseLength - 1].data.slice();

        let promisesSearchDataTypes = this.makeDataSetsPromisesForEachDataType(dataTypes);

        this.assignDataSetsToEachDataType(promisesSearchDataTypes, dataTypes);
      })
      .catch(error => {
        console.log(error);
      });
    },

    wrapPromiseGetEntity(entity) {
      return new Promise((resolve, reject) => {
        entity.getFunction()
          .then(response => {
            resolve({ data: response.data, name: entity.name });
          })
          .catch(error => {
            reject(error);
          });
      });
    },

    /**
     * @param {Object} usefulSets - object that contains a key and a count
     * @param {number} usefulSets["corine land cover"] - ex: count for corine land cover
     * @param {Object[]} allSets - array that contains facets with name and id
     * @param {Object} allSets[] - facets with name and id
     * @param {string} allSets[].name
     * @param {number} allSets[].id
     * @returns {Object} result - formated object with number, id and name
     * @returns {Object} result["corine land cover"] - facet
     * @returns {number} result["corine land cover"].id
     * @returns {string} result["corine land cover"].name
     * @returns {number} result["corine land cover"].number - count
     */
    formatSets(usefulSets, allSets) {
      let tempKeys = {};
      let result = {};

      Object.keys(usefulSets).map(key => {
        const formatedKey = key.toLowerCase().replace(/[^A-Z0-9]+/gi, '');
        tempKeys[formatedKey] = key;
      });

      allSets.map(dataset => {
        const datsetName = dataset.name || dataset + '';
        const tempDataName = datsetName
          .toLowerCase()
          .replace(/[^A-Z0-9]+/gi, '');
        const facetKey = tempKeys[tempDataName];

        if (facetKey) {
          result[facetKey] = {};
          result[facetKey].id = dataset.id ? dataset.id : new Date().getTime();
          result[facetKey].name = dataset.name ? dataset.name : dataset;
          result[facetKey].number = usefulSets[facetKey];
        }
      });

      return result;
    },

    searchByTerms(termType, term) {
      const resultTermType = termType || '';
      const resultTerm = term || '';
      const result = !resultTermType && !resultTerm ? '' : `?${resultTermType}=${resultTerm}`;

      return search(result);
    },

    /**
     * will get the dataTypes and set to each one the corresponding dataSets
     * there isn't a formal constraint on the database regarding which dataSet corresponds to which dataType
     * there for we will search for each DataType and see which dataSet facets comes back
     * will search by dataType name for each dataType
     * @returns {Object[]} - array of promises for each searchByTerms that will return the dataType it's sets
     */
    makeDataSetsPromisesForEachDataType(dataTypes) {
      let promisesSearchDataTypes = [];

      dataTypes.map(dataType => {
        promisesSearchDataTypes.push(
          (params => {
            return new Promise((resolve, reject) => {
              this.searchByTerms(facets.data_type, dataType.name)
                .then(result => {
                  resolve({
                    dataType: dataType,
                    result: result
                  });
                })
                .catch(error => {
                  reject(error);
                });
            });
          })()
        );
      });

      return promisesSearchDataTypes;
    },

    /**
     * after all the search requests for each dataType is done, it will assign the dataSets to each dataType
     * it's important to wait until the end of all the requests so that the checkbox components will get
     * the correct list, not undefined 
     * it will update this.dataTypes not the clone (test for performance)
     */
    assignDataSetsToEachDataType(promisesSetsForEachType, dataTypes) {
      Promise.all(promisesSetsForEachType).then(searchDataTypesResponses => {
        searchDataTypesResponses.map(response => {
          response.dataType.dataSets = this.formatSets(
            response.result.data.facets.data_set,
            this.allSets
          );
        });
        this.dataTypes = dataTypes.slice();
        this.showDateSets = true;
      });
    },

    handleSelectedDataSetsRaster(ev) {
      this.selectedDataSetsSample = ev.slice();
      this.handleSelectedDataSets();
    },

    handleSelectedDataSetsSample(ev) {
      this.selectedDataSetsRaster = ev.slice();
      this.handleSelectedDataSets();
    },

    handleSelectedDataSets() {
      this.selectedFilterOptions.data_set = [
        ...this.selectedDataSetsSample,
        ...this.selectedDataSetsRaster
      ];

      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    handleSelectedResourceTypes(ev) {
      this.selectedFilterOptions.resource_type = ev.slice();
      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    handleSelectedCountry(ev) {
      this.selectedFilterOptions.country = ev.slice();
      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    handleSelectedNutsLevels(ev) {
      this.selectedFilterOptions.nuts_level = ev.slice();
      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    handleSelectedTopicCategory(ev) {
      this.selectedFilterOptions.topic_category = ev.slice();
      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    handleSelectedPublishedYear(ev) {
      this.selectedFilterOptions.published_year = ev.slice();
      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    handleSelectedCollectionYears(ev) {
      this.selectedFilterOptions.collections_range = ev.slice();
      let searchQuery = this.makeSearchQuery();
      this.emitSelectedFilter(searchQuery);
    },

    makeSearchQuery() {
      let searchQuery = '';

      Object.keys(this.selectedFilterOptions).map(key => {
        switch (key)
        {
          case facets.published_year:
            searchQuery += this.makePublishedYearSearchQuery(this.selectedFilterOptions[key]);
            break;
          case facets.collections_range:
            searchQuery += this.makeCollectionsRangeSearchQuery(this.selectedFilterOptions[key]);
            break;
          default:
            const filter = this.selectedFilterOptions[key];

            if(Array.isArray(filter)) { // for all the checkboxes
              for (let i = 0; i < filter.length; i++) {
                const element = filter[i];
                searchQuery += `${key}=${element.name}&`;
              }
            } else if (filter) { // for the country, which can only be one, there for it's not array
              searchQuery += `${key}=${filter.name}&`;
            }               
        }
      });

      return searchQuery;
    },

    makePublishedYearSearchQuery(listOfYears) {
      if(listOfYears.length === 0) return '';

      let min = listOfYears[0] < listOfYears[1] ? listOfYears[0] : listOfYears[1];
      let max = listOfYears[0] > listOfYears[1] ? listOfYears[0] : listOfYears[1];
      let searchQuery = '';

      searchQuery += `${facets.published_year_range}=${min}__${max}&`;

      return searchQuery;
    },

    makeCollectionsRangeSearchQuery(listOfYears) {
      if(listOfYears.length === 0) return '';

      let min = listOfYears[0] < listOfYears[1] ? listOfYears[0] : listOfYears[1];
      let max = listOfYears[0] > listOfYears[1] ? listOfYears[0] : listOfYears[1];
      let searchQuery = '';

      searchQuery += `${facets.data_collection_start_year__lte}=${max}&${facets.data_collection_end_year__gte}=${min}&`;

      return searchQuery;
    },

    emitSelectedFilter(searchQuery) {
      this.$emit('updated-filters', searchQuery);
    },

    /**
     * - will update data for all child componentes
     * - !!the server returns only the data sets that have a value (everything that is 0, will not be received)
     * but we look for all received datasets and replace the existing number with the new one or with 0
     * this way the check-box-buttons component will always receive the same list, the count of each will differ
     * - used clones to avoid rendering on each property set
     */
    updateFacetsCount() {
      Object.keys(simpleFacets).map(key => {
        const faceName = simpleFacets[key].name;

        let entityClone = JSON.parse(JSON.stringify(this.facetsData[faceName]));

        Object.keys(entityClone).map(entityItemName => {
          const entityItem = this.facetsData[faceName][entityItemName];
          entityClone[entityItemName] = Object.assign(entityItem, {
            number: this.facets[faceName][entityItemName] || 0
          });
        });

        this.facetsData[faceName] = JSON.parse(JSON.stringify(entityClone));
      });

      let dataTypesClone = JSON.parse(JSON.stringify(this.dataTypes));
      dataTypesClone.map(dataType => {
        Object.keys(dataType.dataSets).map(key => {
          dataType.dataSets[key] = Object.assign(dataType.dataSets[key], {
            number: this.facets.data_set[key] || 0
          });
        });
      });
      this.dataTypes = JSON.parse(JSON.stringify(dataTypesClone));
    },

    renameLevels(levels) {
      const formattedLevels = JSON.parse(JSON.stringify(levels));

      Object.keys(formattedLevels).map((key, index) => {
        const level = formattedLevels[key];
        formattedLevels[key].displayName = level.name.replace('L','Level ');

        return level;
      });

      return formattedLevels;
    },

    sortObjKeysByPropertyNameAlphabetically(obj) {
      return Object.keys(obj)
        .sort((keyA, keyB) => {
          const itemA = obj[keyA];
          const itemB = obj[keyB];
          return itemA.name > itemB.name
        })
        .reduce((result, key, currentIndex) => {
          result[key] = obj[key];
          return result;
        }, {});
    },

    sortObjKeysAlphabetically(obj) {
      return Object
        .keys(obj)
        .sort((a,b) => a > b)
        .reduce((result, key) => {
          result[key] = obj[key];
          return result;
        }, {});
    },

    sortArrayOfObjectsByValueAlphabetically(arr) {
      const result = arr.slice();

      result.sort(function(a, b) {
        const nameA = a.name.toUpperCase(); // ignore upper and lowercase
        const nameB = b.name.toUpperCase();
        if (nameA < nameB) {
          return -1;
        }
        if (nameA > nameB) {
          return 1;
        }
        // names must be equal
        return 0;
      });
      return result;
    },

    putRegionsAheadOfCountriesSorted(countries) {
      const tempCountries = countries.slice();
      let regionsList = [];
      let result = [];
      // find all regions and insert them at the begining in result
      for (let i = 0; i < regions.length; i++) {
        const region = regions[i];
        var found = tempCountries.find(function(country) {
          return country.name.toUpperCase() === region.toUpperCase();
        });
        regionsList.push(found);
      }
      // remove all regions from countries
      for (let i = tempCountries.length - 1; i >= 0; i--) {
        const country = tempCountries[i];
        var found = regions.find(function(region) {
          return country.name.toUpperCase() === region.toUpperCase();
        });
        if(found) {
          tempCountries[i] = tempCountries[tempCountries.length - 1];
          tempCountries.pop();
        }
      }
      // concat regions with the remaining countrie sorted
      const sortedCountries = this.sortArrayOfObjectsByValueAlphabetically(tempCountries);
      result = [...regionsList, ...sortedCountries];

      return result;
    },
  },

  watch: {
    facets: function(val) {
      setTimeout(() => {
        this.updateFacetsCount();
      })
    }
  }
};
</script>

<style lang="scss">
.custom-select {
  background-color: transparent !important;
}
.nuts {
  label {
    display: inline-flex!important;
    margin-right: 2rem;
    .custom-control {
      max-width: 0px;
    }
  }
}
.bd-sidebar {
  height: 100%;
  top: 0;
  padding-right: 0;
}
.filters-title {
  color: #8DC84C;
  margin: 0;
  line-height: 2rem;
}

.filter-heading {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 1em;
  .fa-angle-down {
    font-size: 1.6em;
    color: #999;
  }
}
</style>

