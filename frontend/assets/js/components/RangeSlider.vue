<template>
  <section data-title="Range + Custom Data" id="demo4">
    <div
      @mouseup="getIndex"
      class="range-slider"
    >
      <vue-slider 
        ref="slider4"
        v-bind="demo.demo4"
        v-model="demo.demo4.value"
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
    this.demo.demo4.value.push(this.dataList[0], this.dataList[len-1]);
  },

  data() {
    return {
      demo: {
        demo4: {
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
      }
    };
  },

  methods: {
    getValue() {
      let slider = this.$refs["slider4"];
      setTimeout(() => {
        this.$emit("selected-" + this.componentName, slider.getValue());
      });
    },
    getIndex() {
      let slider = this.$refs["slider4"];
      setTimeout(() => {
        console.log("getIndex ", slider.getIndex());
        this.$emit("selected-" + this.componentName, slider.getIndex());
      });
    }
  }
};
</script>

<style>
.range-slider {
  margin-left: 50px;
  margin-right: 50px;
}
</style>
