<template>
  <div id="dataTypeCheckbox">
    <div class="nuts"
        v-if="Object.keys(dataTypeSets).length > 0"
        v-for="item in dataTypeSets"
        v-bind:key="item.typeCode">
      <check-box-buttons
        :checkboxDataList="item.data"
        :componentName="item.typeCode"
        :title="item.typeName"
        v-on="eventsObj"
        :clearAllFilters="clearAllFilters"
      ></check-box-buttons>
      <hr>
    </div>
  </div>
</template>

<script>
import CheckBoxButtons from "./CheckBoxButtons";
import filters from "../mixins/filters";
import { search } from '../api';

export default {
  name: "DataTypeComponent",

  components: {
    "check-box-buttons": CheckBoxButtons
  },

  props: {
    dataTypes: {},
    dataSets: {},
    clearAllFilters: false,
  },

  mixins: [filters],

  created() {
    this.makeEventsListenerObject();
    this.makeDataSetsForEachDataType();
  },

  data() {
    return {
      selected: {},
      dataTypeSets: {},
      eventsObj: {},
      componentName: 'data_set',
    };
  },

  methods: {
    /**
     * creates a dynamic event for each type
     * for each type the handler is the same
     * using a closure so that it knows to which type it is assigned
     * the event will issue with the already made search query
     */
    makeEventsListenerObject() {
      const reducer = (accumulator, currentValue) => {
        let eventListenerObj = {};

        eventListenerObj[`selected-${currentValue}`] = ((currentValue) => {
          const currentDataType = currentValue;
          const handleSelectedSet = (ev) => {
            this.selected[currentDataType] = this.selected[currentDataType] ? this.selected[currentDataType] : {};
            this.selected[currentDataType] = ev;

            let result = '';
            const allSetsNames = [];
            
            Object.keys(this.selected).map((dataType) => {
              this.selected[dataType].map((item) => {
                allSetsNames.push(item.name);
              });
              result = `&${this.componentName}=` + allSetsNames.join(`&${this.componentName}=`);              
            })

            this.$emit(`selected-filter-${this.componentName}`, result);
          }

          return handleSelectedSet;

        })(currentValue);

        return Object.assign({}, accumulator, eventListenerObj);
      };
      const dataTypes = Object.keys(this.dataTypes);
      const facetSets = dataTypes.reduce(reducer, {});
      
      this.eventsObj = Object.assign({}, facetSets);
    },
    makeDataSetsForEachDataType() {
      const promises = [];
      let result = {}
      
      Object.keys(this.dataTypes).map(key => {
        const typeName = this.dataTypes[key].name;
        promises.push(this.wrapPromiseSearchForDataType(typeName, key));
      });

      Promise.all(promises).then(response => {

        response.map((responseItem) => {
          const dataType = responseItem.typeCode;

          result[dataType] = responseItem;
        })
        this.dataTypeSets = Object.assign({}, result);
      })
      .catch(error => {
        console.log(error);
      });
    },
    wrapPromiseSearchForDataType(typeName, typeCode) {
      return new Promise((resolve, reject) => {
        search(`?data_type=${typeName}`)
          .then(response => {
            resolve({ 
              data: this.takeTheDataSet(response.data.facets.data_set),
              typeName: typeName,
              typeCode: typeCode
            });
          })
          .catch(error => {
            reject(error);
          });
      });
    },
    takeTheDataSet(dataSetObj) {
      const result = [];
      Object.keys(dataSetObj).map((key) => {
        const dataSetItem = this.dataSets[key];
        dataSetItem.setCode = key;
        result.push(dataSetItem);
      });
      return result;
    },
  },
  watch:{
    dataSets: function(val) {
      let result = {};

      Object.keys(this.dataTypeSets).map(typeKey => {
        const dataType = this.dataTypeSets[typeKey];
        result[typeKey] = {data: [], typeCode: dataType.typeCode, typeName: dataType.typeName};

        dataType.data.map(set => {
          const tempSet = Object.assign(set);
          tempSet.number = val[set.setCode].number;
          result[typeKey].data.push(tempSet);
        });
      });
      this.dataTypeSets = result;
    },
    clearAllFilters: function() {
      this.selected = {};
    }
  },

};
</script>

<style>
</style>
