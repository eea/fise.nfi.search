<template>
  <div class="">
    <h4 class="filters-title">FILTERS
      <a
        v-show="showClearAll"
        role="button"
        class="clear-all"
        @click="onClearAllFilters"
      >
        CLEAR
      </a>
    </h4>

    <hr>

    <!-- Select Topic Category -->
    <div v-if="facetsData.topic_category">
      <topic-category
        :dataList="facetsData.topic_category"
        :clearAllFilters="clearAllFilters"
        @selected-filter-topic_category="handleSelectedTopicCategory"
      ></topic-category>
    </div>

    <hr>

    <!-- Select Country-->
    <h4 class="filter-heading">Countries and regions</h4>
    <div v-if="facetsData.country">
      <country-component
        :dataList="facetsData.country"
        :clearAllFilters="clearAllFilters"
        @selected-filter-country="handleSelectedCountry"
      ></country-component>
    </div>

    <hr>

    <!-- Select NUTS Level -->
    <div v-if="facetsData.nuts_level">
      <nuts-level
        :dataList="facetsData.nuts_level"
        :clearAllFilters="clearAllFilters"
        @selected-filter-nuts_level="handleSelectedNutsLevels"
      ></nuts-level>
    </div>

    <hr>

    <!-- Select Published Year -->
    <div v-if="facetsData.published_year">
      <div class="filter-heading">Published year</div>
      <published-years
        :dataList="facetsData.published_year"
        :clearAllFilters="clearAllFilters"
        @selected-filter-published_year="handleSelectedPublishedYear"
      ></published-years>
    </div>

    <!-- Select Collection Years -->
    <div v-if="facetsData.collections_range">
      <div class="filter-heading">Collection years</div>
      <collection-years
        :dataList="facetsData.collections_range"
        :clearAllFilters="clearAllFilters"
        @selected-filter-collections_range="handleSelectedCollectionYears"
      ></collection-years>
    </div>

    <hr>

    <!-- Data sets -->
    <div v-if="facetsData.data_set && facetsData.data_type">
      <data-type-component
        :dataTypes="facetsData.data_type"
        :dataSets="facetsData.data_set"
        :clearAllFilters="clearAllFilters"
        @selected-filter-data_set="handleSelectedDataSets"
      ></data-type-component>
    </div>

    <!-- Select Result Formats -->
    <div v-if="facetsData.resource_type">
      <results-format
        :dataList="facetsData.resource_type"
        :clearAllFilters="clearAllFilters"
        @selected-filter-resource_type="handleSelectedResourceTypes"
      ></results-format>
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
  getPublicationYearsFormatted,
  getCollectionYearsFormatted,
  search
} from '../api';
import NutsLevelComponent from './NutsLevelComponent';
import TopicCategoryComponent from './TopicCategoryComponent';
import ResultsFormatComponent from './ResultsFormatComponent';
import PublishedYearsComponent from './PublishedYearsComponent';
import CollectionYearsComponent from './CollectionYearsComponent';
import CountryComponent from './CountryComponent';
import DataTypeComponent from './DataTypeComponent';

const queryParams = {
  country: 'country',
  data_set: 'data_set',
  data_type: 'data_type',
  resource_type: 'resource_type',
  nuts_level: 'nuts_level',
  topic_category: 'topic_category',
  published_year: 'published_year',
  collections_range: 'collections_range',
  keyword: 'keyword',
  published_year_range: 'published_year__range',
  data_collection_end_year: 'data_collection_end_year',
  data_collection_start_year: 'data_collection_start_year',
  data_collection_start_year__lte: 'data_collection_start_year__lte',
  data_collection_end_year__gte: 'data_collection_end_year__gte',
}

const facets = {
  country: { entityName: queryParams.country, getFunction: fetchCountries, facetNames: [queryParams.country] },
  nuts_level: { entityName: queryParams.nuts_level, getFunction: fetchNutsLevels, facetNames: [queryParams.nuts_level] },
  published_year: { entityName: queryParams.published_year, getFunction: getPublicationYearsFormatted, facetNames: [queryParams.published_year] },
  collections_range: { entityName: queryParams.collections_range, getFunction: getCollectionYearsFormatted, facetNames: [queryParams.data_collection_end_year, queryParams.data_collection_start_year] },
  topic_category: { entityName: queryParams.topic_category, getFunction: fetchTopicCategories, facetNames: [queryParams.topic_category] },
  resource_type: { entityName: queryParams.resource_type, getFunction: fetchResourceTypes, facetNames: [queryParams.resource_type] },
  keyword: { entityName: queryParams.keyword, getFunction: fetchKeywords, facetNames: [queryParams.keyword] },
  data_set: { entityName: queryParams.data_set, getFunction: fetchDataSets, facetNames: [queryParams.data_set] },
  data_type: { entityName: queryParams.data_type, getFunction: fetchDataTypes, facetNames: [queryParams.data_type] },
}

/**
 * will create the facets using checkboxes, dropdowns, sliders and graphs
 * will autoupdate the count on each value of each facet
 */
