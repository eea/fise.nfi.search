<template>
  <div id="multiselect">
    <multiselect 
      v-model="selected" 
      :options="myDataList"
      :multiple="true"
      track-by="name"
      :custom-label="customLabel"
    >
    </multiselect>
  </div>
</template>

<script>
import Multiselect from "vue-multiselect";

export default {
  name: "CountryComponent",

  components: {
    multiselect: Multiselect
  },

  props: {
    dataList: {},
    componentName: "",
    message: ""
  },

  data() {
    return {
      myDataList: JSON.parse(JSON.stringify(this.dataList)),
      selected: [],
    };
  },

  methods: {
    handleEmit() {
      setTimeout(() => {
        // will emit after the render updates the model
        this.$emit("selected-" + this.componentName, this.selected);
      });
    },

    customLabel(option) {
      return `${option.name}`;
    }
  },

  watch: {
    selected: function(val) {
      this.handleEmit();
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
