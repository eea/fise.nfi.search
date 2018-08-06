<template>
  <div class="jumbotron">
    <h4>FILTER RESULTS</h4>

    <!-- Select Country -->
    <h4>Country and region</h4>
    <div v-if="countries.length > 0">
      <select-custom
        :dataList="countries"
        :componentName="'country'"
        :message="'Select country'"
        v-on:selected-country="handleSelectedCountry"
      ></select-custom>
    </div>


    <!-- Select Keywords -->
    <div v-if="facetsData.keyword">
      <h4>Keywords</h4>
      <bar-chart
        :dataList="facetsData.keyword" 
        :componentName="'keyword'"
        v-on:selected-keyword="handleSelectedKeywords"
      ></bar-chart>
    </div>

    <!-- Select Nuts Levels -->
    <div v-if="facetsData.nuts_level">
      <h4>Nuts Levels</h4>
      <check-box-buttons
        :dataList="facetsData.nuts_level" 
        :componentName="'nutsLevels'"
        v-on:selected-nutsLevels="handleSelectedNutsLevels"
      ></check-box-buttons>
    </div>

    <!-- Select Keywords
    <div v-if="facetsData.keyword">
      <h4>Keywords</h4>
      <check-box-buttons
        :dataList="facetsData.keyword" 
        :componentName="'keyword'"
        v-on:selected-keyword="handleSelectedKeywords"
      ></check-box-buttons>
    </div> -->
    
    <!-- Select Data Sets -->
      <b-row v-if="showDateSets">
      <b-col>
        <check-box-buttons
          :dataList="dataTypes[0].dataSets" 
          :componentName="'dataSets-0'"
          :title="dataTypes[0].name"
          v-on:selected-dataSets-0="handleSelectedDataSetsRaster"
        ></check-box-buttons>
      </b-col>

      <b-col>
        <check-box-buttons
          :dataList="dataTypes[1].dataSets" 
          :componentName="'dataSets-1'"
          :title="dataTypes[1].name"
          v-on:selected-dataSets-1="handleSelectedDataSetsSample"
        ></check-box-buttons>
      </b-col>
    </b-row>

    <!-- Select Topic Category -->
    <div v-if="facetsData.topic_category">
      <h4>Topic Category</h4>
      <check-box-buttons
        :dataList="facetsData.topic_category" 
        :componentName="'topicCategory'"
        v-on:selected-topicCategory="handleSelectedTopicCategory"
      ></check-box-buttons>
    </div>

    <!-- Select Result Formats -->
    <div v-if="facetsData.resource_type">
      <h4>Result format</h4>
      <check-box-buttons
        :dataList="facetsData.resource_type" 
        :componentName="'resourceTypes'"
        v-on:selected-resourceTypes="handleSelectedResourceTypes"
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
  search
} from '../api';
import CheckBoxButtons from './CheckBoxButtons';
import SelectCustom from './SelectCustom';
import BarChart from './BarChart';

const facets = {
  country: 'country',
  data_set: 'data_set',
  data_type: 'data_type',
  resource_type: 'resource_type',
  nuts_level: 'nuts_level',
  topic_category: 'topic_category',
  year_published: 'year_published',
  year_collected: 'year_collected',
  keyword: 'keyword',
}

const simpleFacets = {
  resource_type: { name: facets.resource_type, handler: fetchResourceTypes },
  nuts_level: { name: facets.nuts_level, handler: fetchNutsLevels },
  topic_category: { name: facets.topic_category, handler: fetchTopicCategories },
  keyword: { name: facets.keyword, handler: fetchKeywords },
}

