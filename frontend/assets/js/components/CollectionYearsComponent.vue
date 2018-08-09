<template>
  <div class="pad-top40">
    <range-slider
      :dataList="dataset.labels" 
      :componentName="'range-collections'"
      v-on:selected-range-collections="handleSelectedRangeCollections"
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
    componentName: "",
    title: ""
  },

  data() {
    return {
      mySelectedList: [],
      myDataList: JSON.parse(JSON.stringify(this.dataList)),
      dataset: {},
    };
  },

  created() {
    this.dataset = this.makeRange();
  },

  methods: {
    /**
     * collection year comes as an object with a max and min
     * we need an array of all the years included between min and max and one with labels
     */
    makeRange() {
      let result = { data: new Array(this.myDataList.max - this.myDataList.min + 1).fill(0), labels: [] };
      for (let i = this.myDataList.min; i <= this.myDataList.max; i++) {
        result.labels.push(i);
      };

      return result;
    },

    /**
     * the array will start on position 0 with the first year (ex 1920)
     * the range-slider will send the indexes
     */
    handleSelectedRangeCollections(ev) {
      this.mySelectedList = [];

      if(ev.length > 0) {
        const firstElement = this.dataset.labels[ev[0]];
        const secondElement = this.dataset.labels[ev[1]];

        this.mySelectedList.push(firstElement);
        this.mySelectedList.push(secondElement);        
      }

      this.$emit("selected-" + this.componentName, this.mySelectedList);
    },
  }
};
</script>
<style>
.pad-top40{
  padding-top: 40px;
}
</style>
