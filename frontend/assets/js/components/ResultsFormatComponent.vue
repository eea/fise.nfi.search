<template>
  <div id="resultFormatCheckbox">
    <div class="nuts">
      <check-box-buttons
        :checkboxDataList="dataList"
        :componentName="componentName"
        :title="title"
        :clearAllFilters="clearAllFilters"
        @selected-resource_type="handleSelectedResultsFormat"
      ></check-box-buttons>
    </div>
  </div>
</template>

<script>
import CheckBoxButtons from "./CheckBoxButtons";

export default {
  name: "ResultsFormatComponent",

  components: {
    "check-box-buttons": CheckBoxButtons
  },

  props: {
    dataList: {},
    clearAllFilters: false,
  },

  data() {
    return {
      componentName: 'resource_type',
      title: 'Result format'
    };
  },

  methods: {
    handleSelectedResultsFormat(ev) {
      let result = '';
      const allResultFormatstsNames = [];

      ev.map((item) => {
        allResultFormatstsNames.push(item.name)
      });
      result = `&${this.componentName}=` + allResultFormatstsNames.join(`&${this.componentName}=`);

      this.$emit(`selected-filter-${this.componentName}`, result);
    }
  },

};
</script>

<style>
</style>