export default {
  name: 'SearchFiltersComponent',

  components: {
    'check-box-buttons': CheckBoxButtons,
    'select-custom': SelectCustom,
    'bar-chart': BarChart,
  },

  props: {
    facets: {}
  },

  data() {
    return {
      countries: [],
      dataTypes: null,
      facetsData: {},
      selectedDataSetsSample: [],
      selectedDataSetsRaster: [],
      showDateSets: false,
      sourceOfUpdate: null,
      selectedFilterOptions: {},
    };
  },

  created() {
    this.makeSelectedFilterOptions();
    this.getCountries();
    this.getFacets();
    this.getTypesAndSets();
  },

  methods: {

    makeSelectedFilterOptions() {
      Object.keys(facets).map(key => {
        if(key === 'country') {
          this.selectedFilterOptions[key] = '';
        } else {
          this.selectedFilterOptions[key] = [];
        }
      });
    },

    getCountries() {
      fetchCountries()
        .then(response => {
          this.countries = response.data;
        })
        .catch(error => {
          console.log(error);
        });
    },

    getFacets() {
      const promises = [];
      const facetsData = {};
      
      Object.keys(simpleFacets).map(key => {
        const entity = simpleFacets[key];
        promises.push(this.wrapPromiseGetEntity(entity));
      });
      promises.push(this.searchByTerms());

      Promise.all(promises).then(response => {
        const responseLength = response.length;
        const entities = response.slice(0, responseLength-1);
        const facets = response[responseLength-1].data.facets;
        
        entities.map(entity => {
          const entityName = entity.name;
          const entityData = entity.data;
          facetsData[entityName] = this.formatSets(
            facets[entityName],
            entityData
          );
        })

        this.facetsData = JSON.parse(JSON.stringify(facetsData));
      })
      .catch(error => {
        console.log(error);
      });
    },

    wrapPromiseGetEntity(entity) {
      return new Promise((resolve, reject) => {
        entity.handler()
          .then(response => {
            resolve({ data: response.data, name: entity.name });
          })
          .catch(error => {
            reject(error);
          });
      });
    },
    /**
     * will get the dataTypes and set to each one the corresponding dataSets
     * there isn't a formal constraint on the database regarding which dataSet corresponds to which dataType
     * there for we will search for each DataType and see which dataSet facets comes back
     */
    getTypesAndSets() {
      let promiseParalel = [];

      promiseParalel.push(fetchDataTypes());
      promiseParalel.push(fetchDataSets());

      Promise.all(promiseParalel).then(typesAndSetsResponse => {
        let dataTypes = typesAndSetsResponse[0].data;
        this.allSets = typesAndSetsResponse[1].data;

        let promisesSearchDataTypes = this.makeDataSetsPromisesForEachDataType(dataTypes);

        this.assignDataSetsToEachDataType(promisesSearchDataTypes, dataTypes);
      });
    },

    searchByTerms(termType, term) {
      const resultTermType = termType || '';
      const resultTerm = term || '';

      return search(`?${resultTermType}=${resultTerm}`);
    },

    /**
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
     * aftter all the search requests for each dataType is done, it will assign the dataSets to each dataType
     * it's important to wait until the end of all the requests so that the checkboxe components will get
     * the correct list, not undefined 
     * TODO try and give to each checkbox component only what it need and when it's done, don't wait for all
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
      this.sourceOfUpdate = facets.data_type;
      this.emitSelectedFilter();
    },

    handleSelectedResourceTypes(ev) {
      this.selectedFilterOptions.resource_type = ev.slice();
      this.sourceOfUpdate = facets.resource_type;
      this.emitSelectedFilter();
    },

    handleSelectedCountry(ev) {
      this.selectedFilterOptions.country = ev;
      this.sourceOfUpdate = 'country';
      this.emitSelectedFilter();
    },

    handleSelectedNutsLevels(ev) {
      this.selectedFilterOptions.nuts_level = ev;
      this.sourceOfUpdate = 'nuts_level';
      this.emitSelectedFilter();
    },

    handleSelectedTopicCategory(ev) {
      console.log(ev)
      this.selectedFilterOptions.topic_category = ev;
      this.sourceOfUpdate = 'topic_category';
      this.emitSelectedFilter();
    },

    handleSelectedKeywords(ev) {
      console.log(ev)
      this.selectedFilterOptions.keywords = ev;
      this.sourceOfUpdate = 'keywords';
      this.emitSelectedFilter();
    },

    emitSelectedFilter() {
      this.$emit('updated-filters', this.selectedFilterOptions);
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
        const tempDataName = dataset.name
          .toLowerCase()
          .replace(/[^A-Z0-9]+/gi, '');
        const facetKey = tempKeys[tempDataName];

        if (facetKey) {
          result[facetKey] = dataset;
          result[facetKey].number = usefulSets[facetKey];
        }
      });

      return result;
    },

    /**
     * - will update data for all child componentes except for the one that started the update
     * - !!the server returns only the data sets that have a value (everything that is 0, will not be received)
     * but we look for all received datasets and replace the existing number with the new one or with 0
     * this way the check-box-buttons component will always receive the same list, the count of each will differ
     * - used clones to avoid rendering on each property set
     */
    updateFacetsCount() {
      Object.keys(simpleFacets).map(key => {
        const faceName = simpleFacets[key].name;

        if(this.sourceOfUpdate !== faceName) {
          let entityClone = JSON.parse(JSON.stringify(this.facetsData[faceName]));

          Object.keys(entityClone).map(entityItemName => {
            const entityItem = this.facetsData[faceName][entityItemName];
            
            entityClone[entityItemName] = Object.assign(entityItem, {
              number: this.facets[faceName][entityItemName] || 0
            });
          });

          this.facetsData[faceName] = JSON.parse(JSON.stringify(entityClone));
        }
      });

      if(this.sourceOfUpdate !== facets.data_type) {
        let dataTypesClone = JSON.parse(JSON.stringify(this.dataTypes));
        dataTypesClone.map(dataType => {
          Object.keys(dataType.dataSets).map(key => {
            dataType.dataSets[key] = Object.assign(dataType.dataSets[key], {
              number: this.facets.data_set[key] || 0
            });
          });
        });
        this.dataTypes = JSON.parse(JSON.stringify(dataTypesClone));
      }
    }
  },

  watch: {
    facets: function(val) {
      this.updateFacetsCount();
    }
  }
};
</script>

<style>
.custom-select {
  background-color: transparent !important;
}
</style>