export default {
  name: 'SearchFiltersComponent',

  components: {
    'nuts-level': NutsLevelComponent,
    'topic-category': TopicCategoryComponent,
    'results-format': ResultsFormatComponent,
    'published-years': PublishedYearsComponent,
    'collection-years': CollectionYearsComponent,
    'country-component': CountryComponent,
    'data-type-component': DataTypeComponent,
  },

  props: {
    facets: {},
  },

  data() {
    return {
      clearAllFilters: false,
      facetsData: {},
      facetEntities: [],
      selectedFilterOptions: {},
      showClearAll: false
    };
  },

  created() {
    this.initSelectedFilterOptions();
    this.makeFacets();
  },

  methods: {
    onClearAllFilters() {
      this.showClearAll = false;
      this.clearAllFilters = !this.clearAllFilters;
      this.initSelectedFilterOptions();
      this.$emit('updated-filters', this.selectedFilterOptions);
    },
    /**
     * this.selectedFilterOptions will contain the names of all the facets names
     * here all the selected values from the facets will be available
     * based on these selections, the search query will be created
     */
    initSelectedFilterOptions() {
      Object.keys(facets).map(key => {
        this.selectedFilterOptions[key] = '';
      });
    },

    /**
     * all requests are done at the same time, using one simple search to get the facets names and count
     */
    makeFacets() {
      const promises = [];
      
      Object.keys(facets).map(key => {
        const entity = facets[key];
        promises.push(this.wrapPromiseGetEntity(entity));
      });
      promises.push(this.searchByTerms());

      Promise.all(promises).then(response => {
        const responseLength = response.length;
        const facets = response[responseLength - 1].data.facets;

        this.facetEntities = response.slice(0, responseLength - 1);
        this.facetsData = this.composeFacets(this.facetEntities, facets);
      })
      .catch(error => {
        console.log(error);
      });
    },

    composeFacets(facetEntities, facets) {
      let result = {};

      facetEntities.map(entity => {
        const facetNames = entity.facetNames;
        const entityName = entity.entityName;
        const entityData = entity.data;
        const reducer = (accumulator, currentValue) => {
          return Object.assign({}, facets[accumulator], facets[currentValue]);
        };
        const facetSets = facetNames.reduce(reducer, facetNames[0]);

        result[entityName] = this.formatSets(
          facetSets,
          entityData
        );

      });
      return result;
    },

    wrapPromiseGetEntity(entity) {
      return new Promise((resolve, reject) => {
        entity.getFunction()
          .then(response => {
            resolve({
              data: response.data,
              facetNames: entity.facetNames,
              entityName: entity.entityName
            });
          })
          .catch(error => {
            reject(error);
          });
      });
    },

    /**
     * @param {Object} facetSets - object that contains the keys with count of facets
     * @param {number} facetSets["corine land cover"] - facet ex: count for corine land cover
     * @param {Object[]} facetEntitySets - array that contains facets with name and id
     * @param {Object} facetEntitySets[] - facets with name and id
     * @param {string} facetEntitySets[].name
     * @param {number} facetEntitySets[].id
     * @returns {Object} result - formated object with number, id and name
     * @returns {Object} result["corine land cover"] - facet
     * @returns {number} result["corine land cover"].id
     * @returns {string} result["corine land cover"].name
     * @returns {number} result["corine land cover"].number - count
     */
    formatSets(facetSets, facetEntitySets) {
      let tempKeys = {};
      let result = {};

      facetEntitySets.map(item => {
        const formatedItemName = item.name.toLowerCase();
        result[formatedItemName] = {};
        result[formatedItemName].id = item.id ? item.id : new Date().getTime();
        result[formatedItemName].name = item.name ? item.name : item;
        result[formatedItemName].number = facetSets[formatedItemName] || 0;
      });

      return result;
    },

    searchByTerms(termType, term) {
      return search('');
    },

    handleSelectedDataSets(ev) {
      this.selectedFilterOptions.data_set = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedResourceTypes(ev) {
      this.selectedFilterOptions.resource_type = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedCountry(ev) {
      this.selectedFilterOptions.country = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedNutsLevels(ev) {
      this.selectedFilterOptions.nuts_level = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedTopicCategory(ev) {
      this.selectedFilterOptions.topic_category = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedPublishedYear(ev) {
      this.selectedFilterOptions.published_year = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedCollectionYears(ev) {
      this.selectedFilterOptions.collections_range = ev.slice();
      this.emitSelectedFilter();
    },

    resetAllFilters() {
      const result = {};
      Object.keys(this.selectedFilterOptions).map((key) => {
        result[key] = '';
      });
      this.selectedFilterOptions = result;
    },

    emitSelectedFilter() {
      this.showClearAll = true;
      this.$emit('updated-filters', this.selectedFilterOptions);
    },

    updateFacetsCount() {
      this.facetsData = this.composeFacets(this.facetEntities, this.facets);
    },
  },

  watch: {
    facets: function(val) {
      setTimeout(() => {
        this.updateFacetsCount();
      })
    },
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
    margin-right: 1rem;
    position: absolute;
    width: calc(50% - 1rem);
    .custom-control {
      max-width: 0px;
    }
  }
  .filter-group > label {
    position: relative;
  }
}
.bd-sidebar {
  height: 100%;
  top: 0;
  padding-right: 0;
  font-size: 14px;
}
.filters-title {
  margin: 0;
  line-height: 2rem;
  font-weight: bold;
  color: #444;
  font-size: 16px;
  font-weight: bold;
  a {
    color: #CC4400!important;
    font-size: 13px;
    font-weight: 300;
  }
}

.filter-heading {
  font-weight: bold;
  margin-bottom: 1rem;
  color: #225511;
  font-size: 18px;
  .fa-angle-down {
    font-size: 1.6em;
    color: #999;
  }
}

.filter-heading--date {
  color: var(--fise-dark-green)
}

.clear-all {
  font-size: .8rem;
  position: absolute;
  top: 0;
  right: 0;
  cursor: pointer;
}
.clear-all >i {
  color: red;
}
</style>

