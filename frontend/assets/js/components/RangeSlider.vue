<template>
  <section data-title="Range + Custom Data" id="data">
    <div
      class="range-slider"
    >
      <vue-slider 
        ref="slider4"
        v-bind="data"
        v-model="data.value"
        @drag-end="getValue"
      ></vue-slider>
    </div>
  </section>
</template>

<script>
import vueSlider from 'vue-slider-component';

export default {
  name: 'RangeSlider',

  props: {
    dataList: {},
    componentName: '',
    selected: '',
    title: '',
    clearAllFilters: false,
  },

  components: {
    vueSlider,
  },

  created() {
    const len = this.dataList.length;
    this.data.value.push(this.dataList[0], this.dataList[len - 1]);
  },

  data() {
    return {
      data: {
        width: '100%',
        height: 4,
        dotSize: 14,
        interval: 3,
        disabled: false,
        show: true,
        tooltip: 'always',
        piecewise: true,
        data: this.dataList.slice(),
        value: [],
      }
    };
  },

  methods: {
    getValue() {
      let slider = this.$refs['slider4'];
      const result = slider.getValue();

      this.$emit('selected-' + this.componentName, result);
    },

    setValue(val) {
      let obj = this.data;
      obj.value = val;
    },

    getIndex() {
      let slider = this.$refs['slider4'];
      const indexes = slider.getIndex();
      let result = [];

      if (indexes[0] !== 0 || indexes[1] !== this.dataList.length - 1) {
        result = indexes.slice();
      }

      this.$emit('selected-' + this.componentName, result);
    },

    resetIndex() {
      let slider = this.$refs['slider4'];
      return slider.setIndex([0, this.dataList.length-1]);
    }
  },

  watch: {
    /**
     * selected is an array containing the two years
     * if they are changed by the parent, this will update the slider position
     */
    selected: function updateFacetsCount(val) {
      this.setValue(this.selected);
    },
    clearAllFilters: function() {
      this.resetIndex();
    }
  }
};
</script>

<style lang="scss">
.range-slider {
  margin-left: 50px;
  margin-right: 50px;
}
.vue-slider-component .vue-slider-tooltip {
  display: block;
  font-size: 14px;
  white-space: nowrap;
  padding: 2px 5px;
  min-width: 20px;
  text-align: center;
  color: #fff;
  border-radius: 5px;
  // border: 1px solid var(--fise-orange);
  // background-color: var(--fise-orange);
  background: transparent;
  color: #333;
  border: none;
}
.vue-slider-component .vue-slider-process {
  position: absolute;
  border-radius: 15px;
  background-color: var(--fise-orange);
  transition: all 0s;
  z-index: 1;
}
.vue-slider-component .vue-slider-tooltip-top .vue-merged-tooltip .vue-slider-tooltip:before, .vue-slider-component .vue-slider-tooltip-wrap.vue-slider-tooltip-top .vue-slider-tooltip:before {
  display: none;
}
</style>
