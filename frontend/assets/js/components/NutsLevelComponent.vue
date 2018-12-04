<template>
  <div id="nutsCheckbox">
    <div class="nuts">
      <check-box-buttons
        :checkboxDataList="nutsLevels"
        :componentName="componentName"
        :title="title"
        v-on:selected-nuts_level="handleSelectedNutsLevels"
        :clearAllFilters="clearAllFilters"
      ></check-box-buttons>
    </div>
  </div>
</template>

<script>
import CheckBoxButtons from "./CheckBoxButtons";
import filters from '../mixins/filters';

export default {
  name: "NutsLevelComponent",

  components: {
    "check-box-buttons": CheckBoxButtons
  },

  props: {
    dataList: {},
    clearAllFilters: false,
  },

  mixins: [filters],

  data() {
    return {
      componentName: 'nuts_level',
      title: 'NUTS levels'
    };
  },

  computed: {
    nutsLevels: function transformFromObjectToArray() {
      const result = [];

      Object.keys(this.dataList).map(key => {
        const formattedName = this.renameLevel(this.dataList[key].name);
        const element = Object.assign({}, this.dataList[key], { displayName: formattedName });

        result.push(element);
      });

      return result.sort(this.sortArrayOfObjectsByName);
    },
  },

  methods: {
    handleSelectedNutsLevels(ev) {
      let result = '';
      const allNutsNames = [];

      ev.map((item) => {
        allNutsNames.push(item.name)
      });
      result = `&${this.componentName}=` + allNutsNames.join(`&${this.componentName}=`);

      this.$emit(`selected-filter-${this.componentName}`, result);
    }
  },

};
</script>

<style>
</style>
