<template>
  <div id="topicCategoryCheckbox">

    <div class="nuts">
      <check-box-buttons
        :checkboxDataList="dataList"
        :componentName="componentName"
        :title="title"
        :clearAllFilters="clearAllFilters"
        @selected-topic_category="handleSelectedTopic" 
      ></check-box-buttons>
    </div>
    
  </div>
</template>

<script>
import CheckBoxButtons from "./CheckBoxButtons";

export default {
  name: "TopicCategoryComponent",

  components: {
    "check-box-buttons": CheckBoxButtons
  },

  props: {
    dataList: {},
    clearAllFilters: false,
  },

  data() {
    return {
      componentName: 'topic_category',
      title: 'Topic'
    };
  },

  methods: {
    handleSelectedTopic(ev) {
      let result = '';
      const allTopicsNames = [];

      ev.map((item) => {
        allTopicsNames.push(item.name)
      });
      result = `&${this.componentName}=` + allTopicsNames.join(`&${this.componentName}=`);

      this.$emit(`selected-filter-${this.componentName}`, result);
    }
  }

};
</script>

<style>
</style>
