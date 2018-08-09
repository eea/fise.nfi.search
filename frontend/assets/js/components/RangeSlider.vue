<template>
  <section data-title="Range + Custom Data" id="data">
    <div
      class="range-slider"
    >
      <vue-slider 
        ref="slider4"
        v-bind="data"
        v-model="data.value"
        @drag-end="getIndex"
      ></vue-slider>
    </div>
  </section>
</template>

<script>
import vueSlider from "vue-slider-component";

export default {
  name: "RangeSlider",

  props: {
    dataList: {},
    componentName: "",
    title: ""
  },

  components: {
    vueSlider
  },

  created() {
    const len = this.dataList.length;
    this.data.value.push(this.dataList[0], this.dataList[len-1]);
  },

  data() {
    return {
      data: {
        width: "100%",
        height: 4,
        dotSize: 14,
        interval: 3,
        disabled: false,
        show: true,
        tooltip: "always",
        piecewise: true,
        data: this.dataList.slice(),
        value: [],
      }
    };
  },

  methods: {
    getValue() {
      let slider = this.$refs["slider4"];
      return slider.getValue();
    },

    setValue(val) {
      let obj = this.data;
      obj.value = val;
    },

    getIndex() {
      let slider = this.$refs["slider4"];
      const indexes = slider.getIndex();
      let result = [];

      if((indexes[0] !== 0) || (indexes[1] !== this.dataList.length -1)) {
        result = indexes.slice();
      }

      this.$emit("selected-" + this.componentName, result);
    },

    setIndex(index) {
      let slider = this.$refs["slider4"];
      return slider.setIndex([0,10]);
    },

  }
};
</script>

<style>
.range-slider {
  margin-left: 50px;
  margin-right: 50px;
}
</style>
