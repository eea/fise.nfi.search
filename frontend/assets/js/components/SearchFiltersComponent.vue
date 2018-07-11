<template>
  <div class="jumbotron">
    <h4>FILTER RESULTS</h4>

    <!-- Select Country -->
    <h4>Country and region</h4>
    <div v-if="countries.length > 0">
      <selectCustom
        :dataList="countries"
        :componentName="'country'"
        :message="'Select country'"
        v-on:selected-country="handleSelectedCountry"
      ></selectCustom>
    </div>

    <!-- Select Data Sets -->
     <b-row v-if="showDateSets">
      <b-col>
        <checkBoxButtons 
          :dataList="dataTypes[0].dataSets" 
          :componentName="'dataSets-0'"
          :title="dataTypes[0].name"
          v-on:selected-dataSets-0="handleSelectedDataSetsRaster"
        ></checkBoxButtons>
      </b-col>   

      <b-col>
        <checkBoxButtons 
          :dataList="dataTypes[1].dataSets" 
          :componentName="'dataSets-1'"
          :title="dataTypes[1].name"
          v-on:selected-dataSets-1="handleSelectedDataSetsSample"
        ></checkBoxButtons>
      </b-col>
    </b-row>
    
    <!-- Select Result Formats -->
    <div v-if="(resourceTypes != null)">
      <h4>Result format</h4>
      <checkBoxButtons 
        :dataList="resourceTypes" 
        :componentName="'resourceTypes'"
        v-on:selected-resourceTypes="handleSelectedResourceTypes"
      ></checkBoxButtons>
    </div>

  </div>
</template>

<script>
import {
  fetchCountries,
  fetchDataSets,
  fetchDataTypes,
  fetchInfoLevels,
  fetchNutsLevels,
  fetchResourceTypes,
  search
} from '../api';
import CheckBoxButtons from './CheckBoxButtons';
import SelectCustom from './SelectCustom';

export default {
  name: 'SearchFiltersComponent',

  components: {
    checkBoxButtons: CheckBoxButtons,
    selectCustom: SelectCustom
  },

  props: {
    facets: {}
  },

  data() {
    return {
      countries: [],
      resourceTypes: null,
      dataTypes: {},
      selectedDataSetsSample: [],
      selectedDataSetsRaster: [],
      showDateSets: false,
      allSets: [],
      allResourceTypes: [],
      selectedFilterOptions: {
        country: '',
        resource_type: [],
        data_type: [],
        data_set: []
      }
    };
  },

  created() {
    this.getCountries();
    this.getResourceType();
    this.getTypesAndSets();
  },

  methods: {
    /**
     * will get the dataTypes and set to each one the corresponding dataSets
     * there isn't a formal contraint on the database regarding which dataSet corresponds to which dataType
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
              this.searchByTerms('data_type', dataType.name)
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

    getCountries() {
      fetchCountries()
        .then(response => {
          this.countries = response.data;
        })
        .catch(error => {
          console.log(error);
        });
    },

    /**
     * will get all the resource types but it will also make a new object that will contain the code and the number from facets
     * just like dataSets
     */
    getResourceType() {
      fetchResourceTypes()
        .then(response => {
          this.allResourceTypes = response.data;

          this.searchByTerms().then(response => {
            this.resourceTypes = this.formatSets(
              response.data.facets.resource_type,
              this.allResourceTypes
            );
          });
        })
        .catch(error => {
          console.log(error);
        });
    },

    searchByTerms(termType, term) {
      const resultTermType = termType || '';
      const resultTerm = term || '';

      return search(`?${resultTermType}=${resultTerm}`);
    },

    handleSelectedDataTypes(ev) {
      this.selectedFilterOptions.data_type = ev.slice();
      this.emitSelectedFilter();
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
      this.emitSelectedFilter();
    },

    handleSelectedResourceTypes(ev) {
      this.selectedFilterOptions.resource_type = ev.slice();
      this.emitSelectedFilter();
    },

    handleSelectedCountry(ev) {
      this.selectedFilterOptions.country = ev;
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
     * !!the server returns only the data sets that have a value (everything that is 0, will not be received)
     * but we look for all received datasets and replace the existing number with the new one or with 0
     * this way the CheckBoxButtons component will always receive the same list, the count of each will differ
     * used clones to avoid rendering on each property set
     */
    updateFacetsCount() {
      const resourceTypesClone = JSON.parse(JSON.stringify(this.resourceTypes));
      const dataTypesClone = JSON.parse(JSON.stringify(this.dataTypes));

      dataTypesClone.map(dataType => {
        Object.keys(dataType.dataSets).map(key => {
          dataType.dataSets[key] = Object.assign(dataType.dataSets[key], {
            number: this.facets.data_set[key] || 0
          });
        });
      });

      Object.keys(resourceTypesClone).map(key => {
        resourceTypesClone[key] = Object.assign(this.resourceTypes[key], {
          number: this.facets.resource_type[key] || 0
        });
      });

      this.dataTypes = JSON.parse(JSON.stringify(dataTypesClone));
      this.resourceTypes = JSON.parse(JSON.stringify(resourceTypesClone));
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
