<template>
  <div class="pad-top40">

    <range-slider
      :dataList="dataset"
      :componentName="'range-collections'"
      v-on:selected-range-collections="handleSelectedRangeCollections"
      :clearAllFilters="clearAllFilters"
    ></range-slider>

  </div>
</template>

<script>
import RangeSlider from './RangeSlider';

export default {
  name: "CollectionYearsComponent",

  components: {
    'range-slider': RangeSlider,
  },

  props: {
    dataList: {},
    clearAllFilters: false,
  },

  data() {
    return {
      dataset: Object.keys(this.dataList),
      componentName: 'collections_range',
    };
  },

  methods: {

    /**
     * the array will start on position 0 with the first year (ex 1920)
     * the range-slider will send the values
     */
    handleSelectedRangeCollections(ev) {
      const searchQuery = `&data_collection_end_year__gte=${ev[0]}&data_collection_start_year__lte=${ev[1]}`;

      this.$emit("selected-filter-" + this.componentName, searchQuery);
    },
  },

};
</script>
<style>
.pad-top40{
  padding-top: 40px;
}
</style>
