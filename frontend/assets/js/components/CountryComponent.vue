<template>
   <div id="multiselect">
    <multiselect 
      v-model="selected" 
      :options="countryList"
      :multiple="true"
      track-by="name"
      :custom-label="customLabel" 
    >
    </multiselect>
  </div>
</template>

<script>
import Multiselect from "vue-multiselect";

const regions = ['EEA39', 'EU28', 'FAO234', 'SOEF46'];
let emitUpdate = true;

export default {
  name: "CountryComponent",

  components: {
    multiselect: Multiselect
  },

  props: {
    dataList: {},
    clearAllFilters: false,
  },

  data() {
    return {
      selected: [],
      componentName: 'country',
    };
  },

  computed: {
    // will make an array from the object dataList
    countryList: function transformFromObjectToArray() {
      const result = [];

      Object.keys(this.dataList).map((key) => {
        const element = Object.assign({}, this.dataList[key]);

        result.push(element);
      });

      return this.putRegionsAheadOfCountriesSorted(result);
    }
  },

  methods: {
    handleEmit() {
      setTimeout(() => {
        let result = '';
        const allCountriesNames = [];

        this.selected.map((item) => {
          allCountriesNames.push(item.name)
        });
        result = `&${this.componentName}=` + allCountriesNames.join(`&${this.componentName}=`);

        // will emit after the render updates the model
        this.$emit(`selected-filter-${this.componentName}`, result);
      });
    },

    customLabel(option) {
      return `${option.name}`;
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
  },

  watch: {
    selected: function(val) {
      emitUpdate ? this.handleEmit() : null;
      emitUpdate = true;
    },
    clearAllFilters: function() {
      emitUpdate = false;
      this.selected = [];
    }
  }
};
</script>

<style>
#multiselect {
  position: relative;
  z-index: 6;
}
</style>
