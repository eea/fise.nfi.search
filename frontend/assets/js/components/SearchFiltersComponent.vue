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

    <!-- Select Data Type -->
    <!-- <div v-if="dataTypes.length > 0">
      <h4>Result type</h4>
      <checkBoxButtons 
        :dataList="dataTypes"
        :componentName="'dataTypes'"
        v-on:selected-dataTypes="handleSelectedDataTypes"
      ></checkBoxButtons>
    </div> -->
    <!-- <p
      v-for="dataItem in dataTypes"
      :key="dataItem.id"
    >{{dataItem.name}}
    </p> -->

    <!-- Select Data Sets -->
    <!-- <b-row v-if="allDataSets.length > 0">
      <b-col>
        <checkBoxButtons 
          :dataList="allDataSets.slice(1,3)" 
          :componentName="'dataSets'"
          v-on:selected-dataSets="handleSelectedDataSets"
        ></checkBoxButtons>
      </b-col>

      <b-col>
        <checkBoxButtons 
          :dataList="allDataSets.slice(3,5)" 
          :componentName="'dataSets'"
          v-on:selected-dataSets="handleSelectedDataSets"
        ></checkBoxButtons>
      </b-col>
    </b-row> -->
    <!-- Select Data Sets -->
    <b-row v-if="showDateSets">
      <b-col>
        <checkBoxButtons 
          :dataList="dataTypes[0].dataSets" 
          :componentName="'dataSets-0'"
          :title="dataTypes[0].name"
          v-on:selected-dataSets-0="handleSelectedDataSets0"
        ></checkBoxButtons>
      </b-col>

      <b-col>
        <checkBoxButtons 
          :dataList="dataTypes[1].dataSets" 
          :componentName="'dataSets-1'"
          :title="dataTypes[1].name"
          v-on:selected-dataSets-1="handleSelectedDataSets1"
        ></checkBoxButtons>
      </b-col>
    </b-row>
    
    <!-- Select Result Formats -->
    <div v-if="(resourceTypes.length > 0)">
      <h4>Result format</h4>
      <checkBoxButtons 
        :dataList="resourceTypes" 
        :componentName="'resourceTypes'"
        v-on:selected-resourceTypes="handleSelectedResourceTypes"
      ></checkBoxButtons>
    </div>

    <!-- Select ranged years -->
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
} from "../api";
import CheckBoxButtons from "./CheckBoxButtons";
import SelectCustom from "./SelectCustom";

export default {
  name: "SearchFiltersComponent",

  components: {
    checkBoxButtons: CheckBoxButtons,
    selectCustom: SelectCustom
  },

  data() {
    return {
      countries: [],
      resourceTypes: [],
      dataTypes: [],
      dataSets0: [],
      dataSets1: [],
      // allDataSets: [],
      showDateSets: false,
      selectedFilterOptions: {
        country: "",
        resource_type: [],
        data_type: [],
        data_set: []
      }
    };
  },

  created() {
    this.getCountries();
    this.getResourceType();
    // this.getDataType();
    // this.getAllDataSets();
    this.getTypesAndSets();
  },

  methods: {
    getTypesAndSets() {
      let promiseParalel = [];

      promiseParalel.push(fetchDataTypes());
      promiseParalel.push(fetchDataSets());

      Promise.all(promiseParalel).then(dataTypesResponse => {
        // console.log(dataTypesResponse);
        let dataTypes = dataTypesResponse[0].data;
        let allDataSets = dataTypesResponse[1].data;
        dataTypes.map(dataType => {
          // console.log(dataType);
          this.searchByTerms("data_type", dataType).then(response => {
            // console.log(response);
            // dataType.dataSets = response.data.facets.data_set;
            dataType.dataSets = this.filterDataSets(
              response.data.facets.data_set,
              allDataSets
            );
            // console.log(dataType);
            // console.log(this.filterDataSets(dataType.dataSets, allDataSets));
          });
        });
        this.dataTypes = dataTypes.slice();
          console.log(this.dataTypes);
        setTimeout(()=> {
          this.showDateSets = true;
          // console.log(this.dataTypes);
        }, 1000);
        // console.log(dataTypes);
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

    getResourceType() {
      fetchResourceTypes()
        .then(response => {
          this.resourceTypes = response.data;
        })
        .catch(error => {
          console.log(error);
        });
    },

    getDataType() {
      fetchDataTypes()
        .then(response => {
          let dataTypes = response.data;
          this.dataTypes = response.data;
          // dataTypes.map(dataType => {
          //   this.searchByTerms("data_type", dataType)
          //     .then(responseDataSets => {
          //       dataType.dataSets = response.data;
          //       console.log("dataType", dataType);
          //     })
          //     .catch(error => {
          //       console.log(error);
          //     });
          // });
        })
        .catch(error => {
          console.log(error);
        });
    },

    // getAllDataSets() {
    //   fetchDataSets()
    //     .then(response => {
    //       this.allDataSets = response.data;
    //       // this.getDataSetsForSelectedDataTypes();
    //     })
    //     .catch(error => {
    //       console.log(error);
    //     });
    // },

    searchByTerms(termType, term) {
      if (!termType) {
        termType = "search";
      }
      return search(`?${termType}=${term.name}`);
    },

    handleSelectedDataTypes(ev) {
      this.selectedFilterOptions.data_type = ev.slice();
      // this.getDataSetsForSelectedDataTypes();
      this.emitSelectedFilter();
    },

    handleSelectedDataSets0(ev) {
      this.dataSets0 = ev.slice();
      console.log(ev)
      this.handleSelectedDataSets();
    },

    handleSelectedDataSets1(ev) {
      this.dataSets1 = ev.slice();
      console.log(ev)
      this.handleSelectedDataSets();
    },

    handleSelectedDataSets() {
      this.selectedFilterOptions.data_set = [...this.dataSets0, ...this.dataSets1];
      console.log(this.selectedFilterOptions.data_set)
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
      this.$emit("updated-filters", this.selectedFilterOptions);
    },

// NOT USED
    // getDataSetsForSelectedDataTypes() {
    //   let promiseParalel = [];
    //   let usefulDataSets = {};
    //   this.dataSets = [];

    //   this.selectedFilterOptions.data_type.map(dataType => {
    //     promiseParalel.push(this.searchByTerms("data_type", dataType));
    //   });

    //   Promise.all(promiseParalel).then(dataTypesResponse => {
    //     dataTypesResponse.map(dataTypeSearchedResponse => {
    //       usefulDataSets = Object.assign(
    //         usefulDataSets,
    //         dataTypeSearchedResponse.data.facets.data_set
    //       );
    //     });

    //     this.dataSets = this.filterDataSets(usefulDataSets).slice();
    //   });
    // },

    filterDataSets(usefulDataSets, allDataSets) {
      let tempKeys = {};
      // let tempDateSets = [];
      let data = {};

// console.log('!!!!!!!!usefulDataSets', usefulDataSets);
// console.log(allDataSets);

      Object.keys(usefulDataSets).map(key => {
        const formatedKey = key.toLowerCase().replace(/[^A-Z0-9]+/gi, "");
        tempKeys[formatedKey] = key;
      });

      allDataSets.map(dataset => {
        const tempDateSetName = 
          dataset.name
          .toLowerCase()
          .replace(/[^A-Z0-9]+/gi, "");
        const test = tempKeys[tempDateSetName];
              // console.log('@@@@@dataset', dataset);
              // console.log('#####test', test);


        if (test) {
          data[tempKeys[tempDateSetName]] = dataset;
          data[tempKeys[tempDateSetName]].number = usefulDataSets[tempKeys[tempDateSetName]];

          // tempDateSets.push(data);
        }
      });
      // console.log('result', tempDateSets);
              // console.log('#####data', data);
      return data;
    }
  }
};
</script>

<style>


.custom-select {
    background-color: transparent!important;
}
</style>
